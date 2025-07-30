#include "noiseSensor.h"
#include <Arduino.h>

const int noisePin = A0;

int getNoiseLevel()
{
    unsigned long startMillis = millis();
    unsigned int peakToPeak = 0;
    unsigned int sample;
    unsigned int sampleWindow = 50;

    unsigned int signalMax = 0;
    unsigned int signalMin = 1024;

    while (millis() - startMillis < sampleWindow) {
        sample = analogRead(noisePin);
        if (sample < 1024) {
            if (sample > signalMax) {
                signalMax = sample;
            } else if (sample < signalMin) {
                signalMin = sample;
            }
        }
    }
    peakToPeak = signalMax - signalMin;

    return peakToPeak;
}

void printNoiseLevel()
{
    Serial.print("Noise Level: ");
    Serial.print(getNoiseLevel());
    Serial.println();
}
