#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "noiseSensor.h"
#include "tempSensor.h"
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>

#define MAX_WIFI_CON_TRIES 3

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = BROKER;
int port = 1883;
const char topic[] = TOPIC;

const long interval = 2000;
unsigned long previousMillis = 0;

int count = 0;

void connectWifi()
{
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);

    int connection_tries = 0;

    while (WiFi.begin(ssid, pass) != WL_CONNECTED && connection_tries < MAX_WIFI_CON_TRIES) {
        Serial.print(".");
        delay(5000);
        connection_tries++;
    }

    if (connection_tries >= MAX_WIFI_CON_TRIES){
        Serial.println("Connection to WiFi failed");
    }
    else {
        Serial.println("You're connected to the network");
    }
    Serial.println();

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

void setup()
{
    Serial.begin(115200);
    while (!Serial) {
        ;
    }
    // connectWifi();
    // connectMqtt();

    setupTempSensor();
    setupHumiditySensor();
    setupCo2Sensor();
}

void loop()
{
    mqttClient.poll();
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        printTemp();
        printHumidity();
        printCo2(getTemp(), getHumidity());
        printNoiseLevel();

        // // send message, the Print interface can be used to set the message contents
        // mqttClient.beginMessage(topic);
        // mqttClient.print("temp: ");
        // mqttClient.println(get_temp_from_sensor());
        // mqttClient.print("humidity: ");
        // mqttClient.println(get_humidity());
        // mqttClient.endMessage();

        Serial.println();

        count++;
    }
}
