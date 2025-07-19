#ifndef TEMPSENSOR_H
#define TEMPSENSOR_H
#include "Adafruit_ADT7410.h"

extern Adafruit_ADT7410 tempsensor;

void setupTempSensor();
float getTemp();
#endif
