"""Alerting utilities for the subscription script.

Provides simple e-mail based alerting with a cooldown to avoid spamming.

Environment Variables (all optional except recipients if you want mails):
  SMTP_HOST                      SMTP server host
  SMTP_PORT                      SMTP server port (default: 587)
  SMTP_USER                      SMTP username (if auth required)
  SMTP_PASS                      SMTP password (if auth required)
  ALERT_EMAIL_FROM               From address (default: value of SMTP_USER)
  ALERT_EMAIL_TO                 Comma separated list of recipients

Additional (used by main / watchdog):
  WATCHDOG_INACTIVITY_THRESHOLD_SECONDS   Threshold for inactivity (default: 10)

If mail configuration is missing, sending will be skipped with a warning once.
"""
from __future__ import annotations

import os
import time
import logging
import smtplib
import ssl
from email.message import EmailMessage
from threading import Lock
from typing import Optional

# Global cooldown registry { alert_key: last_send_unix_ts }
_last_alert_times: dict[str, float] = {}
_alert_lock = Lock()

# Read global cooldown (can be overridden per call by force=True)
try:
    ALERT_COOLDOWN_SECONDS = int(os.getenv("ALERT_COOLDOWN_SECONDS", "300"))
except ValueError:
    ALERT_COOLDOWN_SECONDS = 300

# Cache for missing config warning
_warned_missing_config = False

def _mail_config_valid() -> bool:
    global _warned_missing_config
    required_any = os.getenv("ALERT_EMAIL_TO")  # Only need recipients to attempt
    if not required_any:
        if not _warned_missing_config:
            logging.warning("Alerting disabled: ALERT_EMAIL_TO not set.")
            _warned_missing_config = True
        return False
    if not os.getenv("SMTP_HOST"):
        if not _warned_missing_config:
            logging.warning("Alerting disabled: SMTP_HOST not set.")
            _warned_missing_config = True
        return False
    return True

def _can_send(key: str, cooldown: int) -> bool:
    now = time.time()
    with _alert_lock:
        last = _last_alert_times.get(key, 0.0)
        if now - last >= cooldown:
            _last_alert_times[key] = now
            return True
        return False

def send_alert_email(subject: str, body: str, *, key: Optional[str] = None, force: bool = False, cooldown: Optional[int] = None) -> bool:
    """Send an alert email if configuration is present.

    Args:
        subject: Mail subject
        body: Mail body (plain text)
        key: Logical key used for cooldown scoping. If omitted subject is used.
        force: If True ignore cooldown.
        cooldown: Custom cooldown seconds (falls back to ALERT_COOLDOWN_SECONDS)

    Returns:
        bool: True if an email send was attempted (not necessarily succeeded), False if skipped early.
    """
    if not _mail_config_valid():
        return False

    if key is None:
        key = subject

    effective_cooldown = cooldown if cooldown is not None else ALERT_COOLDOWN_SECONDS

    if not force and not _can_send(key, effective_cooldown):
        return False

    host = os.getenv("SMTP_HOST")
    # Default wieder 587 (Submission); Port 465 => implicit SSL
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_addr = os.getenv("ALERT_EMAIL_FROM") or user or "alerts@example.invalid"
    to_raw = os.getenv("ALERT_EMAIL_TO", "")
    recipients = [addr.strip() for addr in to_raw.split(",") if addr.strip()]

    if not recipients:
        logging.warning("No recipients configured for alerting (ALERT_EMAIL_TO). Skipping send.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    try:
        context = ssl.create_default_context()

        if port == 465:
            # Implicit SSL
            logging.debug("Using implicit SSL (SMTP_SSL) for host=%s port=%s", host, port)
            with smtplib.SMTP_SSL(host, port, timeout=15, context=context) as server:
                if user and password:
                    try:
                        server.login(user, password)
                    except smtplib.SMTPException as e:
                        logging.error("SMTP login failed (SSL): %s", e)
                server.send_message(msg)
        else:
            # Plain + optional STARTTLS
            with smtplib.SMTP(host, port, timeout=15) as server:
                try:
                    server.ehlo()
                except Exception:
                    pass
                try:
                    server.starttls(context=context)
                    server.ehlo()
                    logging.debug("STARTTLS negotiated successfully with %s:%s", host, port)
                except smtplib.SMTPException as e:
                    logging.debug("STARTTLS not available (%s) – continuing without TLS", e)
                if user and password:
                    try:
                        server.login(user, password)
                    except smtplib.SMTPException as e:
                        logging.error("SMTP login failed: %s", e)
                server.send_message(msg)

        logging.info("Alert e-mail sent: %s", subject)
        return True
    except (smtplib.SMTPException, OSError) as e:
        logging.error("Failed to send alert email '%s' (smtp/os error): %s", subject, e)
        return False
    except Exception as e:
        logging.error("Failed to send alert email '%s' (unexpected): %s", subject, e)
        return False

def send_inactivity_alert(inactive_seconds: int) -> None:
    subject = "MQTT Inactivity Alert"
    body = (
        f"No MQTT messages received for {inactive_seconds} seconds. "
        f"Threshold exceeded. Please investigate broker, network, or publisher devices."
    )
    # Inaktivitäts-Alert soll nur EINMAL beim Eintritt gesendet werden -> force, eigener Key ohne Cooldown-Abbruch
    send_alert_email(subject, body, key="inactivity", force=True)


def send_inactivity_recovery_alert(recovered_after: int) -> None:
    subject = "MQTT Inactivity Recovery"
    body = (
        f"MQTT traffic resumed after {recovered_after} seconds of inactivity. "
        f"System considered recovered."
    )
    # Recovery ebenfalls einmalig beim Übergang senden
    send_alert_email(subject, body, key="inactivity_recovery", force=True)

def send_sequence_alert(topic: str, expected: int, received: int, last_good: int) -> None:
    subject = "MQTT Sequence Anomaly"
    body = (
        "Sequence anomaly detected on topic: {topic}\n"
        "Expected sequence: {expected}\n"
        "Received sequence: {received}\n"
        "Last good sequence: {last_good}\n"
        "Time: {ts}\n"
    ).format(
        topic=topic,
        expected=expected,
        received=received,
        last_good=last_good,
        ts=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    )
    key = f"seq:{topic}"  # Cooldown per topic
    send_alert_email(subject, body, key=key)
