# DB olusturma.
import sqlite3 #SQLite kutuphanesi

conn = sqlite3.connect("cnc.db") # SQLite veritabanina baglan ve cnc.db dosyasini olustur.
cursor = conn.cursor()           # cursor ; SQL sorgulari gonderme araci.

# Tabloları oluştur ( birden fazla SQL sorgusunu tek seferde calistirmak icin executescript kullanilir.)
cursor.executescript("""        
CREATE TABLE IF NOT EXISTS machines (
    machine_id TEXT PRIMARY KEY,
    machine_name TEXT NOT NULL,
    model TEXT
);

CREATE TABLE IF NOT EXISTS production (
    production_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    part_name TEXT,
    quantity INTEGER,
    production_time REAL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS downtime (
    downtime_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    reason TEXT,
    duration REAL,
    date TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    maintenance_type TEXT,
    date TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);
""")

conn.commit() # yapilan degisiklikleri veritabanina kaydet
conn.close()  # veritabani baglantisini kapat
print("Veritabani ve tablolar olusturuldu: cnc.db")