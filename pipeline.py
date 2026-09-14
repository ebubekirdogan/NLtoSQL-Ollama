# SELF CORRECTION DONGUSU
from schema_utils import get_schema_text # DB yapısının metinsel temsilini almak için fonksiyonu import et.
from sql_generator import build_prompt, call_llm, clean_sql # DB yapısına ve kullanıcı sorusuna göre SQL sorgusu üretmek için gerekli fonksiyonları import et.
from db_executor import execute_sql # SQL sorgusu guvenliğini kontrol ederek çalıştırmak için fonksiyonu import et.
from sql_generator import build_prompt, build_few_shot_prompt, call_llm, clean_sql
# Hatalı SQL + hata mesajını modele geri gönderecek düzeltme prompt'u.
def build_correction_prompt(question, schema_text, previous_sql, error_message):
    return f"""You are an expert SQL generator. You write SQLite queries.

Database schema:
{schema_text}

You previously generated this SQL for the question below, but it failed.

Question: {question}

Previous SQL:
{previous_sql}

Error message:
{error_message}

Please fix the SQL query. Only output the corrected SQL, nothing else.
No explanations, no markdown formatting. The query must be a SELECT statement only.

Corrected SQL:"""

# Kullanici sorusunu SQL'e cevir, SQL'i calistir ve sonucu dondur. Hata olursa hatayi modele geri gondererek SQL'i duzeltmeye calis.
def run_query(question, db_path="cnc.db", max_attempts=3, strategy="zero_shot"):
    schema_text = get_schema_text(db_path)
    sql = None
    error_message = None

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            if strategy == "few_shot":
                prompt = build_few_shot_prompt(question, schema_text)
            else:
                prompt = build_prompt(question, schema_text)
        else: # ilk deneme degilse 
            prompt = build_correction_prompt(question, schema_text, sql, error_message)

        raw_output = call_llm(prompt)
        sql = clean_sql(raw_output)

        try:
            result = execute_sql(sql, db_path)
            return {"success": True, "sql": sql, "result": result, "attempts": attempt}
        except Exception as e:
            error_message = str(e)
            print(f"[Deneme {attempt}] Hata: {error_message}")

    return {"success": False, "sql": sql, "error": error_message, "attempts": max_attempts}


# Hızlı test
if __name__ == "__main__":
    question = "Sensör verilerine göre hangi makinenin titreşim değeri en yüksek?"
    outcome = run_query(question)

    print("\n--- SONUÇ ---")
    if outcome["success"]:
        print(f"Başarılı ({outcome['attempts']}. denemede)")
        print("SQL:", outcome["sql"])
        print("Sonuç:", outcome["result"])
    else:
        print(f"Başarısız ({outcome['attempts']} denemeden sonra)")
        print("Son hata:", outcome["error"])