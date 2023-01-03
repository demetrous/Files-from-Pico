import machine
import socket
import math

from picozero import pico_temp_sensor, pico_led
from secrets import *
from do_connect import *

from dht_read import *

def webpage(temperature, humidity, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <style>
                  .block {{
                    display: block;
                    width: 100%;
                    border: none;
                    background-color: #04aa6d;
                    padding: 14px 28px;
                    font-size: 32px;
                    cursor: pointer;
                    text-align: center;
                  }}
                  .off {{
                    background-color: #d8d8d8;
                  }}
                  h1 {{
                    text-align: center;
                  }}
                </style>
              </head>
              <body>
                <form action="./lighton">
                  <input type="submit" value="Light on" class="block" />
                </form>
                <form action="./lightoff">
                  <input type="submit" value="Light off" class="block off" />
                </form>
                <h1>LED is {state}</h1>
                <h1>Temperature is {temperature}</h1>
                <h1>Humidity is {humidity}</h1>
              </body>
            </html>

            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    #temperature
    #humidity
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
        #temperature = pico_temp_sensor.temp        
        #temperature, humidity = DHTread()
        temperature = 10
        humidity = 15
        html = webpage(temperature, humidity, state)
        client.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(html)
        client.close()

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return(connection)


try:
    ip=do_connect()
    if ip is not None:
        connection=open_socket(ip)
        serve(connection)
except KeyboardInterrupt:
    machine.reset()


