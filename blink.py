from machine import Pin
import utime
led = Pin(28, Pin.OUT)
led.low()
i=1
while i<11:
    led.toggle()
    print("Toggle ", i)
    utime.sleep(1)
    i+=1