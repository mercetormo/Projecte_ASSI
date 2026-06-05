from flask import Flask, request, jsonify, render_template, session, redirect
import bcrypt
from sqlalchemy import create_engine, text
import requests
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_PATH  = os.path.join(BASE_DIR, "BD", "projecte.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

app= Flask(__name__)
app.secret_key = "clau_secreta_projecte"


ID_SENSOR = 1
ID_ACTUADOR = 2
ARDUINO_API = "http://localhost:8000"

# Registre de dades del sensor (activar/desactivar des de l'admin)
REGISTRE_ACTIU = True


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    if session.get("rol") != "admin":
        return redirect("/")
    return render_template("admin.html")

@app.route("/viewer")
def viewer():
    if "usuari" not in session:
        return redirect("/")
    return render_template("viewer.html")

@app.route("/register")
def register():
    return render_template("registrar.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    nom=data.get("username","")
    pwd=data.get("password","")

    with engine.connect() as con:
        fila = con.execute(text("""
        SELECT nom_usuari, pwd_hash, rol FROM usuari
        WHERE nom_usuari = :nom
        """),{"nom": nom}).fetchone()

    if fila is None:
        return jsonify({"error": "Usuari incorrecte"}), 401

    user = dict(fila._mapping) #agafem el sql i fem un diccionari

    if not bcrypt.checkpw(pwd.encode(),user["pwd_hash"].encode()):  #comprovem que la contrasenya sigui correcta
        return jsonify({"error": "Contrasenya incorrecta"}), 401

    session["usuari"] = user["nom_usuari"]
    session["rol"] = user["rol"]

    return jsonify({
        "message": "OK",
        "rol": user["rol"]
    })



@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "OK"})


# ---------------------------------------------------
# GET SENSOR
# ---------------------------------------------------
LLINDAR_SENSOR = 3

@app.route("/api/sensor", methods=["GET"])
def get_sensor():
    if "usuari" not in session:
        return jsonify({"error": "No autenticat"}), 401

    r = requests.get(f"{ARDUINO_API}/api/sensor", timeout=5)
    dades = r.json()

    valor = int(dades["value"])

    if REGISTRE_ACTIU:
        with engine.begin() as con:

            fila = con.execute(text("""
                SELECT estat_registre
                FROM sensor
                WHERE id_disp = :id
            """), {"id": ID_SENSOR}).fetchone()

            valor_anterior = int(fila[0]) if fila else None

            if valor_anterior is None or abs(valor - valor_anterior) > LLINDAR_SENSOR:

                con.execute(text("""
                    INSERT INTO historic (nom_usuari, id_disp, valor_estat)
                    VALUES (:usuari, :id_disp, :valor)
                """), {
                    "usuari": session.get("usuari", "prova"),
                    "id_disp": ID_SENSOR,
                    "valor": str(valor)
                })

                con.execute(text("""
                    UPDATE sensor
                    SET estat_registre = :valor
                    WHERE id_disp = :id
                """), {
                    "valor": valor,
                    "id": ID_SENSOR
                })

    return jsonify({"value": valor})

# ---------------------------------------------------
# PUT ACTUATOR
# ---------------------------------------------------
@app.route("/api/actuator", methods=["PUT"])
def put_actuator():
    if "usuari" not in session:
        return jsonify({"error": "No autenticat"}), 401
    
    if session.get("rol") != "admin":
        return jsonify({"error": "Només admin"}), 403

    data = request.json

    if data is None or "state" not in data:
        return jsonify({"error": "JSON invàlid"}), 400

    estat=bool(data["state"])  #estat que volem
    
    r = requests.put(f"{ARDUINO_API}/api/actuator",json={"state": estat}, timeout=5)

    if r.status_code != 200:
        return jsonify({"message": "ERROR"}), 502
    
    with engine.begin() as con:
        con.execute(text("""
        UPDATE actuador
        SET estat_actual = :estat
        WHERE id_disp = :id
        """), {"estat": 1 if estat else 0,"id": ID_ACTUADOR})

        con.execute(text("""
        INSERT INTO historic (nom_usuari, id_disp, valor_estat)
        VALUES (:usuari, :id_disp, :valor)
        """), {"usuari": session["usuari"],"id_disp": ID_ACTUADOR,"valor": "ON" if estat else "OFF"})


    return jsonify({
        "message": "OK",
        "state": estat
    })


@app.route("/api/actuator", methods=["GET"])
def get_actuator():
    if "usuari" not in session:
        return jsonify({"error": "No autenticat"}), 401

    r = requests.get(f"{ARDUINO_API}/api/actuator", timeout=5)
    dades = r.json()

    return jsonify({
        "state": dades["state"]
    })


# ---------------------------------------------------
# REGISTRE SENSOR (activar / desactivar)
# ---------------------------------------------------
@app.route("/api/sensor/registre", methods=["GET"])
def get_registre():
    if "usuari" not in session:
        return jsonify({"error": "No autenticat"}), 401

    return jsonify({"estat_registre": REGISTRE_ACTIU})


@app.route("/api/sensor/registre", methods=["PUT"])
def put_registre():
    if "usuari" not in session:
        return jsonify({"error": "No autenticat"}), 401

    if session.get("rol") != "admin":
        return jsonify({"error": "Només admin"}), 403

    data = request.json

    if data is None or "estat_registre" not in data:
        return jsonify({"error": "JSON invàlid"}), 400

    global REGISTRE_ACTIU
    REGISTRE_ACTIU = bool(data["estat_registre"])

    return jsonify({
        "message": "OK",
        "estat_registre": REGISTRE_ACTIU
    })


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    nom = data.get("username", "").strip()
    pwd = data.get("password", "")

    if len(nom) < 4 or len(pwd) < 8:
        return jsonify({"error": "Dades insuficients"}), 400

    pwd_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

    try:
        with engine.begin() as con:
            con.execute(text("""
                INSERT INTO usuari (nom_usuari, pwd_hash, rol)
                VALUES (:nom, :h, 'viewer')
            """), {"nom": nom, "h": pwd_hash})
    except Exception:
        return jsonify({"error": "L'usuari ja existeix"}), 409

    return jsonify({"message": "OK"}), 201




#------------------------------------------
#HISTÒRICS
#------------------------------------------
@app.route("/api/historic", methods=["GET"])
def historic():
    tipus = request.args.get("tipus", "sensor")

    if tipus == "actuador":
        id_disp = ID_ACTUADOR
    else:
        id_disp = ID_SENSOR

    if session.get("rol") == "admin":
        vista = "historic_admin"
    else:
        vista = "historic_viewer"

    sql = text(f"""
    SELECT data, nom_usuari, valor_estat
    FROM {vista}
    WHERE id_disp = :id
    ORDER BY data DESC
    LIMIT 100
    """)

    with engine.begin() as con:
        files = con.execute(sql, {"id": id_disp}).fetchall()

    return jsonify([
        {
            "data": f[0],
            "nom_usuari": f[1],
            "valor_estat": f[2]
        }
        for f in files
    ])



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
