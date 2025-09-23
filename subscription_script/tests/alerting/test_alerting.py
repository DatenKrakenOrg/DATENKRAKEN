import os
import time
import types
from unittest import mock

import subscription_script.alerting as alerting


def _set_env(**env):
    for k, v in env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = str(v)


def test_send_alert_email_cooldown(monkeypatch):
    _set_env(SMTP_HOST="smtp.local", SMTP_PORT="587", ALERT_EMAIL_TO="a@example.com", SMTP_USER="u", SMTP_PASS="p")

    # mock smtp
    smtp_mock = mock.MagicMock()
    smtp_ctx = mock.MagicMock()
    smtp_ctx.__enter__.return_value = smtp_mock
    monkeypatch.setattr(alerting.smtplib, "SMTP", mock.MagicMock(return_value=smtp_ctx))

    # ensure clean cooldown state
    alerting._last_alert_times.clear()

    sent1 = alerting.send_alert_email("Test Subject", "Body", key="k1", cooldown=60)
    sent2 = alerting.send_alert_email("Test Subject", "Body", key="k1", cooldown=60)

    assert sent1 is True
    assert sent2 is False  # suppressed by cooldown
    smtp_mock.send_message.assert_called_once()


def test_send_alert_email_force(monkeypatch):
    _set_env(SMTP_HOST="smtp.local", SMTP_PORT="587", ALERT_EMAIL_TO="a@example.com")

    smtp_mock = mock.MagicMock()
    smtp_ctx = mock.MagicMock()
    smtp_ctx.__enter__.return_value = smtp_mock
    monkeypatch.setattr(alerting.smtplib, "SMTP", mock.MagicMock(return_value=smtp_ctx))

    alerting._last_alert_times.clear()

    sent1 = alerting.send_alert_email("Force", "Body", key="force", cooldown=300)
    sent2 = alerting.send_alert_email("Force", "Body", key="force", cooldown=300, force=True)

    assert sent1 is True
    assert sent2 is True  # force bypasses cooldown
    assert smtp_mock.send_message.call_count == 2


def test_inactivity_and_recovery(monkeypatch):
    _set_env(SMTP_HOST="smtp.local", SMTP_PORT="587", ALERT_EMAIL_TO="ops@example.com")
    smtp_mock = mock.MagicMock()
    smtp_ctx = mock.MagicMock()
    smtp_ctx.__enter__.return_value = smtp_mock
    monkeypatch.setattr(alerting.smtplib, "SMTP", mock.MagicMock(return_value=smtp_ctx))

    alerting._last_alert_times.clear()

    alerting.send_inactivity_alert(120)
    alerting.send_inactivity_recovery_alert(120)

    # two different forced keys => 2 sends
    assert smtp_mock.send_message.call_count == 2


def test_sequence_alert(monkeypatch):
    _set_env(SMTP_HOST="smtp.local", SMTP_PORT="587", ALERT_EMAIL_TO="ops@example.com")
    smtp_mock = mock.MagicMock()
    smtp_ctx = mock.MagicMock()
    smtp_ctx.__enter__.return_value = smtp_mock
    monkeypatch.setattr(alerting.smtplib, "SMTP", mock.MagicMock(return_value=smtp_ctx))

    alerting._last_alert_times.clear()

    # first anomaly
    alerting.send_sequence_alert("topic/xyz", expected=11, received=15, last_good=10)
    # second should be suppressed because of cooldown
    alerting.send_sequence_alert("topic/xyz", expected=16, received=20, last_good=15)

    smtp_mock.send_message.assert_called_once()


def test_port_465_ssl(monkeypatch):
    _set_env(SMTP_HOST="smtp.local", SMTP_PORT="465", ALERT_EMAIL_TO="ops@example.com")
    smtp_ssl_mock = mock.MagicMock()
    smtp_ssl_ctx = mock.MagicMock()
    smtp_ssl_ctx.__enter__.return_value = smtp_ssl_mock
    monkeypatch.setattr(alerting.smtplib, "SMTP_SSL", mock.MagicMock(return_value=smtp_ssl_ctx))

    alerting._last_alert_times.clear()

    ok = alerting.send_alert_email("SSL Port", "Body", key="ssltest", force=True)
    assert ok is True
    smtp_ssl_mock.send_message.assert_called_once()
