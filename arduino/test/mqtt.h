#pragma once
class String;  // forward-declare reicht
void sendMqttMessage(String topic, char payload[]);
