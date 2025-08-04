# Deployment of new Arduinos

## Prerequisite
To upload the code to an arduino you need a software like pio or the arduino IDE.

## Clone the Repository
For the deployment you need to download the code from our [repository](https://github.com/DatenKrakenOrg/DATENKRAKEN.git).  

## Config
For the configuration of your needs you rename the `arduino_secrets_template.h` file to `arduino_secrets.h` in the arduino folder and adjust the following information in the file accordingly.

```cpp
#define ROOM_ID 1
#define TOPIC "topic/subtopic" //Sensortype is automatically added
#define SECRET_SSID "wifi ssid"
#define SECRET_PASS "wifi password"
#define BROKER "broker address"
#define MQTT_USER "username"
#define MQTT_PASS "userpassword"
```

The topic is then combined with the sensor and the room id to make it unique. In this example the topic to publish would be `topic/subtopic/sensortype/1`.

## Upload

After changing the filename and the information in the file you upload this to the arduino with pio or the arduino ide.  
When you plug the arduino in it connects automatically to the wifi and the broker you provided and will start publishing the data on the configured topic.
