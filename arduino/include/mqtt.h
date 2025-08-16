#ifndef MQTT_H
#define MQTT_H

#ifdef UNIT_TEST

// ---- Test-Build (native) ----
#include "mqtt_fake.h"   

#else

// ---- Arduino-Build ----
#include <Arduino.h>
#include <MqttClient.h>  

extern MqttClient mqttClient;

void setupMqtt();
void connectMqtt();
void sendMqttMessage(String topic, char payload[]);

#endif 

#endif 
