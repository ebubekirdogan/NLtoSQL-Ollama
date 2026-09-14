import sqlite3

class UnsafeQueryError(Exception):
    """Sorgu SELECT disinda bir işlem içeriyorsa firlatilir."""
    pass

# Sorgunun sadece SELECT oldugunu kontrol et.
def is_safe_select(sql):
    normalized = sql.strip().lower() # strip basindaki ve sondaki bosluklari kaldir, lower ile kucuk harfe cevir.
    if not normalized.startswith("select"): #startswith ile sorgunun SELECT ile baslayip baslamadigini kontrol et.
        return False

    # Tehlikeli anahtar kelimeler sorgunun içinde geçmesin
    forbidden_keywords = ["delete", "drop", "update", "insert", "alter", "truncate", "attach"]
    for keyword in forbidden_keywords:
        if keyword in normalized:
            return False

    return True


def execute_sql(sql, db_path="cnc.db"): # calistirilacak SQL sorgusu ve veritabani yolu parametre olarak alinir.
    if not is_safe_select(sql):
        raise UnsafeQueryError(f"Sadece SELECT sorgularina izin veriliyor. Alinan: {sql}") # raise ile program hata ile durdurur ve hata mesaji firlatir.

    conn = sqlite3.connect(db_path) # DB bagla.
    cursor = conn.cursor()          # Cursor olustur.(SQL sorgularini DB gondermek icin.)

    # SQL basarili ise try ve finally calisir. SQL basarisiz ise try blogu  hata firlatilir, finally blogu calisir.
    try:
        cursor.execute(sql) # sql sorgusunu cnc.db uzerinde calistir.
        columns = [description[0] for description in cursor.description] # kolon isimlerini alir.
        rows = cursor.fetchall() # fetchall; SQL sorgusunun sondurdugu butun satirlari alir. 
        return {"columns": columns, "rows": rows}
    finally:
        conn.close()


# Hızlı test
if __name__ == "__main__":
    test_sql = "SELECT machine_id, machine_name FROM machines LIMIT 3;"
    result = execute_sql(test_sql)
    print("Kolonlar:", result["columns"])
    print("Satırlar:", result["rows"])