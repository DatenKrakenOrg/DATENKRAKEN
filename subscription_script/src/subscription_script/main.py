"""Proposes the entry point of the subscription script. Configurable via env-var.

USERNAME - MQTT-Broker Username
PASSWORD - MQTT Broker Password
CLIENT_ID - MQTT Client ID => CANNOT BE DUPLICATED
BROKER_IP - MQTT Broker Hostname

DB_USERNAME - Database Username
DB_PASSWORD - Database Password
DB_HOST - Database Hostname
"""

from dotenv import load_dotenv
import os
import logging
from subscription_script.mqtt_util import (
    connect_mqtt,
    on_disconnect,
    on_message,
    get_last_message_timestamp,
)
from subscription_script.sql.engine import set_engine_session_factory
from subscription_script.alerting import (
    send_inactivity_alert,
    send_inactivity_recovery_alert,
)

import time
import threading

WATCHDOG_THRESHOLD_SECONDS = int(
    os.getenv("WATCHDOG_INACTIVITY_THRESHOLD_SECONDS", "300")
)

_watchdog_stop = threading.Event()
_inactivity_alert_active = False


def _watchdog_loop():
    """Background thread that monitors time since last received MQTT message.

    Sends an inactivity alert if threshold exceeded. Alert sending has its own cooldown
    inside the alerting module (key 'inactivity').
    """
    global _inactivity_alert_active
    while not _watchdog_stop.is_set():
        last_ts = get_last_message_timestamp()
        now = time.time()
        if last_ts is not None:
            inactive = now - last_ts
            if inactive >= WATCHDOG_THRESHOLD_SECONDS:
                if not _inactivity_alert_active:
                    send_inactivity_alert(int(inactive))
                    _inactivity_alert_active = True
            else:
                # Es kommen wieder Nachrichten nach einer Inaktivität
                if _inactivity_alert_active:
                    # Recovery nach der letzten Inaktivität
                    send_inactivity_recovery_alert(int(inactive))
                    _inactivity_alert_active = False
        # Sleep in short intervals so shutdown is responsive
        _watchdog_stop.wait(1.0)

load_dotenv()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


broker = os.getenv("BROKER_IP")
port = 1883
topics = [
    "dhbw/ai/si2023/6/co2/#",
    "dhbw/ai/si2023/6/mic/#",
    "dhbw/ai/si2023/6/hum/#",
    "dhbw/ai/si2023/6/temp/#",
]
client_id = os.getenv("CLIENT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


def main():
    """Initializes and runs the subscription script. Reconnects automatically by calling client.loop_forever()"""
    set_engine_session_factory()
    # Start watchdog thread
    t = threading.Thread(target=_watchdog_loop, name="mqtt-watchdog", daemon=True)
    t.start()
    client = connect_mqtt(client_id, username, password, broker, port)
    client.on_disconnect = on_disconnect
    for topic in topics:
        client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
