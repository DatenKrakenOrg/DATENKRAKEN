"""Includes all paho_mqtt callback functions that the subscription script client calls on events such as on_disconnect, etc."""

import logging
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from typing import List, Union
from subscription_script.sql.orm import Temperature, Humidity, Voc, Noise
from subscription_script.sql.engine import insert_into_db
from paho.mqtt import client as mqtt_client
from .alerting import send_sequence_alert

# Track last message arrival (epoch seconds UTC)
_last_message_ts: float | None = None

_temp_seq = 0
_hum_seq = 0
_voc_seq = 0
_noise_seq = 0


def connect_mqtt(
    client_id: str, username: str, password: str, broker: str, port: int
) -> mqtt_client.Client:
    """Used to initialize the client that subscribes the mqtt broker.

    Args:
        client_id (str): Used as identifier for the subscription on the broker side.
        username (str): Used to authenticate towards the broker
        password (str): Used to authenticate towards the broker
        broker (str): Broker Hostname
        port (int): Broker Port

    Returns:
        mqtt_client.Client: Returns a mqtt_client used to subscribe the topics in main.
    """

    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.critical("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        clean_session=False,
    )

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_disconnect(client, userdata, flags, rc, properties) -> None:
    """Defines a callback function that is called on disconnect. Args are given by paho mqtt.

    A log is generated whenever a client disconnects.
    """
    logging.info("Disconnected with result code: %s. Attempting reconnection..", rc)


def on_message(client, userdata, msg) -> None:
    """
    Defines a callback function that is called whenever a mqtt message arrives from a topic. Args are given by paho-mqtt.

    The function validates whether the sequence number interrupts (negative case is logged) and logs a deserialization error (whenever a message is corrupt). Other than that it persists alle datapoints into timescaledb.
    Raises:
        RuntimeError: Raised whenever the message value field doesn't hold the topic specification, since this would show a severe design misunderstand that cannot be determistically fixed => Therefore persistence is possible!
    """
    global _temp_seq, _hum_seq, _voc_seq, _noise_seq, _last_message_ts

    # Update last message timestamp early (even if JSON invalid we still observed broker traffic)
    _last_message_ts = datetime.now(tz=timezone.utc).timestamp()

    payload = None
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        logging.critical(
            f"Error during deserialization of {msg.payload.decode()} from {msg.topic} topic"
        )

    try:
        values: list = []
        if type(payload["value"]) is list:
            for value in payload["value"]:
                values.append(value)
        elif type(payload["value"]) is int or type(payload["value"]) is float:
            values.append(payload["value"])
        else:
            raise RuntimeError(
                f"Datatype mismatch of value attribute within data collection. Type received: {type(payload['value'])}"
            )

        orm_objs: List[Union[Temperature, Humidity, Voc, Noise]] = []

        if "temp" in msg.topic:
            if _temp_seq == 0:
                # Baseline setzen – erste Sequenz ohne Prüfung akzeptieren
                _temp_seq = payload["sequence"]
                logging.info(
                    "Initial temperature sequence baseline set to %s", _temp_seq
                )
            else:
                expected = _temp_seq + 1
                if expected != payload["sequence"]:
                    logging.warning(
                        "Payload sequence number interrupted at: %s. Expected: %s (last good: %s)",
                        payload["sequence"], expected, _temp_seq,
                    )
                    send_sequence_alert(
                        msg.topic,
                        expected=expected,
                        received=payload["sequence"],
                        last_good=_temp_seq,
                    )
                _temp_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Temperature(
                        time=datetime.fromtimestamp(
                            payload["timestamp"], ZoneInfo("Europe/Berlin")
                        ),
                        deleted_at=None,
                        arduino_id=str(payload["meta"]["device_id"]),
                        temperature=value,
                    )
                )
        elif "hum" in msg.topic:
            if _hum_seq == 0:
                _hum_seq = payload["sequence"]
                logging.info(
                    "Initial humidity sequence baseline set to %s", _hum_seq
                )
            else:
                expected = _hum_seq + 1
                if expected != payload["sequence"]:
                    logging.warning(
                        "Payload sequence number interrupted at: %s. Expected: %s (last good: %s)",
                        payload["sequence"], expected, _hum_seq,
                    )
                    send_sequence_alert(
                        msg.topic,
                        expected=expected,
                        received=payload["sequence"],
                        last_good=_hum_seq,
                    )
                _hum_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Humidity(
                        time=datetime.fromtimestamp(
                            payload["timestamp"], ZoneInfo("Europe/Berlin")
                        ),
                        deleted_at=None,
                        arduino_id=str(payload["meta"]["device_id"]),
                        humidity=value,
                    )
                )
        elif "co2" in msg.topic:
            if _voc_seq == 0:
                _voc_seq = payload["sequence"]
                logging.info(
                    "Initial co2/voc sequence baseline set to %s", _voc_seq
                )
            else:
                expected = _voc_seq + 1
                if expected != payload["sequence"]:
                    logging.warning(
                        "Payload sequence number interrupted at: %s. Expected: %s (last good: %s)",
                        payload["sequence"], expected, _voc_seq,
                    )
                    send_sequence_alert(
                        msg.topic,
                        expected=expected,
                        received=payload["sequence"],
                        last_good=_voc_seq,
                    )
                _voc_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Voc(
                        time=datetime.fromtimestamp(
                            payload["timestamp"], ZoneInfo("Europe/Berlin")
                        ),
                        deleted_at=None,
                        arduino_id=str(payload["meta"]["device_id"]),
                        voc=value,
                    )
                )
        elif "mic" in msg.topic:
            if _noise_seq == 0:
                _noise_seq = payload["sequence"]
                logging.info(
                    "Initial noise sequence baseline set to %s", _noise_seq
                )
            else:
                expected = _noise_seq + 1
                if expected != payload["sequence"]:
                    logging.warning(
                        "Payload sequence number interrupted at: %s. Expected: %s (last good: %s)",
                        payload["sequence"], expected, _noise_seq,
                    )
                    send_sequence_alert(
                        msg.topic,
                        expected=expected,
                        received=payload["sequence"],
                        last_good=_noise_seq,
                    )
                _noise_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Noise(
                        time=datetime.fromtimestamp(
                            payload["timestamp"], ZoneInfo("Europe/Berlin")
                        ),
                        deleted_at=None,
                        arduino_id=str(payload["meta"]["device_id"]),
                        noise=value,
                    )
                )

        if len(orm_objs) > 0:
            insert_into_db(orm_objs)
    except Exception as e:
        logging.critical(
            f"Error during insertion of datapoint from {msg.topic} topic. Exception: {e}"
        )


def get_last_message_timestamp() -> float | None:
    """Returns the UNIX timestamp (UTC) of the last received MQTT message or None if none yet."""
    return _last_message_ts
