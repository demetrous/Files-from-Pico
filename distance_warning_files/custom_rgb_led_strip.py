import machine
from ws2812 import WS2812
import utime
import urandom

ws = WS2812(machine.Pin(0),8)

ws[0] = [255,0,0]
ws[1] = [0,255,0]
ws[2] = [0,0,255]
ws[3] = [255,255,0]
ws[4] = [255,165,0]
ws[5] = [99,199,0]
ws[6] = [128,128,128]
ws[7] = [255,255,255]
ws.write()