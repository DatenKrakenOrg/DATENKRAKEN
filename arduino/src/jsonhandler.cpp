#include "jsonhandler.h"
#include "ArduinoJson.h"
#include "ArduinoJson.hpp"
#include "ArduinoJson/Document/JsonDocument.hpp"
#include "ArduinoJson/Json/JsonSerializer.hpp"
#include "mqtt.h"

JsonDocument doc;

void buildAndSendJsonNoise(unsigned long timestamp, int value[], int count, int secondsIndex)
{
    doc["timestamp"] = timestamp;
    for (int i = 0; i < secondsIndex; i++) {
        doc["value"][i] = value[i];
    }
    doc["sequence"] = count;
    doc["meta"] = "null";
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage("dhbw/ai/si2023/6/mic/303", jsonString);
    doc.clear();
}

void buildAndSendJsonVoc(unsigned long timestamp, int value[], int vocIndex, int count, int secondsIndex)
{
    doc["timestamp"] = timestamp;
    for (int i = 0; i < vocIndex; i++) {
        doc["value"][i] = value[i];
    }
    doc["sequence"] = count;
    doc["meta"] = "null";
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage("dhbw/ai/si2023/6/co2/303", jsonString);
    doc.clear();
}

void buildAndSendJsonTemp(unsigned long timestamp, float value, int count)
{
    doc["timestamp"] = timestamp;
    doc["value"] = value;
    doc["sequence"] = count;
    doc["meta"] = "null";
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage("dhbw/ai/si2023/6/temp/303", jsonString);
    doc.clear();
}

void buildAndSendJsonHum(unsigned long timestamp, int value, int count)
{
    doc["timestamp"] = timestamp;
    doc["value"] = value;
    doc["sequence"] = count;
    doc["meta"] = "null";
    char jsonString[JSONSIZE];
    serializeJsonPretty(doc, jsonString);
    sendMqttMessage("dhbw/ai/si2023/6/hum/303", jsonString);
    doc.clear();
}
