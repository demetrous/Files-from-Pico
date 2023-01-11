from machine import Pin
from lcd_out_methods import *
from time import sleep

import dht

sensor = dht.DHT22(Pin(27))

while True:
    sensor.measure()
    sleep(5)
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    
    print_two_rows(temperature, humidity)
    
