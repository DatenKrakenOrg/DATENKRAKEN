#ifndef SENSOR_H
#define SENSOR_H
#include "Adafruit_ADT7410.h"
#include <Wire.h>

extern Adafruit_ADT7410 tempsensor;

void setupTempSensor();
void setupHumiditySensor();
void setupCo2Sensor();
float getTemp();
float getHumidity();
void getCo2(float t, float h);
void getNoiseLevel();
#endif
