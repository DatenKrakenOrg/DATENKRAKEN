#include "humiditySensor.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 13 // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 // DHT 11

DHT_Unified dht(DHTPIN, DHTTYPE);

void setupHumiditySensor()
{
    // Initialize device.
    dht.begin();
    sensor_t sensor;
    dht.humidity().getSensor(&sensor);
}

float getHumidity()
{
    float humidity = 0.0f;
    sensors_event_t event;
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
        Serial.println(F("Error reading humidity!"));
    } else {
        humidity = event.relative_humidity;
    }
    return humidity;
}

void printHumidity()
{
    Serial.print("Humidity: ");
    Serial.print(getHumidity());
    Serial.println();
}
