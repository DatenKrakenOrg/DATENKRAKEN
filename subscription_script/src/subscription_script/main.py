from dotenv import load_dotenv
import os
import logging
from subscription_script.mqtt_util import connect_mqtt, on_disconnect, on_message
from subscription_script.sql.engine import set_engine_session_factory

load_dotenv()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


broker = "aicon.dhbw-heidenheim.de"
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
    set_engine_session_factory()
    client = connect_mqtt(client_id, username, password, broker, port)
    client.on_disconnect = on_disconnect
    for topic in topics:
        client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
