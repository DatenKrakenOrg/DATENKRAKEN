#pragma once
#include <string>
#include <vector>

struct PublishedMsg {
  std::string topic;
  std::string payload;
};

extern std::vector<PublishedMsg> PUBLISHED;

void sendMqttMessage(String topic, char payload[]);
