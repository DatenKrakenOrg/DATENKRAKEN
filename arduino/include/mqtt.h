#ifndef MQTT_H 
#define MQTT_H

#include "MqttClient.h"
extern MqttClient mqttClient;
void connectMqtt();
void sendMqttMessage(char topic[], char payload[]);

#endif
