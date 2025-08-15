#pragma once
#ifdef UNIT_TEST

// Minimal declaration used by jsonhandler.cpp during native tests.
// We only need the function signature; definition is in test/mqtt_fake.cpp.
class String;  // forward declaration
void sendMqttMessage(String topic, char payload[]);

#else

// Forward to the real project header in include/mqtt.h for non-test builds.
#include_next "mqtt.h"

#endif
