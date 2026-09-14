# Her soru için: kategori, doğal dil sorusu, ve referans (doğru kabul edilen) SQL.
# Cevaplanamaz sorularda reference_sql = None -> beklenen davranış CANNOT_ANSWER.

TEST_QUESTIONS = [
    # --- BASİT ---
    {
        "id": 1,
        "category": "basit",
        "question": "Kaç makine var?",
        "reference_sql": "SELECT COUNT(*) FROM machines;"
    },
    {
        "id": 2,
        "category": "basit",
        "question": "Tüm makinelerin isimlerini listele.",
        "reference_sql": "SELECT machine_name FROM machines;"
    },
    {
        "id": 3,
        "category": "basit",
        "question": "M03 makinesinin modeli nedir?",
        "reference_sql": "SELECT model FROM machines WHERE machine_id = 'M03';"
    },

    # --- ORTA (tek tablo + agregasyon/filtre) ---
    {
        "id": 4,
        "category": "orta",
        "question": "Toplam kaç duruş kaydı var?",
        "reference_sql": "SELECT COUNT(*) FROM downtime;"
    },
    {
        "id": 5,
        "category": "orta",
        "question": "En sık görülen duruş sebebi nedir?",
        "reference_sql": "SELECT reason, COUNT(*) as cnt FROM downtime GROUP BY reason ORDER BY cnt DESC LIMIT 1;"
    },
    {
        "id": 6,
        "category": "orta",
        "question": "Ortalama üretim süresi nedir?",
        "reference_sql": "SELECT AVG(production_time) FROM production;"
    },

    # --- JOIN GEREKTİREN ---
    {
        "id": 7,
        "category": "join",
        "question": "En fazla duran makinenin adı nedir?",
        "reference_sql": """SELECT m.machine_name FROM machines m
                             JOIN downtime d ON m.machine_id = d.machine_id
                             GROUP BY m.machine_id, m.machine_name
                             ORDER BY SUM(d.duration) DESC LIMIT 1;"""
    },
    {
        "id": 8,
        "category": "join",
        "question": "Hangi makinenin toplam üretim miktarı en yüksek?",
        "reference_sql": """SELECT m.machine_name FROM machines m
                             JOIN production p ON m.machine_id = p.machine_id
                             GROUP BY m.machine_id, m.machine_name
                             ORDER BY SUM(p.quantity) DESC LIMIT 1;"""
    },
    {
        "id": 9,
        "category": "join",
        "question": "En az bakım yapılan makinenin adı ve modeli nedir?",
        "reference_sql": """SELECT m.machine_name, m.model FROM machines m
                             JOIN maintenance mt ON m.machine_id = mt.machine_id
                             GROUP BY m.machine_id, m.machine_name, m.model
                             ORDER BY COUNT(*) ASC LIMIT 1;"""
    },

    # --- TARİH FİLTRELİ ---
    {
        "id": 10,
        "category": "tarih",
        "question": "Son 30 günde en fazla duran makine hangisi?",
        "reference_sql": """SELECT machine_id FROM downtime
                             WHERE date >= DATE('now', '-30 days')
                             GROUP BY machine_id ORDER BY SUM(duration) DESC LIMIT 1;"""
    },
    {
        "id": 11,
        "category": "tarih",
        "question": "Son 60 günde kaç bakım yapıldı?",
        "reference_sql": "SELECT COUNT(*) FROM maintenance WHERE date >= DATE('now', '-60 days');"
    },

    # --- CEVAPLANAMAZ (şemada karşılığı olmayan sorular) ---
    {
        "id": 12,
        "category": "cevaplanamaz",
        "question": "Hangi makinenin elektrik tüketimi en yüksek?",
        "reference_sql": None
    },
    {
        "id": 13,
        "category": "cevaplanamaz",
        "question": "Sensör verilerine göre hangi makinenin titreşim değeri en yüksek?",
        "reference_sql": None
    },
    {
        "id": 14,
        "category": "cevaplanamaz",
        "question": "Hangi operatör en çok üretim yapmış?",
        "reference_sql": None  
    },
]