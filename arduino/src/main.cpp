/*
  ArduinoMqttClient - WiFi Simple Sender

  This example connects to a MQTT broker and publishes a message to
  a topic once a second.

  The circuit:
  - Arduino MKR 1000, MKR 1010 or Uno WiFi Rev2 board

  This example code is in the public domain.
*/

#include <ArduinoMqttClient.h>
#if defined(ARDUINO_SAMD_MKRWIFI1010) || defined(ARDUINO_SAMD_NANO_33_IOT) ||  \
    defined(ARDUINO_AVR_UNO_WIFI_REV2)
#include <WiFiNINA.h>
#elif defined(ARDUINO_SAMD_MKR1000)
#include <WiFi101.h>
#elif defined(ARDUINO_ARCH_ESP8266)
#include <ESP8266WiFi.h>
#elif defined(ARDUINO_PORTENTA_H7_M7) || defined(ARDUINO_NICLA_VISION) ||      \
    defined(ARDUINO_ARCH_ESP32) || defined(ARDUINO_GIGA) ||                    \
    defined(ARDUINO_OPTA)
#include <WiFi.h>
#elif defined(ARDUINO_PORTENTA_C33)
#include <WiFiC3.h>
#elif defined(ARDUINO_UNOR4_WIFI)
#include <WiFiS3.h>
#endif

#include "arduino_secrets.h"
#define MAX_WIFI_CON_TRIES 3

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID; // your network SSID (name)
char pass[] = SECRET_PASS; // your network password10.43.100.127 (use for WPA,
                           // or use as key for WEP)

#include <sensors.h>

// Create the ADT7410 temperature sensor object

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = BROKER;
int port = 1883;
const char topic[] = TOPIC;

const long interval = 1000;
unsigned long previousMillis = 0;

int count = 0;

void connect_wifi() {
  // attempt to connect to WiFi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);

  int connection_tries = 0;

  while (WiFi.begin(ssid, pass) != WL_CONNECTED && connection_tries < MAX_WIFI_CON_TRIES) {
    // failed, retry
    Serial.print(".");
    delay(5000);
    connection_tries++;
  }

  Serial.println("You're connected to the network");
  Serial.println();
}

void connect_mqtt() {
  // You can provide a unique client ID, if not set the library uses
  // Arduino-millis() Each client must have a unique client ID
  // mqttClient.setId("4711");

  // You can provide a username and password for authentication
  // mqttClient.setUsernamePassword("username", "password");
  mqttClient.setUsernamePassword(MQTT_USER, MQTT_PASS);

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1)
      ;
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}

void setup() {
  // Initialize serial and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  // connect_wifi();
  // connect_mqtt();

  setup_temp_sensor();
  // setup_humidity_sensor();
  setup_co2_sensor();
}


void loop() {
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  mqttClient.poll();

  // to avoid having delays in loop, we'll use the strategy from
  // BlinkWithoutDelay see: File -> Examples -> 02.Digital -> BlinkWithoutDelay
  // for more info
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;

    Serial.print("Sending message to topic: ");
    Serial.println(topic);
    Serial.print("hello ");
    Serial.println(count);
    loop_co2_sensor();

    // // send message, the Print interface can be used to set the message contents
    // mqttClient.beginMessage(topic);
    // mqttClient.print("temp: ");
    // mqttClient.println(get_temp_from_sensor());
    // mqttClient.print("humidity: ");
    // mqttClient.println(get_humidity());
    // mqttClient.endMessage();

    Serial.println();

    count++;
  }
}
