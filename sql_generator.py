# SQL GENERATION
import re
from urllib import response
import ollama # pythondan ollama modelleri ile iliski kurmak icin
from schema_utils import get_schema_text # schema_utilsde yazilan fonk.nu import et.

MODEL_NAME = "qwen2.5-coder:7b"

# birlestir ve LLM'e gonderilecek olan promptu olustur.
def build_prompt(question, schema_text): #! question:kullanici sorusu ; schema_text: veritabani semasi
    return f"""You are an expert SQL generator. You write SQLite queries.

Database schema:
{schema_text}

Rules:
- Only output the SQL query, nothing else.
- Do not include explanations or markdown formatting.
- Use only the tables and columns listed above.
- The query must be a SELECT statement only.
- If the question cannot be answered using the schema above (e.g. it refers to data that does not exist in any table), respond with exactly: SELECT 'CANNOT_ANSWER' AS note;

Question: {question}

SQL:""" # simdi SQL sorgusunu yazmaya basla talimatini modele ver.

# promptu modele gonderir, ham metin cevabi dondurur 
def call_llm(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]
    # return response["message"]["content"]
    # response yapisi su sekildedir:
    # response = {
    #     "message": {
    #         "role": "assistant",
    #         "content": "SELECT * FROM machines;"
    #     },
    #}

# dogal dil -> SQL islemi gerceklestiren fonksiyon.
def generate_sql(question, db_path="cnc.db"):
    schema_text = get_schema_text(db_path)
    prompt = build_prompt(question, schema_text) # LLM'e gonderilecek promptu olustur.

    return call_llm(prompt)
   


# ```sql ... ``` veya ``` ... ``` bloklarını yakala
def clean_sql(raw_output): # raw_output: modelden gelen ham SQL cikti, parametre olarak ver.
    match = re.search(r"```(?:sql)?\s*(.*?)```", raw_output, re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        # Kod bloğu yoksa, direkt çıktının kendisini kullan
        sql = raw_output.strip()

    return sql


# bu dosya dogrudan calistirilirsa asagidaki kod blogu calisir. baska dosyadan import edilirse calismaz.
if __name__ == "__main__":
    question = "Son 30 günde en fazla duran makine hangisi?"
    raw_output = generate_sql(question)
    print("--- HAM MODEL ÇIKTISI ---")
    print(raw_output)

    cleaned = clean_sql(raw_output)
    print("\n--- TEMİZLENMİŞ SQL ---")
    print(cleaned)