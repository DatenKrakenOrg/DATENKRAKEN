#include "ArduinoJson.h"
#include "ArduinoJson.hpp"
#include "ArduinoJson/Document/JsonDocument.hpp"
#include "ArduinoJson/Json/JsonSerializer.hpp"
#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "mqtt.h"
#include "noiseSensor.h"
#include "ntp.h"
#include "tempSensor.h"
#include "wifi.h"

const long interval = 1000;
unsigned long previousMillis = 0;

int sound[30] = { 0 };
int voc[7] = { 0 };

int voc_idx = 0;
int seconds_index = 0;
static int count = 0;

void setup()
{
    Serial.begin(115200);

    connectWifi();
    connectMqtt();
    setupTempSensor();
    setupHumiditySensor();
    setupCo2Sensor();
    setupNTP();
    mqttClient.setTxPayloadSize(8001);
}

JsonDocument doc;

void loop()
{
    mqttClient.poll();
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        sound[seconds_index++] = getNoiseLevel();
    }

    if (seconds_index % 5 == 0) {
        voc[voc_idx++] = getCo2Voc(getTemp(), getHumidity());
    }

    // Sound
    if (seconds_index == 30) {
        unsigned long unix_timestamp = getNTP();

        Serial.println("sending mic..");
        doc["timestamp"] = unix_timestamp;
        for (int i = 0; i < seconds_index; i++) {
            doc["value"][i] = sound[i];
        }
        doc["sequence"] = count;
        doc["meta"] = "null";
        char json_string[8192];
        Serial.println("before serialize mic");
        serializeJsonPretty(doc, json_string);
        sendMqttMessage("dhbw/ai/si2023/6/mic/303", json_string);
        Serial.println("sended mic successfully");
        doc.clear();

        // voc
        Serial.println("sending voc...");
        doc["timestamp"] = unix_timestamp;
        for (int i = 0; i < voc_idx; i++) {
            doc["value"][i] = voc[i];
        }
        doc["sequence"] = count;
        doc["meta"] = "null";
        char vocString[4096];
        serializeJsonPretty(doc, vocString);
        sendMqttMessage("dhbw/ai/si2023/6/co2/303", vocString);
        doc.clear();

        // Humid
        Serial.println("sending humidity...");
        doc["timestamp"] = unix_timestamp;
        doc["value"] = getHumidity();
        doc["sequence"] = count;
        doc["meta"] = "null";
        char humString[1024];
        serializeJsonPretty(doc, humString);
        sendMqttMessage("dhbw/ai/si2023/6/hum/303", humString);
        doc.clear();

        // Temp
        Serial.println("sending temp...");
        doc["timestamp"] = unix_timestamp;
        doc["value"] = getTemp();
        doc["sequence"] = count;
        doc["meta"] = "null";

        char tempString[1024];
        serializeJsonPretty(doc, tempString);
        sendMqttMessage("dhbw/ai/si2023/6/temp/303", tempString);
        doc.clear();

        seconds_index = 0;
        voc_idx = 0;
        count++;
    }
}
