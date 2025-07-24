# MQTT-Topicformat
## Topic 
`dhbw/ai/si2023/<GROUP-NUMBER>/<SENSOR-TYPE>/SensorID`  
(Group 6)

## Sensortypes
- temp (temperature)
- mic (microphone / noise level)
- hum (humidity)
- co2 (CO2 Sensor)

# MQTT-Messageformat

The messages are sent in the json format.
This json object contains  

- unix timestamp (examine when the data was gathered)  
- value array (the gathered data)  
- sequence number (to be able to check if a message was lost)  
- meta data (can be used to transfer custom data)  

A example json object looks like this
```json
{
  "timestamp": "1753098733",
  "value": [23.45],
  "sequence" : 123,
  "meta": {
    "firmware": "v1.2.3",
    "startup" : "1753098730"
  }
}
```
