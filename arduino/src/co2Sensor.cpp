#include "co2Sensor.h"
#include "Adafruit_SGP40.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include <DHT.h>
#include <DHT_U.h>

Adafruit_SGP40 sgp;

void setupCo2Sensor()
{
    if (!sgp.begin()) {
        Serial.println("SGP40 sensor not found :(");
        while (1)
            ;
    }

    Serial.print(sgp.serialnumber[0], HEX);
    Serial.print(sgp.serialnumber[1], HEX);
    Serial.println(sgp.serialnumber[2], HEX);
}

void getCo2(float t, float h)
{
    uint16_t sraw;
    int32_t voc_index;

    Serial.print("Temp: ");
    Serial.print(t);
    Serial.print(" Humidity: ");
    Serial.print(h);
    Serial.println();

    delay(1000);
    sraw = sgp.measureRaw(t, h);
    Serial.print("Raw measurement: ");
    Serial.println(sraw);

    voc_index = sgp.measureVocIndex(t, h);
    Serial.print("Voc Index: ");
    Serial.println(voc_index);
}
