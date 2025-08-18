# Pico W Microdot server (AP-only, local assets, better range, onboard LED)
# - Set your country code below (VERY IMPORTANT for TX power/channels)

from microdot import Microdot, send_file
import rp2, network, time, gc
from machine import Pin, Timer

# -------- Region: set to your 2-letter code ----------
rp2.country('US')   # <-- CHANGE to e.g. 'US','CA','GB','DE','AU', etc.

# ------------- Config -------------
AP_SSID     = 'PicoW-TinyServer'
AP_PASSWORD = 'tinyserver1234'     # >= 8 chars
DEFAULT_CH  = 1                    # fallback if scan fails
HTTP_PORT   = 80
STATIC_ROOT = '/static'
LED_IDLE_MS = 15000                # LED off after inactivity

# ------------- Onboard LED -------------
try:
    led = Pin('LED', Pin.OUT)   # Pico W onboard LED
except Exception:
    led = Pin(25, Pin.OUT)
led.value(0)

try:
    _led_timer = Timer(-1)      # soft one-shot timer
except Exception:
    _led_timer = None

def _schedule_led_off():
    if _led_timer:
        _led_timer.init(mode=Timer.ONE_SHOT, period=LED_IDLE_MS,
                        callback=lambda t: led.value(0))

# ------------- Wi-Fi helpers -------------
def set_opt(wlan, key, val):
    try:
        wlan.config(**{key: val}); return True
    except Exception:
        try:
            wlan.config(key, val); return True
        except Exception as e:
            print("config ignored:", key, "->", e); return False

def pick_best_channel():
    """Scan 2.4 GHz and pick the least-crowded among 1/6/11."""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        # Some firmwares accept pm tweak (ignored if unknown)
        set_opt(sta, 'pm', 0xA11140)
        nets = sta.scan()  # (ssid, bssid, channel, RSSI, auth, hidden)
        score = {1:0, 6:0, 11:0}
        for ssid, bssid, ch, rssi, auth, hidden in nets:
            if ch in score:
                # rssi is negative; stronger AP => larger penalty
                score[ch] += (120 + rssi) if rssi < 0 else 120
        sta.active(False)
        best = min(score, key=score.get)
        print("Channel scan:", score, "-> best:", best)
        return best
    except Exception as e:
        print("Channel scan failed:", e)
        return DEFAULT_CH

def start_ap(ssid, password, channel=None):
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.active(False)

    ch = channel or pick_best_channel()

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    set_opt(ap, 'essid', ssid)
    set_opt(ap, 'password', password)
    set_opt(ap, 'channel', ch)
    set_opt(ap, 'pm', 0xA11140)  # try to keep radio responsive (ignored if unsupported)

    try:
        ap.ifconfig(('192.168.4.1','255.255.255.0','192.168.4.1','8.8.8.8'))
    except Exception as e:
        print("ifconfig set ignored:", e)

    for _ in range(30):
        if ap.active():
            break
        time.sleep_ms(100)

    ip = ap.ifconfig()[0]
    try:
        cur_ssid = ap.config('essid')
    except Exception:
        cur_ssid = ssid
    print("AP active:", ap.active(), "| SSID:", cur_ssid, "| IP:", ip, "| CH:", ch)
    return ap, ip, cur_ssid

ap, ip, cur_ssid = start_ap(AP_SSID, AP_PASSWORD, None)

# ------------- Microdot app -------------
app = Microdot()
app.debug = False  # reduce noisy traces

try:
    import uos as os
except ImportError:
    import os

def safe_path(relpath):
    if not relpath:
        return None
    if relpath.startswith('/'):
        relpath = relpath[1:]
    if '..' in relpath or relpath.startswith('.'):
        return None
    while '//' in relpath:
        relpath = relpath.replace('//', '/')
    return STATIC_ROOT + '/' + relpath

@app.route('/static/<path:path>')
def static_any(_req, path):
    led.value(1); _schedule_led_off()
    gc.collect()  # free RAM before streaming
    full = safe_path(path)
    if not full:
        return 'Not allowed', 403, {'Content-Type':'text/plain; charset=utf-8','Connection':'close'}
    try:
        os.stat(full)
    except Exception:
        return 'Not Found', 404, {'Content-Type':'text/plain; charset=utf-8','Connection':'close'}
    resp = send_file(full)
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    resp.headers['Connection'] = 'close'  # avoid long-lived keep-alives
    return resp

@app.route('/')
def index(_req):
    led.value(1); _schedule_led_off()
    resp = send_file('/static/index.html')
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Connection'] = 'close'
    return resp

@app.route('/health')
def health(_req):
    led.value(1); _schedule_led_off()
    return {'ok': True, 'ip': ip, 'ssid': cur_ssid}, 200, {'Content-Type':'application/json; charset=utf-8','Connection':'close'}

print("Open: http://{}/  (SSID: {})".format(ip, cur_ssid))
app.run(host='0.0.0.0', port=HTTP_PORT, debug=False)
