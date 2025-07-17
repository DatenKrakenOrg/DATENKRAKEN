# Hardware Components
- Arduino MKR Wifi 1010
- Temperature sensor
- Humidity sensor
- CO2 sensor
- Noise level sensor

# Output format
Each sensor has a different unit of measurement. Therefore different datatypes are needed.

1. Temperature
The temperature is measured in celcius (°C), the values are floats and can be negative.
- Unit: °C

2. Humidity Sensor
The Humidity sensor returns values ranging from 0% to 100%, anything other is a invalid value.
- Unit: relative Humidity in %

3. CO2 Sensor
The CO2 sensor is dependant on temperature and humidity. These values are needed to calculate the VOC-Index. 
The VOC-Index is ranging value from 0 to 500, any other value is invalid
- Unit: VOC-Index (ppm?)

4. Noise Level


# Required Libraries
- Platform.ini holds all used Libraries - WIP, not complete yet
