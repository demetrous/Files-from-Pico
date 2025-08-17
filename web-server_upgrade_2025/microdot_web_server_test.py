# Pico W Microdot server in AP-only mode (offline, all assets local)
from microdot import Microdot, send_file
    
import network, time
from machine import Pin, Timer

LED_IDLE_MS = 15000
led = Pin(15, Pin.OUT); led.value(0)

# Use a software timer (id = -1). Fall back gracefully if unsupported.
try:
    _led_timer = Timer(-1)  # soft timer (works on Pico W)
except Exception as e:
    print("Soft Timer not available:", e)
    _led_timer = None

def _schedule_led_off():
    if _led_timer:
        # Arm a one-shot that turns the LED off after inactivity
        _led_timer.init(mode=Timer.ONE_SHOT, period=LED_IDLE_MS,
                        callback=lambda t: led.value(0))
    else:
        # Fallback (no Timer): do nothing here; LED will stay on
        # (or implement a lazy check in your routes if you want)
        pass

app = Microdot()

AP_SSID     = 'PicoW-TinyServer'
AP_PASSWORD = 'tinyserver1234'   # >= 8 chars
AP_CHANNEL  = 1
HTTP_PORT   = 80
STATIC_ROOT = '/static'          # where your assets live on the Pico

led = Pin(15, Pin.OUT); led.value(0)

def set_opt(wlan, key, val):
    try:
        wlan.config(**{key: val}); return True
    except Exception:
        try:
            wlan.config(key, val); return True
        except Exception as e:
            print("config ignored:", key, "->", e); return False

def start_ap(ssid, password, channel):
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.active(False)

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    set_opt(ap, 'essid', ssid)
    set_opt(ap, 'password', password)
    set_opt(ap, 'channel', channel)

    try:
        ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
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
    print("AP active:", ap.active(), "| SSID:", cur_ssid, "| IP:", ip)
    return ap, ip, cur_ssid

ap, ip, cur_ssid = start_ap(AP_SSID, AP_PASSWORD, AP_CHANNEL)

# -------------- Static file server --------------
try:
    import uos as os
except ImportError:
    import os

STATIC_ROOT = '/static'

def safe_path(relpath):
    # Normalize & block traversal
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
    led.value(1); _schedule_led_off()  # <— light LED when any asset is requested
    full = safe_path(path)
    if not full:
        return 'Not allowed', 403, {'Content-Type': 'text/plain; charset=utf-8'}
    try:
        os.stat(full)  # ensure it exists
    except Exception:
        return 'Not Found', 404, {'Content-Type': 'text/plain; charset=utf-8'}
    # Let Microdot stream it; add cache header
    resp = send_file(full)
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    # (Optional) force close to reduce lingering sockets on tiny stacks:
    resp.headers['Connection'] = 'close'
    return resp


# -------------- Microdot app --------------


# Serve /static/... (covers up to two subfolders)
@app.route('/static/<name>')
def _static1(req, name):
    return serve_static(name)

@app.route('/static/<d1>/<name>')
def _static2(req, d1, name):
    return serve_static('{}/{}'.format(d1, name))

@app.route('/static/<d1>/<d2>/<name>')
def _static3(req, d1, d2, name):
    return serve_static('{}/{}/{}'.format(d1, d2, name))

# Local-asset HTML
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
  <meta name="description" content="" />
  <meta name="author" content="" />
  <title>Tiny Server - Runs on Tiny Raspberry Pi Pico W</title>
  <link rel="icon" type="image/x-icon" href="/static/assets/favicon.ico" />
  <link href="/static/css/styles.css" rel="stylesheet" />
</head>
<body id="page-top">
  <!-- Navigation-->
  <nav class="navbar navbar-expand-lg navbar-dark bg-success fixed-top" id="mainNav">
    <div class="container px-4">
      <a class="navbar-brand" href="#page-top">Tiny Server</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarResponsive"
        aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation"><span
          class="navbar-toggler-icon"></span></button>
      <div class="collapse navbar-collapse" id="navbarResponsive">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
          <li class="nav-item"><a class="nav-link" href="#parking">Parking Assistant</a></li>
          <li class="nav-item"><a class="nav-link" href="#cooling">Smart Cooling</a></li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Header-->
  <header class="bg-primary bg-image text-white" style="
    background-image: url('/static/assets/raspberry.jpg');
    background-size: cover; padding-top: 0; padding-bottom: 0; background-position: center;
  ">
    <div class="mask" style="background-color: rgba(0, 0, 0, 0.3); padding-top: 16rem; padding-bottom: 12rem;">
      <div class="container px-4 text-center">
        <h1 class="fw-bolder" style="text-shadow: 2px 2px 4px #000000;">Hi, I'm a Tiny Server!</h1>
        <p class="display-6" style="text-shadow: 2px 2px 4px #000000;">You are browsing this website from me now.</p>
        <a class="btn btn-lg btn-success" style="box-shadow: 4px 4px 11px #00000073;" href="#about">Check what I can do!</a>
      </div>
    </div>
  </header>

  <!-- About section-->
  <section id="about">
    <div class="container px-4">
      <div class="row gx-4 justify-content-center">
        <div class="col-lg-8">
          <h2>About the Tiny Server hardware</h2>
          <p class="lead">The Raspberry Pi Pico series is a range of tiny, fast, and versatile boards built using RP2040.</p>
          <p class="lead"><strong>Serving from:</strong> <code>http://%%IP%%/</code> (SSID: <code>%%SSID%%</code>)</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Services section-->
  <section class="bg-light" id="parking">
    <div class="container px-4">
      <div class="row gx-4 justify-content-center">
        <div class="col-lg-8">
          <h2>Parking Assistant</h2>
          <p class="lead">Green = ideal, Yellow = getting close, Red = too close.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Contact section-->
  <section id="cooling">
    <div class="container px-4">
      <div class="row gx-4 justify-content-center">
        <div class="col-lg-8">
          <h2>Smart Cooling</h2>
          <p class="lead">Monitors temperatures and controls ventilation for comfort and efficiency.</p>
        </div>
      </div>
    </div>
  </section>

  <footer class="py-5 bg-dark">
    <div class="container px-4">
      <p class="m-0 text-center text-white">Copyright &copy; Dmitrii Karaulanov 2024</p>
    </div>
  </footer>

  <!-- Local JS -->
  <script src="/static/js/bootstrap.bundle.min.js"></script>
  <script src="/static/js/scripts.js"></script>
</body>
</html>
"""

@app.route('/')
def index(_req):
    led.value(1); _schedule_led_off()  # <— light LED when any asset is requested
    page = HTML_TEMPLATE.replace('%%IP%%', ip).replace('%%SSID%%', cur_ssid)
    return page, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health')
def health(_req):
    led.value(1); _schedule_led_off()  # optional
    return {'ok': True, 'ip': ip, 'ssid': cur_ssid}, 200, {'Content-Type': 'application/json; charset=utf-8'}

print("Open: http://{}/  (SSID: {})".format(ip, cur_ssid))
app.run(host='0.0.0.0', port=HTTP_PORT, debug=False)

