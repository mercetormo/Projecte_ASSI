/* TAULES */

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuari (
    nom_usuari TEXT PRIMARY KEY,
    pwd_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('viewer', 'admin'))
);

CREATE TABLE IF NOT EXISTS dispositiu (
    id_disp INTEGER PRIMARY KEY AUTOINCREMENT,
    ubicacio TEXT
);

-- Taules Herencia de "dispositiu"
CREATE TABLE IF NOT EXISTS sensor (
    id_disp INTEGER PRIMARY KEY,
    estat_registre INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (id_disp) REFERENCES dispositiu(id_disp)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS actuador (
    id_disp INTEGER PRIMARY KEY,
    estat_actual INTEGER NOT NULL DEFAULT 0 CHECK (estat_actual IN (0,1)),
    FOREIGN KEY (id_disp) REFERENCES dispositiu(id_disp)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS historic (
    id_hist INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_usuari TEXT,
    id_disp INTEGER NOT NULL,
    valor_estat TEXT NOT NULL,
    data TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (nom_usuari) REFERENCES usuari(nom_usuari)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (id_disp) REFERENCES dispositiu(id_disp)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_historic_disp_data ON historic(id_disp, data);


/* TRIGGERS */

-- Limit de 5000 registres a l'historic (elimina el mes antic)
CREATE TRIGGER IF NOT EXISTS historic_limit
AFTER INSERT ON historic
WHEN (SELECT COUNT(*) FROM historic) > 5000
BEGIN
    DELETE FROM historic
    WHERE id_hist = (SELECT id_hist FROM historic ORDER BY data ASC LIMIT 1);
END;

-- Validacio de la identificacio de les subclases
CREATE TRIGGER IF NOT EXISTS identificacio_subclase_s
BEFORE INSERT ON sensor
WHEN NEW.id_disp NOT IN (SELECT id_disp FROM dispositiu)
BEGIN
    SELECT RAISE(ABORT, 'Aquest dispositiu no consta en la BD');
END;

CREATE TRIGGER IF NOT EXISTS identificacio_subclase_a
BEFORE INSERT ON actuador
WHEN NEW.id_disp NOT IN (SELECT id_disp FROM dispositiu)
BEGIN
    SELECT RAISE(ABORT, 'Aquest dispositiu no consta en la BD');
END;

-- Un historic ha d'apuntar a un dispositiu existent
CREATE TRIGGER IF NOT EXISTS historic_dispositiu_existeix
BEFORE INSERT ON historic
FOR EACH ROW
WHEN NEW.id_disp NOT IN (SELECT id_disp FROM dispositiu)
BEGIN
    SELECT RAISE(ABORT, 'Error: el dispositiu de l''historic no existeix.');
END;


/* VISTES */

-- L'admin veu qui ha fet cada canvi
CREATE VIEW IF NOT EXISTS historic_admin AS
    SELECT id_disp, nom_usuari, valor_estat, data
    FROM historic;

-- El viewer no veu el nom_usuari
CREATE VIEW IF NOT EXISTS historic_viewer AS
SELECT
    data,
    NULL AS nom_usuari,
    valor_estat,
    id_disp
FROM historic;
