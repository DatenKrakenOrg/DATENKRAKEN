#include "noiseSensor.h"
#include <Arduino.h>

const int noisePin = A0;

int getNoiseLevel()
{
    int micValue = analogRead(noisePin);
    return micValue;
}

void printNoiseLevel()
{
    Serial.print("Noise Level: ");
    Serial.print(getNoiseLevel());
    Serial.println();
}
