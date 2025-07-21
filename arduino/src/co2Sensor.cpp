#include "co2Sensor.h"
#include "Adafruit_SGP40.h"
#include <Arduino.h>

Adafruit_SGP40 sgp;

void setupCo2Sensor()
{
    while (!sgp.begin()) {
        Serial.println("SGP40 sensor not found");
        Serial.println("Trying again in 1 second");
        delay(1000);
    }

    Serial.print(sgp.serialnumber[0], HEX);
    Serial.print(sgp.serialnumber[1], HEX);
    Serial.println(sgp.serialnumber[2], HEX);
}

int getCo2Voc(float t, float h)
{
    int32_t voc_index;
    voc_index = sgp.measureVocIndex(t, h);
    return voc_index;
}

int getCo2Raw(float t, float h)
{
    uint16_t sraw;
    sraw = sgp.measureRaw(t, h);
    return sraw;
}

void printCo2(float t, float h)
{
    Serial.print("Raw measurement: ");
    Serial.print(getCo2Raw(t, h));
    Serial.println();

    Serial.print("Voc Index: ");
    Serial.print(getCo2Voc(t, h));
    Serial.println();
}
