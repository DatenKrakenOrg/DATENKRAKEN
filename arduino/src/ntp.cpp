#include "wifi.h"
#include <NTPClient.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>

WiFiUDP ntpUDP;

// By default 'pool.ntp.org' is used with 60 seconds update interval and
// no offset
NTPClient timeClient(ntpUDP);

// You can specify the time server pool and the offset, (in seconds)
// additionally you can specify the update interval (in milliseconds).
// NTPClient timeClient(ntpUDP, "europe.pool.ntp.org", 3600, 60000);

void setupNTP()
{
    timeClient.begin();
}

unsigned long getNTP()
{

    if (WiFi.status() != WL_CONNECTED) {
        WiFi.end();
        connectWifi();
    }
    timeClient.update();
    return timeClient.getEpochTime();
}
