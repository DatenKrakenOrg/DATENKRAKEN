import logging
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from typing import List, Union
from subscription_script.sql.orm import Temperature, Humidity, Voc, Noise
from subscription_script.sql.engine import insert_into_db
from paho.mqtt import client as mqtt_client

_temp_seq = 0
_hum_seq = 0
_voc_seq = 0
_noise_seq = 0


def connect_mqtt(
    client_id: str, username: str, password: str, broker: str, port: int
) -> mqtt_client.Client:
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        clean_session=False,
    )

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_disconnect(client, userdata, rc) -> None:
    logging.info("Disconnected with result code: %s. Attempting reconnection..", rc)


def on_message(client, userdata, msg) -> None:
    global _temp_seq, _hum_seq, _voc_seq, _noise_seq

    payload = None
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        logging.critical(f"Error during deserialization of {msg.payload.decode()} from {msg.topic} topic")

    try:
        values: list = []
        if type(payload["value"]) is list:
            for value in payload["value"]:
                values.append(value)
        elif type(payload["value"]) is int or type(payload["value"]) is float:
            values.append(payload["value"])
        else:
            raise RuntimeError(f"Datatype mismatch of value attribute within data collection. Type received: {type(payload["value"])}")

        orm_objs: List[Union[Temperature, Humidity, Voc, Noise]] = []

        if 'temp' in msg.topic:
            if _temp_seq + 1 != payload["sequence"]:
                logging.warn(f"Payload sequence number interrupted at: {payload["sequence"]}. Expected: {_temp_seq}")
            
            _temp_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Temperature(
                        time=datetime.fromtimestamp(payload["timestamp"], ZoneInfo("Europe/Berlin")),
                        deleted_at=None,
                        arduino_id = str(payload["meta"]["device_id"]),
                        temperature=value
                    )
                )
        elif 'hum' in msg.topic:
            if _hum_seq + 1 != payload["sequence"]:
                logging.warn(f"Payload sequence number interrupted at: {payload["sequence"]}. Expected: {_hum_seq}")
            
            _hum_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Humidity(
                        time=datetime.fromtimestamp(payload["timestamp"], ZoneInfo("Europe/Berlin")),
                        deleted_at=None,
                        arduino_id = str(payload["meta"]["device_id"]),
                        humidity=value
                    )
                )
        elif 'co2' in msg.topic:
            if _voc_seq + 1 != payload["sequence"]:
                logging.warn(f"Payload sequence number interrupted at: {payload["sequence"]}. Expected: {_voc_seq}")
            
            _voc_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Voc(
                        time=datetime.fromtimestamp(payload["timestamp"], ZoneInfo("Europe/Berlin")),
                        deleted_at=None,
                        arduino_id = str(payload["meta"]["device_id"]),
                        voc=value
                    )
                )
        elif 'mic' in msg.topic:
            if _noise_seq + 1 != payload["sequence"]:
                logging.warn(f"Payload sequence number interrupted at: {payload["sequence"]}. Expected: {_noise_seq}")
            
            _noise_seq = payload["sequence"]

            for value in values:
                orm_objs.append(
                    Noise(
                        time=datetime.fromtimestamp(payload["timestamp"], ZoneInfo("Europe/Berlin")),
                        deleted_at=None,
                        arduino_id = str(payload["meta"]["device_id"]),
                        noise=value
                    )
                )

        if len(orm_objs) > 0:
            insert_into_db(orm_objs)
    except Exception as e:
        logging.critical(f"Error during insertion of datapoint from {msg.topic} topic. Exception: {e}")