#include "sensors.h"
#include "Adafruit_SGP40.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 13 // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 // DHT 11

Adafruit_ADT7410 tempsensor;
Adafruit_SGP40 sgp;
DHT_Unified dht(DHTPIN, DHTTYPE);
const int noisePin = A0;

uint32_t delayMS;

void setupTempSensor()
{
    tempsensor = Adafruit_ADT7410();

    if (!tempsensor.begin()) {
        Serial.println("Couldn't find ADT7410!");
        while (1)
            ;
    }

    // sensor takes 250 ms to get first readings
    delay(250);

    tempsensor.setResolution(ADT7410_16BIT);
}

void setupHumiditySensor()
{
    // Initialize device.
    dht.begin();
    Serial.println(F("DHTxx Unified Sensor Example"));
    // Print temperature sensor details.
    sensor_t sensor;
    dht.humidity().getSensor(&sensor);
    Serial.println(F("Humidity Sensor"));
    Serial.print(F("Sensor Type: "));
    Serial.println(sensor.name);
    Serial.print(F("Driver Ver:  "));
    Serial.println(sensor.version);
    Serial.print(F("Unique ID:   "));
    Serial.println(sensor.sensor_id);
    Serial.print(F("Max Value:   "));
    Serial.print(sensor.max_value);
    Serial.println(F("%"));
    Serial.print(F("Min Value:   "));
    Serial.print(sensor.min_value);
    Serial.println(F("%"));
    Serial.print(F("Resolution:  "));
    Serial.print(sensor.resolution);
    Serial.println(F("%"));
    Serial.println(F("------------------------------------"));
    // delayMS = sensor.min_delay / 1000;
}

void setupCo2Sensor()
{
    if (!sgp.begin()) {
        Serial.println("SGP40 sensor not found :(");
        while (1)
            ;
    }

    Serial.print(sgp.serialnumber[0], HEX);
    Serial.print(sgp.serialnumber[1], HEX);
    Serial.println(sgp.serialnumber[2], HEX);
}

float getTemp()
{
    float c = tempsensor.readTempC();
    return c;
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

void getCo2(float t, float h)
{
    uint16_t sraw;
    int32_t voc_index;

    Serial.print("Temp: ");
    Serial.print(t);
    Serial.print(" Humidity: ");
    Serial.print(h);
    Serial.println();

    delay(1000);
    sraw = sgp.measureRaw(t, h);
    Serial.print("Raw measurement: ");
    Serial.println(sraw);

    voc_index = sgp.measureVocIndex(t, h);
    Serial.print("Voc Index: ");
    Serial.println(voc_index);
}

void getNoiseLevel()
{
    int micValue = analogRead(noisePin);
    Serial.print("Noise Level: ");
    Serial.println(micValue);
}
