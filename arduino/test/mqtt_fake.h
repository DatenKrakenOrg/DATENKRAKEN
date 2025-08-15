#pragma once
#include <string>
#include <vector>

// Simple struct to hold MQTT topic + payload for verification in tests
struct PublishedMsg {
  std::string topic;
  std::string payload;
};

// Extern declaration so tests can access the collected messages
extern std::vector<PublishedMsg> PUBLISHED;

// Function signature must exactly match the production code
void sendMqttMessage(String topic, char payload[]);
