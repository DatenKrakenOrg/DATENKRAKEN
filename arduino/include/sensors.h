#ifndef SENSOR_H
#define SENSOR_H
#include "Adafruit_ADT7410.h"
#include <Wire.h>

extern Adafruit_ADT7410 tempsensor;

void setup_temp_sensor();
void setup_humidity_sensor();
float get_temp_from_sensor();
float get_humidity();
void loop_co2_sensor(float t, float h);
void setup_co2_sensor();
void get_noise_level();
#endif
