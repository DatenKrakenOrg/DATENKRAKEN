#include "noiseSensor.h"
#include <Arduino.h>

const int noisePin = A0;

void getNoiseLevel()
{
    int micValue = analogRead(noisePin);
    Serial.print("Noise Level: ");
    Serial.println(micValue);
}
