#pragma once
// Minimale Deklaration für den Test. Kein Arduino/kein MqttClient nötig.
class String;  // forward-declare reicht
void sendMqttMessage(String topic, char payload[]);
