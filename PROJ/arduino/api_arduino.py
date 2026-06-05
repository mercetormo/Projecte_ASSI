from flask import Flask, jsonify, request, render_template
import serial
import time

PORT = 8000

SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

app = Flask(__name__)


def enviar_arduino(ordre):
    arduino.write(ordre.encode("utf-8"))
    resposta = arduino.readline().decode("utf-8").strip()
    return resposta



"""
@app.route("/")
def inicial():
    return jsonify({
        "message": "API activa",
        "endpoints": [
            "GET /api/actuator",
            "PUT /api/actuator",
            "GET /api/sensor"
        ]
    })
"""

@app.route("/")
def inicial():
    return render_template("index.html")


@app.route("/api/actuator", methods=["GET"])
def status():

    led_estat = enviar_arduino("?")

    return jsonify({
        "state": led_estat == "1"
    })


@app.route("/api/actuator", methods=["PUT"])
def control():

    global led_estat

    dades = request.get_json()

    if dades is None or "state" not in dades:
        return jsonify({"error": "JSON invàlid"}), 400

    if dades["state"] == True:
        led_estat = enviar_arduino("1")
    else:
        led_estat = enviar_arduino("0")

    return jsonify({
        "state": led_estat == "1"
    })


@app.route("/api/sensor", methods=["GET"])
def get_potentiometer():

    potentiometer = enviar_arduino("P")

    return jsonify({
        "value": potentiometer
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
