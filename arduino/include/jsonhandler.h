#ifndef JSONHANDLER_H 
#define JSONHANDLER_H
#include <ArduinoJson.h>
extern StaticJsonDocument<512> doc;


#define JSONSIZE 8192

void buildAndSendJsonNoise(unsigned long timestamp, int value[], int count, int secondsIndex);
void buildAndSendJsonVoc(unsigned long timestamp, int value[], int vocIndex, int count, int secondsIndex);
void buildAndSendJsonTemp(unsigned long timestamp, float value, int count);
void buildAndSendJsonHum(unsigned long timestamp, int value, int count);

#endif
