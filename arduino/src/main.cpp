#include "arduino_secrets.h"
#include "co2Sensor.h"
#include "humiditySensor.h"
#include "jsonhandler.h"
#include "mqtt.h"
#include "noiseSensor.h"
#include "ntp.h"
#include "tempSensor.h"
#include "wifi.h"

const long interval = 1000;
unsigned long previousMillis = 0;

int noise[30] = { 0 };
int voc[7] = { 0 };

int vocIndex = 0;
int secondsIndex = 0;
static int count = 0;

void setup()
{
    Serial.begin(115200);

    setupTempSensor();
    setupHumiditySensor();
    setupCo2Sensor();
    connectWifi();
    setupNTP();
    setupMqtt();
}

void loop()
{
    mqttClient.poll();
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        noise[secondsIndex++] = getNoiseLevel();

        if (secondsIndex % 5 == 0) {
            voc[vocIndex++] = getCo2Voc(getTemp(), getHumidity());
        }

        if (secondsIndex == 30) {
            Serial.print("Publishing data ");
            Serial.println(count);
            unsigned long unixTimestamp = getNTP();

            buildAndSendJsonNoise(unixTimestamp, noise, count, secondsIndex);
            buildAndSendJsonVoc(unixTimestamp, voc, vocIndex, count, secondsIndex);
            buildAndSendJsonHum(unixTimestamp, getHumidity(), count);
            buildAndSendJsonTemp(unixTimestamp, getTemp(), count);

            secondsIndex = 0;
            vocIndex = 0;
            count++;
        }
    }
}
