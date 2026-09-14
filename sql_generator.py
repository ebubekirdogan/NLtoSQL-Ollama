# SQL GENERATION
import re
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

SQL:"""


# Few-shot icin kullanilacak sabit ornekler (! test setindeki sorularla farkli sorular)
FEW_SHOT_EXAMPLES = [
    {
        "question": "Kaç adet duruş kaydı var?",
        "sql": "SELECT COUNT(*) FROM downtime;"
    },
    {
        "question": "En çok üretim yapılan parça hangisi?",
        "sql": "SELECT part_name, SUM(quantity) as total FROM production GROUP BY part_name ORDER BY total DESC LIMIT 1;"
    },
    {
        "question": "Hangi makinenin bakım sayısı en fazla?",
        "sql": "SELECT m.machine_name FROM machines m JOIN maintenance mt ON m.machine_id = mt.machine_id GROUP BY m.machine_id, m.machine_name ORDER BY COUNT(*) DESC LIMIT 1;"
    },
]

# few-shot promptu olustur.
def build_few_shot_prompt(question, schema_text):
    examples_text = ""
    for ex in FEW_SHOT_EXAMPLES:
        examples_text += f"Question: {ex['question']}\nSQL: {ex['sql']}\n\n"

    return f"""You are an expert SQL generator. You write SQLite queries.

Database schema:
{schema_text}

Rules:
- Only output the SQL query, nothing else.
- Do not include explanations or markdown formatting.
- Use only the tables and columns listed above.
- The query must be a SELECT statement only.
- If the question cannot be answered using the schema above (e.g. it refers to data that does not exist in any table), respond with exactly: SELECT 'CANNOT_ANSWER' AS note;

Here are some examples:

{examples_text}Now answer this question:

Question: {question}

SQL:"""


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