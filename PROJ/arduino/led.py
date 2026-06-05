import http.server
import socketserver
import serial
import time
import json

PORT = 8000

SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

#arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

class Handler(http.server.BaseHTTPRequestHandler):

    def enviar_json(self, dades, codi=200):
        self.send_response(codi)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(dades).encode("utf-8"))

        """
    def enviar_arduino(self, ordre):
        arduino.write(ordre.encode("utf-8"))
        resposta = arduino.readline().decode("utf-8").strip()
        return resposta
        """
    def do_GET(self):
        led_estat=1
        potentiometer=123

        if self.path == "/":
            self.enviar_json({
                "message": "API activa",
                "endpoints": [
                    "/led/on",
                    "/led/off",
                    "/led/status",
                    "/potentiometer"]
            })

        elif self.path == "/led/on":
            #led_estat = self.enviar_arduino("1")
            self.enviar_json({"status": "on"})

        elif self.path == "/led/off":
            #led_estat = self.enviar_arduino("0")
            self.enviar_json({"status": "off"})

        elif self.path == "/led/status":
            #led_estat=self.enviar_arduino("?")
            if led_estat=="1":
                self.enviar_json({"status": "on"})
            else:
                self.enviar_json({"status": "off"})
        elif self.path == "/potentiometer":
            #potentiometer = self.enviar_arduino("P")
            self.enviar_json({"value": potentiometer})
        else:
            self.enviar_json({"error": "No trobat"}, 404)


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Servidor en marxa al port", PORT)
    print("Arduino connectat a", SERIAL_PORT)
    httpd.serve_forever()
