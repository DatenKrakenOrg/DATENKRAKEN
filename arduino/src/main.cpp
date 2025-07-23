#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "mqtt.h"
#include "wifi.h"
#include "noiseSensor.h"
#include "tempSensor.h"
#include "ntp.h"
#include "ArduinoJson.h"
#include "ArduinoJson.hpp"                                                                                                                                                                   
#include "ArduinoJson/Document/JsonDocument.hpp"                                                                                                                                             
#include "ArduinoJson/Json/JsonSerializer.hpp" 

const long interval = 100;
unsigned long previousMillis = 0;


int sound[30] = {0};
int voc[7] = {0};

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
        Serial.println(sound[seconds_index-1]);
    }

    if (voc_idx % 5 == 0) {
        Serial.println(voc_idx);
        voc[voc_idx++] = getCo2Voc(getTemp(), getHumidity());
        Serial.print("Voc: ");
        Serial.println(voc[voc_idx-1]);
    }

    // Sound
    if(seconds_index == 30) {

        unsigned long unix_timestamp = getNTP();

        for(int i = 0; i < seconds_index;i++){
            doc["value"][i] = sound[i];
        }

        Serial.println("sending mic..");
        doc["timestamp"] = unix_timestamp;
        doc["sequence"] = count;
        doc["meta"]["customfield"] = "value";
        char json_string[8000];
        Serial.println("before serialize mic");
        serializeJsonPretty(doc, json_string);
        sendMqttMessage("dhbw/ai/si2023/6/mic/303", json_string);
        Serial.println("sended mic successfully");
        doc.clear();

        // voc 
        for(int i = 0; i < voc_idx;i++){
            doc["value"][i] = voc[i];
        }

        Serial.println("sending voc...");
        doc["timestamp"] = unix_timestamp;
        doc["sequence"] = count;
        doc["meta"]["customfield"] = "value";
        char voc_string[8000];
        serializeJsonPretty(doc, voc_string);
        sendMqttMessage("dhbw/ai/si2023/6/co2/303", voc_string);
        doc.clear();


        // Humid + Temp
        Serial.println("sending humidity...");
        doc["value"] = getHumidity();
        doc["timestamp"] = unix_timestamp;
        doc["sequence"] = count;
        char json_string2[8000];
        serializeJsonPretty(doc, json_string2);
        sendMqttMessage("dhbw/ai/si2023/6/hum/303", json_string2);
        doc.clear();

        Serial.println("sending temp...");
        doc["value"] = getTemp();
        doc["timestamp"] = unix_timestamp;
        doc["sequence"] = count;

        char json_string3[8000];
        serializeJsonPretty(doc, json_string3);
        sendMqttMessage("dhbw/ai/si2023/6/temp/303", json_string3);
        doc.clear();

        seconds_index = 0;
        voc_idx = 0;
        count++;
    }
}
