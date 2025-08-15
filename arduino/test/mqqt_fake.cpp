#include "mqtt_fake.h"

// Global container holding all "published" MQTT messages during tests
std::vector<PublishedMsg> PUBLISHED;

void sendMqttMessage(String topic, char payload[]) {
  // Push the message into the vector as plain std::string
  PUBLISHED.push_back(PublishedMsg{
      std::string(topic.c_str()),
      std::string(payload)
  });
}
