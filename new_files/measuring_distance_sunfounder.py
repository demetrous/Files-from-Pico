import machine
from ws2812 import WS2812
import utime
import urandom

ws = WS2812(machine.Pin(0),8)

def flowing_light():
    for i in range(7,0,-1):
        ws[i] = ws[i-1]
    ws[0] = int(urandom.uniform(0, 0xFFFFFF))
    ws.write()
    utime.sleep_ms(80)
    
def flashing_light():
    for i in range(0,256,20):
        ws[0] = [i,0,0]   
        ws.write()
        utime.sleep_ms(2)

def onoff_light():    
    zero = [0,0,0]
    on = [255,0,0]
    if ws[0] == zero:
        ws[0] = on
    else:
        ws[0] = zero
    ws.write()
    utime.sleep_ms(200)   

while True:
    onoff_light()
    print(ws[0])

