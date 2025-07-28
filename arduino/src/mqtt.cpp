#include "mqtt.h"
#include "arduino_secrets.h"
#include "jsonhandler.h"
#include "wifi.h"
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>

const char broker[] = BROKER;
int port = 1883;

MqttClient mqttClient(wifiClient);

void setupMqtt()
{
    connectMqtt();
    mqttClient.setTxPayloadSize(JSONSIZE);
}

void connectMqtt()
{
    mqttClient.setUsernamePassword(MQTT_USER, MQTT_PASS);

    Serial.print("Attempting to connect to the MQTT broker: ");
    Serial.println(broker);

    while (!mqttClient.connect(broker, port)) {
        Serial.print("MQTT connection failed! Error code = ");
        Serial.println(mqttClient.connectError());
        Serial.println("Trying again in 1 second");
        delay(1000);
    }

    Serial.println("You're connected to the MQTT broker!");
    Serial.println();
}

void sendMqttMessage(char topic[], char payload[])
{
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.end();
        connectWifi();
    }
    if (!mqttClient.connected()) {
        mqttClient.stop();
        connectMqtt();
    }
    mqttClient.beginMessage(topic);
    mqttClient.println(payload);
    mqttClient.endMessage();
}
