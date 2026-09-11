# Ana amac: SQLite veritabanina baglanip tablolarin icine veri eklemek.
import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("cnc.db")
cursor = conn.cursor()

# Önce tabloları temizleyelim (script tekrar calistirilirsa eski veriler silinsin diye.)
cursor.executescript("""
DELETE FROM maintenance;
DELETE FROM downtime;
DELETE FROM production;
DELETE FROM machines;
""")

# --- 1. MACHINES ---

# python listesi
machines = [
    ("M01", "Haas VF-2", "Dikey İşleme Merkezi"),
    ("M02", "DMG Mori NLX 2500", "CNC Torna"),
    ("M03", "Mazak Integrex i-200", "Çoklu Eksen"),
    ("M04", "Haas ST-20", "CNC Torna"),
    ("M05", "Okuma Genos M560-V", "Dikey İşleme Merkezi"),
    ("M06", "Doosan Puma 2600", "CNC Torna"),
]
# VALUES(SQL) ile python tarafindaki verileri veritabanina eklemek icin executemany kullanilir.
cursor.executemany(
    "INSERT INTO machines (machine_id, machine_name, model) VALUES (?, ?, ?)",
    machines
)

machine_ids = [m[0] for m in machines] # machines'in 0. indislerini yani M01,M02... al.
part_names = ["Mil Kapağı", "Flanş", "Dişli Gövdesi", "Bağlantı Elemanı", "Pim", "Contalı Kapak"]
today = datetime.now()

def random_date_within(days_back):
    offset = random.randint(0, days_back) # 0 ile days_back arasında rastgele bir gun uretir.
    return (today - timedelta(days=offset)).strftime("%Y-%m-%d") # offset kadar gunluk zaman geriye gider ve YYYY.MM.DD formatina cevirir.

# --- 2. PRODUCTION (~60 kayıt, her makineden ~10) ---
random.seed(42)  # tekrar calistirinca aynı veriyi uretmesi icin (tutarlilik)
production_rows = [] 
for machine_id in machine_ids: # bu dongu 6 kere calisir.
    for _ in range(10): # her makine icin 10 kere calisir.
        part = random.choice(part_names) 
        quantity = random.randint(50, 500)
        prod_time = round(random.uniform(0.5, 8.0), 2)
        date = random_date_within(90)  # son 3 ay
        production_rows.append((machine_id, part, quantity, prod_time)) #  production_rows listesine ekliyoruz.

cursor.executemany(
    # az onceki liste veritabanındaki sutunlarina karsilik gelir.
    "INSERT INTO production (machine_id, part_name, quantity, production_time) VALUES (?, ?, ?, ?)",
    production_rows
)

# --- 3. DOWNTIME (~25 kayıt) ---
downtime_reasons = [
    "Elektrik arızası", "Alet aşınması", "Malzeme eksikliği",
    "Planlı bakım", "Operatör molası", "Yazılım/Kontrol hatası"
]
downtime_rows = []
for _ in range(25):
    machine_id = random.choice(machine_ids)
    reason = random.choice(downtime_reasons)
    duration = random.randint(15, 240)  # dakika
    date = random_date_within(90)       # son 3 ay arasi rastgele bir tarih olustur.
    downtime_rows.append((machine_id, reason, duration, date)) # downtime listesine ekle.

cursor.executemany(
    # DB'e ekle.
    "INSERT INTO downtime (machine_id, reason, duration, date) VALUES (?, ?, ?, ?)",
    downtime_rows
)

# --- 4. MAINTENANCE (~15 kayıt) ---
maintenance_types = ["Periyodik bakım", "Arıza sonrası bakım", "Önleyici bakım"]
maintenance_rows = []
for _ in range(15):
    machine_id = random.choice(machine_ids)
    m_type = random.choice(maintenance_types)
    date = random_date_within(90)
    maintenance_rows.append((machine_id, m_type, date))

cursor.executemany(
    "INSERT INTO maintenance (machine_id, maintenance_type, date) VALUES (?, ?, ?)",
    maintenance_rows
)

conn.commit()
conn.close()

print(f"Veri eklendi: {len(machines)} makine, {len(production_rows)} üretim, "
      f"{len(downtime_rows)} duruş, {len(maintenance_rows)} bakım kaydı başarıyla eklendi.")