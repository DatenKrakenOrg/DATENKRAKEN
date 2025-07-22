#include "ArduinoJson.hpp"
#include "ArduinoJson/Document/JsonDocument.hpp"
#include "ArduinoJson/Json/JsonSerializer.hpp"
#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "mqtt.h"
#include "wifi.h"
#include "noiseSensor.h"
#include "tempSensor.h"
#include "ntp.h"
#include "ArduinoJson.h"

const long interval = 100;
unsigned long previousMillis = 0;

static int count = 0;

float temperatures[30] = {0};
int temp_index = 0;

void setup()
{
    Serial.begin(115200);

    connectWifi();
    connectMqtt();
    setupTempSensor();
    // setupHumiditySensor();
    // setupCo2Sensor();
    setupNTP();

}


void loop()
{
    mqttClient.poll();
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        temperatures[temp_index++] = getTemp();
        Serial.println(temp_index);
        Serial.println(temperatures[temp_index-1]);
    }

    if(temp_index == 30) {
        JsonDocument doc;
        for(int i = 0; i < temp_index;i++){
            doc["value"][i] = temperatures[i];
        }
        Serial.println("sending...");
        doc["timestamp"] = getNTP();
        doc["sequence"] = count++;
        doc["meta"]["customfield"] = "value";

        char json_string[8000];

        serializeJsonPretty(doc, json_string);
        mqttClient.setTxPayloadSize(8000);
        mqttClient.beginMessage("dhbw/ai/si2023/6/temp/303");
        mqttClient.println(json_string);
        mqttClient.endMessage();

        temp_index = 0;
    }

    // sendMqttMessage("dhbw/ai/si2023/6/hum/303", "test");
    // sendMqttMessage("dhbw/ai/si2023/6/co2/303", "test");
    // sendMqttMessage("dhbw/ai/si2023/6/mic/303", "test");
}
