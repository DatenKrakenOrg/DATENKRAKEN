#include "mqtt_fake.h"

std::vector<PublishedMsg> PUBLISHED;

void sendMqttMessage(String topic, char payload[]) {
  PUBLISHED.push_back(PublishedMsg{
      std::string(topic.c_str()),
      std::string(payload)
  });
}
