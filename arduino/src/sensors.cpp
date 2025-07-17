#include "sensors.h"
#include <Adafruit_Sensor.h>
#include <Arduino.h>
#include <DHT.h>
#include <DHT_U.h>

Adafruit_ADT7410 tempsensor;

void setup_temp_sensor()
{
    tempsensor = Adafruit_ADT7410();
    Serial.println("ADT7410 demo");

    // Make sure the sensor is found, you can also pass in a different i2c
    // address with tempsensor.begin(0x49) for example
    if (!tempsensor.begin()) {
        Serial.println("Couldn't find ADT7410!");
        while (1)
            ;
    }

    // sensor takes 250 ms to get first readings
    delay(250);

    // ** Optional **
    // Can set ADC resolution
    // ADT7410_13BIT = 13 bits (default)
    // ADT7410_16BIT = 16 bits
    tempsensor.setResolution(ADT7410_16BIT);
    Serial.print("Resolution = ");
    switch (tempsensor.getResolution()) {
    case ADT7410_13BIT:
        Serial.print("13 ");
        break;
    case ADT7410_16BIT:
        Serial.print("16 ");
        break;
    default:
        Serial.print("??");
    }
    Serial.println("bits");
}

float get_temp_from_sensor()
{
    float c = tempsensor.readTempC();
    // delay(1000);
    return c;
}

#define DHTPIN 13 // Digital pin connected to the DHT sensor
// Feather HUZZAH ESP8266 note: use pins 3, 4, 5, 12, 13 or 14 --
// Pin 15 can work but DHT must be disconnected during program upload.

// Uncomment the type of sensor in use:
#define DHTTYPE DHT11 // DHT 11
// #define DHTTYPE    DHT22     // DHT 22 (AM2302)
// #define DHTTYPE    DHT21     // DHT 21 (AM2301)

// See guide for details on sensor wiring and usage:
//   https://learn.adafruit.com/dht/overview

DHT_Unified dht(DHTPIN, DHTTYPE);

uint32_t delayMS;

void setup_humidity_sensor()
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

float get_humidity()
{
    // Delay between measurements.
    // Get temperature event and print its value.
    float humidity = 0.0f;
    sensors_event_t event;
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
        Serial.println(F("Error reading humidity!"));
    } else {
        humidity = event.relative_humidity; // unit in %
    }
    return humidity;
}

#include "Adafruit_SGP40.h"
#include "Adafruit_SHT31.h"

Adafruit_SGP40 sgp;

void setup_co2_sensor()
{
    Serial.println("SGP40 test with SHT31 compensation");

    if (!sgp.begin()) {
        Serial.println("SGP40 sensor not found :(");
        while (1)
            ;
    }

    Serial.print("Found SHT3x + SGP40 serial #");
    Serial.print(sgp.serialnumber[0], HEX);
    Serial.print(sgp.serialnumber[1], HEX);
    Serial.println(sgp.serialnumber[2], HEX);
}

void loop_co2_sensor(float t, float h)
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

const int noisePin = A0;

void get_noise_level()
{
    int micValue = analogRead(noisePin);
    Serial.print("Noise Level: ");
    Serial.println(micValue);
}
