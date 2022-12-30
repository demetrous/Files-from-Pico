import machine
import utime
import math
from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd

thermistor = machine.ADC(28)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

pin = Pin(16, Pin.OUT, Pin.PULL_DOWN)

while True:
    temperature_value = thermistor.read_u16()
    Vr = 3.3 * float(temperature_value) / 65535
    Rt = 10000 * Vr / (3.3 - Vr)
    temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
    Cel = temp - 273.15
    Fah = Cel * 1.8 + 32
   
    lcd.putstr('%.2f C\n%.2f F' % (Cel, Fah))
    utime.sleep_ms(2000)
    lcd.clear()

