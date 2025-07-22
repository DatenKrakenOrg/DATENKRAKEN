#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "mqtt.h"
#include "noiseSensor.h"
#include "tempSensor.h"
#include "wifi.h"
#include "ntp.h"

const long interval = 2000;
unsigned long previousMillis = 0;

int count = 0;

void setup()
{
    Serial.begin(115200);
    while (!Serial) {
        ;
    }
    connectWifi();
    connectMqtt();

    setupTempSensor();
    setupHumiditySensor();
    setupCo2Sensor();
    setupNTP();
}

void loop()
{
    mqttClient.poll();
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        sendMqttMessage("dhbw/ai/si2023/6/temp/303", "test");
        sendMqttMessage("dhbw/ai/si2023/6/hum/303", "test");
        sendMqttMessage("dhbw/ai/si2023/6/co2/303", "test");
        sendMqttMessage("dhbw/ai/si2023/6/mic/303", "test");

        Serial.println();

        count++;
    }
}
