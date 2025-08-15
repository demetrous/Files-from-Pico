from machine import Pin
import utime
import math
from ws2812 import WS2812

trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)
ws = WS2812(machine.Pin(0),8)

min_distance = 400
max_distance = 800
dist_range = max_distance - min_distance
current_amount = 0

white = [120,120,120]
green = [0,255,0]
orange = [255,165,0]
red = [255,0,0]
off = [0,0,0]

def flashing_lights(color,off,amount,speed):    
    
    for i in range(amount):
        if ws[i] == off:
            ws[i] = color
        else:
            ws[i] = off   
   
    ws.write()
    utime.sleep_ms(speed) #200
    
    
    
def lights_on(amount):

    global current_amount
    
    if current_amount == amount:
        return
    else:
        current_amount = amount
               
    if amount <= 0:
        for i in range(8):
            ws[i] = white
        ws.write()
        return
    
    if amount > 8:
        #flashing_lights(red,off,8,200)            
        for i in range(8):
            ws[i] = red
        ws.write()
        return            
            
    ws[0] = green if amount > 0 else off
    ws[1] = green if amount > 1 else off
    ws[2] = green if amount > 2 else off
    ws[3] = green if amount > 3 else off
    ws[4] = orange if amount > 4 else off
    ws[5] = orange if amount > 5 else off
    ws[6] = red if amount > 6 else off
    ws[7] = red if amount > 7 else off
            
    ws.write()

  
    
def light_range(measure_distance):
    diff = measure_distance - min_distance   
    position = math.floor(8 - diff / dist_range * 8)
    print(position)
    lights_on(position)
    #return position

def ultra():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   while echo.value() == 0:
       signaloff = utime.ticks_us()
   while echo.value() == 1:
       signalon = utime.ticks_us()
   timepassed = signalon - signaloff
   distance = round(timepassed * 0.1715)
   light_range(distance)

   print("The distance from object is ",distance,"mm")
while True:
   ultra()
   utime.sleep_ms(50)
