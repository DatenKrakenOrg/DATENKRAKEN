#include "jsonhandler.h"
#include "ArduinoJson.h"
#include "ArduinoJson.hpp"
#include "ArduinoJson/Document/JsonDocument.hpp"
#include "ArduinoJson/Json/JsonSerializer.hpp"
#include "arduino_secrets.h"
#include "mqtt.h"

JsonDocument doc;

String micTopic = String(TOPIC) + "/mic/" + String(ROOM_ID);
String co2Topic = String(TOPIC) + "/co2/" + String(ROOM_ID);
String tempTopic = String(TOPIC) + "/temp/" + String(ROOM_ID);
String humTopic = String(TOPIC) + "/hum/" + String(ROOM_ID);

void buildAndSendJsonNoise(unsigned long timestamp, int value[], int count, int secondsIndex)
{
    doc["timestamp"] = timestamp;
    for (int i = 0; i < secondsIndex; i++) {
        doc["value"][i] = value[i];
    }
    doc["sequence"] = count;
    doc["meta"]["device_id"] = ROOM_ID;
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage(micTopic, jsonString);
    doc.clear();
}

void buildAndSendJsonVoc(unsigned long timestamp, int value[], int vocIndex, int count, int secondsIndex)
{
    doc["timestamp"] = timestamp;
    for (int i = 0; i < vocIndex; i++) {
        doc["value"][i] = value[i];
    }
    doc["sequence"] = count;
    doc["meta"]["device_id"] = ROOM_ID;
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage(co2Topic, jsonString);
    doc.clear();
}

void buildAndSendJsonTemp(unsigned long timestamp, float value, int count)
{
    doc["timestamp"] = timestamp;
    doc["value"][0] = value;
    doc["sequence"] = count;
    doc["meta"]["device_id"] = ROOM_ID;
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage(tempTopic, jsonString);
    doc.clear();
}

void buildAndSendJsonHum(unsigned long timestamp, int value, int count)
{
    doc["timestamp"] = timestamp;
    doc["value"][0] = value;
    doc["sequence"] = count;
    doc["meta"]["device_id"] = ROOM_ID;
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage(humTopic, jsonString);
    doc.clear();
}
