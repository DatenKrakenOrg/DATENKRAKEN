/*
 * These tests run in the native (host) environment and rely on the MQTT fake
 * to capture published messages instead of sending them to a broker.
 */

#include <unity.h>
#include <string>
#include "jsonhandler.h"
#include "mqtt_fake.h"
#include "arduino_secrets.h"   


static const std::string TOPIC_TEMP = std::string(TOPIC) + std::string("/temp/") + std::to_string(ROOM_ID);
static const std::string TOPIC_HUM  = std::string(TOPIC) + std::string("/hum/")  + std::to_string(ROOM_ID);
static const std::string TOPIC_MIC  = std::string(TOPIC) + std::string("/mic/")  + std::to_string(ROOM_ID);
static const std::string TOPIC_CO2  = std::string(TOPIC) + std::string("/co2/")  + std::to_string(ROOM_ID);

void setUp()   { PUBLISHED.clear(); }
void tearDown(){}

/** Humidity: exact topic + key fields present with correct values */
void test_humidity_message_exact_topic_and_fields() {
  unsigned long ts = 1723036800UL;
  int hum = 63;
  int seq = 5;

  buildAndSendJsonHum(ts, hum, seq);

  TEST_ASSERT_EQUAL_INT(1, (int)PUBLISHED.size());
  auto& m = PUBLISHED[0];

  TEST_ASSERT_EQUAL_STRING(TOPIC_HUM.c_str(), m.topic.c_str());
  TEST_ASSERT_TRUE(m.payload.find("\"timestamp\": 1723036800") != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"sequence\": 5")           != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"device_id\": 1")          != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"value\"")                 != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("63")                        != std::string::npos);
}

/** Temperature: exact topic + value appears in payload */
void test_temperature_message_exact_topic_and_value() {
  unsigned long ts = 1723036900UL;
  float temp = 23.5f;
  int seq = 6;

  buildAndSendJsonTemp(ts, temp, seq);

  TEST_ASSERT_EQUAL_INT(1, (int)PUBLISHED.size());
  auto& m = PUBLISHED[0];

  TEST_ASSERT_EQUAL_STRING(TOPIC_TEMP.c_str(), m.topic.c_str());
  TEST_ASSERT_TRUE(m.payload.find("\"timestamp\": 1723036900") != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"sequence\": 6")           != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"device_id\": 1")          != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"value\"")                 != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("23.5")                      != std::string::npos);
}

/** Noise: array values are included and core fields are present */
void test_noise_message_array_length_and_values_ok() {
  unsigned long ts = 1723037000UL;
  int seq = 7;
  int values[] = {10, 11, 12};
  int secondsIndex = 3;

  buildAndSendJsonNoise(ts, values, seq, secondsIndex);

  TEST_ASSERT_EQUAL_INT(1, (int)PUBLISHED.size());
  auto& m = PUBLISHED[0];

  TEST_ASSERT_EQUAL_STRING(TOPIC_MIC.c_str(), m.topic.c_str());
  TEST_ASSERT_TRUE(m.payload.find("\"timestamp\": 1723037000") != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"sequence\": 7")           != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"device_id\": 1")          != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("10")                        != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("11")                        != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("12")                        != std::string::npos);
}

/**
 * Noise (edge case): when secondsIndex == 0 the implementation does not create
 * a "value" field at all; verify it’s absent and core fields remain.
 */
void test_noise_message_zero_length_array_ok() {
  unsigned long ts = 1723037100UL;
  int seq = 8;
  int secondsIndex = 0;
  int dummy[1] = {42};

  buildAndSendJsonNoise(ts, dummy, seq, secondsIndex);

  TEST_ASSERT_EQUAL_INT(1, (int)PUBLISHED.size());
  auto& m = PUBLISHED[0];
  TEST_ASSERT_EQUAL_STRING(TOPIC_MIC.c_str(), m.topic.c_str());

  TEST_ASSERT_TRUE(m.payload.find("\"timestamp\": 1723037100") != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"sequence\": 8")           != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"device_id\": 1")          != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"value\"") == std::string::npos);
}

/** VOC/CO2: array values are included and core fields are present */
void test_voc_message_array_length_and_values_ok() {
  unsigned long ts = 1723037200UL;
  int seq = 9;
  int values[] = {400, 405};
  int vocIndex = 2;
  int secondsIndex = 30; // parameter is not used by implementation

  buildAndSendJsonVoc(ts, values, vocIndex, seq, secondsIndex);

  TEST_ASSERT_EQUAL_INT(1, (int)PUBLISHED.size());
  auto& m = PUBLISHED[0];

  TEST_ASSERT_EQUAL_STRING(TOPIC_CO2.c_str(), m.topic.c_str());
  TEST_ASSERT_TRUE(m.payload.find("\"timestamp\": 1723037200") != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"sequence\": 9")           != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("\"device_id\": 1")          != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("400")                       != std::string::npos);
  TEST_ASSERT_TRUE(m.payload.find("405")                       != std::string::npos);
}

int main(int, char**) {
  UNITY_BEGIN();
  RUN_TEST(test_humidity_message_exact_topic_and_fields);
  RUN_TEST(test_temperature_message_exact_topic_and_value);
  RUN_TEST(test_noise_message_array_length_and_values_ok);
  RUN_TEST(test_noise_message_zero_length_array_ok);
  RUN_TEST(test_voc_message_array_length_and_values_ok);
  return UNITY_END();
}
