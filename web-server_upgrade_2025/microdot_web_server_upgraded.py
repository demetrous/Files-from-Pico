# Pico W Microdot server in AP-only mode (offline)
from microdot import Microdot
import network, time
from machine import Pin

AP_SSID     = 'PicoW-TinyServer'
AP_PASSWORD = 'tinyserver1234'   # >= 8 chars
AP_CHANNEL  = 1                  # try 1/6/11 if needed
HTTP_PORT   = 80

led = Pin(15, Pin.OUT); led.value(0)

def set_opt(wlan, key, val):
    """Try both config styles; ignore if unsupported."""
    try:
        wlan.config(**{key: val})
        return True
    except Exception:
        try:
            wlan.config(key, val)  # some ports accept this
            return True
        except Exception as e:
            print("config ignored:", key, "->", e)
            return False

def start_ap(ssid, password, channel):
    # make sure STA is off so it can't interfere
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.active(False)

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    # Set SSID/password/channel (each may fail on very old builds; we try anyway)
    set_opt(ap, 'essid', ssid)
    set_opt(ap, 'password', password)
    set_opt(ap, 'channel', channel)

    # Try to force a predictable IP (optional)
    try:
        ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
    except Exception as e:
        print("ifconfig set ignored:", e)

    # Wait for AP to come up
    for _ in range(30):
        if ap.active():
            break
        time.sleep_ms(100)

    ip = ap.ifconfig()[0]
    # Read back what the firmware actually applied
    try:
        cur_ssid = ap.config('essid')
    except Exception:
        cur_ssid = ssid  # best guess
    print("AP active:", ap.active(), "| SSID:", cur_ssid, "| IP:", ip)
    return ap, ip, cur_ssid

# Bring up AP
ap, ip, cur_ssid = start_ap(AP_SSID, AP_PASSWORD, AP_CHANNEL)

# ----- Microdot app -----

app = Microdot()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <title>Tiny Server - Runs on Tiny Raspberry Pi Pico W</title>
    <link rel="icon" type="image/x-icon"
        href="https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/assets/favicon.ico" />
    <!-- Core theme CSS (includes Bootstrap)-->
    <link href="https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/css/styles.css" rel="stylesheet" />
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
    background-image: url('https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/assets/raspberry-pi-pico-w-hand.jpg');
    background-size: cover; padding-top: 0;padding-bottom: 0; background-position: center;
  ">
        <div class="mask" style="background-color: rgba(0, 0, 0, 0.3); padding-top: 16rem;padding-bottom: 12rem;">
            <div class="container px-4 text-center">
                <h1 class="fw-bolder" style="text-shadow: 2px 2px 4px #000000;">Hi, I'm a Tiny Server!</h1>
                <p class="display-6" style="text-shadow: 2px 2px 4px #000000;">You are browsing this website from me
                    now.</p>
                <a class="btn btn-lg btn-success" style="box-shadow: 4px 4px 11px #00000073;" href="#about">Check what I
                    can do!</a>
            </div>
        </div>
    </header>
    <!-- About section-->
    <section id="about">
        <div class="container px-4">
            <div class="row gx-4 justify-content-center">
                <div class="col-lg-8">
                    <h2>About the Tiny Server hardware</h2>
                    <p class="lead">The Raspberry Pi Pico series is a range of tiny, fast, and versatile boards built
                        using RP2040, the flagship microcontroller chip designed by Raspberry Pi in the UK.</p>

                    <p class="lead">From light displays and IoT devices to signage and manufacturing processes, the
                        Raspberry Pi Pico series gives you the power to control countless home, hobby, and industrial
                        operations.</p>

                    <p class="lead">Programmable in C++ and MicroPython, Pico is adaptable to a vast range of
                        applications and skill levels, and getting started is as easy as dragging and dropping a file.
                    </p>

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
                    <p class="lead">Built with Raspberry Pi Pico, the Parking Assistant is a cutting-edge device that
                        signals the current position of your car while parking in the garage. This innovative technology
                        ensures precision and ease as you maneuver your vehicle into place.</p>
                    <p class="lead"> Whether you're parking a
                        compact car or a larger SUV, the Parking Assistant can be adjusted to accommodate any length,
                        providing customized assistance tailored to your specific vehicle dimensions.</p>
                    <p class="lead">With its intuitive design and reliable performance, you can trust the Parking
                        Assistant to streamline your parking experience and eliminate the guesswork associated with
                        tight spaces.</p>
                    <p class="lead">Say goodbye to the stress of parking and hello to effortless, worry-free parking
                        with the Raspberry Pi Pico Parking Assistant.</p>

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



                    <p class="lead">Living in a hot climate poses a constant challenge: keeping your living space cool
                        during relentless summer heat. But fret not, for the Smart Cooling system is here to offer a
                        solution. Utilizing the advanced technology of Raspberry Pi Pico, this innovative system
                        monitors the daily temperature fluctuations with precision. By analyzing both indoor and outdoor
                        temperatures, it intelligently regulates your cooling system to ensure optimal comfort and
                        energy efficiency.</p>

                    <p class="lead">Gone are the days of manually adjusting your thermostat or relying on guesswork to
                        combat the sweltering heat. The Smart Cooling system automates the process, seamlessly engaging
                        the cooling fan when the outside temperature drops below that of the indoors. This proactive
                        approach not only maintains a comfortable environment but also reduces energy consumption,
                        saving you money on your utility bills.</p>

                    <p class="lead">With its intuitive design and reliable performance, the Smart Cooling system
                        provides peace of mind, allowing you to enjoy a cool and refreshing indoor atmosphere, even in
                        the midst of the hottest summer days. Say goodbye to overheated spaces and hello to personalized
                        climate control with Raspberry Pi Pico's Smart Cooling system.</p>

                </div>
            </div>
        </div>
    </section>
    <!-- Footer-->
    <footer class="py-5 bg-dark">
        <div class="container px-4">
            <p class="m-0 text-center text-white">Copyright &copy; Dmitrii Karaulanov 2024</p>
        </div>
    </footer>
    <!-- Bootstrap core JS-->
    <script src="https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/js/bootstrap.bundle.min.js"></script>
    <!-- Core theme JS-->
    <script src="https://cdn.jsdelivr.net/gh/demetrous/tiny-server-assets/js/scripts.js"></script>
</body>

</html>
"""

@app.route('/')
def index(_req):
    # ip and ssid should be variables you computed earlier when starting AP
    page = HTML_TEMPLATE.replace("%%IP%%", ip).replace("%%SSID%%", cur_ssid)
    return page, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health')
def health(_req):
    return {'ok': True, 'ip': ip, 'ssid': cur_ssid}, 200, {'Content-Type': 'application/json; charset=utf-8'}

print("Open: http://{}/  (SSID: {})".format(ip, cur_ssid))
app.run(host='0.0.0.0', port=80, debug=False)

