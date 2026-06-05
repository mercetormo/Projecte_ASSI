import bcrypt
import sqlite3
import os


ADMINS = [
    "Manel Abizanda",
    "Enric Plana",
    "Merce Tormo",
    "Oscar Alegre",
    "Carolina Martins",
]


def crear_bd(fitxer):
    if os.path.exists(fitxer):
        os.remove(fitxer)

    conn = sqlite3.connect(fitxer)

    with open("script.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    for nom in ADMINS:
        h = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO usuari (nom_usuari, pwd_hash, rol) VALUES (?, ?, 'admin');",
            (nom, h)
        )

    cur.execute("INSERT INTO dispositiu (id_disp, ubicacio) VALUES (1, 'Arduino UNO - Shield');")
    cur.execute("INSERT INTO dispositiu (id_disp, ubicacio) VALUES (2, 'Arduino UNO - Shield');")
    cur.execute("INSERT INTO sensor   VALUES (1, 1);")
    cur.execute("INSERT INTO actuador VALUES (2, 0);")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    crear_bd("projecte.db")
