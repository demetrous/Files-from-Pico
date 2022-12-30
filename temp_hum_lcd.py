from machine import I2C, Pin
from time import sleep
from pico_i2c_lcd import I2cLcd
from dht import DHT11

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

pin = Pin(16, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)


while True:
    sensor.measure()        
    lcd.putstr("Temp: {}".format(sensor.temperature)+"\n")
    lcd.putstr("Humidity: {}".format(sensor.humidity))
    sleep(5)
    lcd.clear()
   