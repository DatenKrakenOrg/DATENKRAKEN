#ifndef MQTT_H
#define MQTT_H

#include "MqttClient.h"
extern MqttClient mqttClient;
void setupMqtt();
void connectMqtt();
void sendMqttMessage(String topic, char payload[]);

#endif
