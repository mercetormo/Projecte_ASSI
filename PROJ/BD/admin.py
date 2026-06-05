import bcrypt
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///projecte.db")

usuari = "admin"
password = "admin"

pwd_hash = bcrypt.hashpw(
    password.encode(),
    bcrypt.gensalt()
).decode()

with engine.begin() as con:
    con.execute(text("""
        INSERT INTO usuari (nom_usuari, pwd_hash, rol)
        VALUES (:nom, :pwd_hash, :rol)
    """), {
        "nom": usuari,
        "pwd_hash": pwd_hash,
        "rol": "admin"
    })

print("Usuari admin creat")
print("username: admin")
print("password: admin")
