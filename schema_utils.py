# Ana amac : SQLite veritabaninin yapisini otomatik olarak okuyup LLM'in anlayabilecegi duz metne cevirmek

import sqlite3 # SQLite

def get_schema_text(db_path="cnc.db"): # veritabaninin yolunu parametre olarak ver. 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Veritabanındaki tüm tablo isimlerini çek (sqlite_ ile başlayan sistem tablolarını hariç tut)
    # SQLite'da tablo isimlerini almak için sqlite_master tablosunu sorgularız.Bu tablo; tablo isimlerini,kolonlari sorgulayabilecegimiz ozel bir tablodur.
    # SELECT name ile tablo isimlerini al.
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    table_names = [row[0] for row in cursor.fetchall()] # butun tablo isimlerini listeye al

    schema_lines = []
    for table in table_names: # tablolari tek tek gez.
        # Her tablonun kolon bilgisini çek (PRAGMA table_info sqlite'ın özel komutu)
        cursor.execute(f"PRAGMA table_info({table})") # PRAGMA table_info komutu(SQLite ozel komutudur), bir tablonun kolon bilgilerini döndürür. Bu bilgiler; kolon adı, veri tipi, null olup olmadığı, varsayılan değer ve birincil anahtar olup olmadığı gibi bilgileri içerir.
        columns = cursor.fetchall() # PRAGMA sorgusunun sonucunu al.
        # columns: (cid, name, type, notnull, default, pk)
        col_descriptions = [f"{col[1]} ({col[2]})" for col in columns]

        # o tabloya ait bilgiyi tek bir metin haline getir.
        schema_lines.append(f"Table: {table}\nColumns: {', '.join(col_descriptions)}") 
        # "Table: machines
        # Columns: machine_id (TEXT), machine_name (TEXT), model (TEXT)"

    conn.close()
    return "\n\n".join(schema_lines) # schema_lines' da her tablo icin bir string var.

# ciktiyi olustur ve de yazdir.
if __name__ == "__main__":
    print(get_schema_text())