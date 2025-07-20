#include "tempSensor.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>

Adafruit_ADT7410 tempsensor;

void setupTempSensor()
{
    tempsensor = Adafruit_ADT7410();

    while (!tempsensor.begin()) {
        Serial.println("Couldn't find ADT7410!");
        Serial.println("Trying again in 1 second");
        delay(1000);
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

void printTemp()
{
    Serial.print("Temp: ");
    Serial.print(getTemp());
    Serial.println();
}
