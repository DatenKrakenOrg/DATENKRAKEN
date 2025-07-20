#ifndef CO2SENSOR_H
#define CO2SENSOR_H

void setupCo2Sensor();
int getCo2Voc(float t, float h);
int getCo2Raw(float t, float h);
void printCo2(float t, float h);

#endif
