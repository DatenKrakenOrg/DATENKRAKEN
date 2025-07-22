#include <NTPClient.h>
#include <WiFiUdp.h>

WiFiUDP ntpUDP;

// By default 'pool.ntp.org' is used with 60 seconds update interval and
// no offset
NTPClient timeClient(ntpUDP);

// You can specify the time server pool and the offset, (in seconds)
// additionally you can specify the update interval (in milliseconds).
// NTPClient timeClient(ntpUDP, "europe.pool.ntp.org", 3600, 60000);

void setupNTP(){
  timeClient.begin();
}

void updateNTP() {
  timeClient.update();

  Serial.print("Time ");
  Serial.println(timeClient.getEpochTime());

  delay(1000);
}
