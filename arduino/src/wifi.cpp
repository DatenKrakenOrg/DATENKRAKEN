#include "arduino_secrets.h"
#include <WiFiNINA.h>

#define MAX_WIFI_CON_TRIES 3

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

WiFiClient wifiClient;

void connectWifi()
{
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);

    int connection_tries = 0;

    while (WiFi.begin(ssid, pass) != WL_CONNECTED && connection_tries < MAX_WIFI_CON_TRIES) {
        Serial.print(".");
        delay(5000);
        connection_tries++;
    }

    if (connection_tries >= MAX_WIFI_CON_TRIES){
        Serial.println("Connection to WiFi failed");
    }
    else {
        Serial.println("You're connected to the network");
    }
    Serial.println();

}

