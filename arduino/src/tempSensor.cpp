#include "tempSensor.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>

Adafruit_ADT7410 tempsensor;

void setupTempSensor()
{
    tempsensor = Adafruit_ADT7410();

    if (!tempsensor.begin()) {
        Serial.println("Couldn't find ADT7410!");
        while (1)
            ;
    }

    // sensor takes 250 ms to get first readings
    delay(250);

    tempsensor.setResolution(ADT7410_16BIT);
}

float getTemp()
{
    float c = tempsensor.readTempC();
    return c;
}
