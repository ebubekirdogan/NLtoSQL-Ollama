import ollama

response = ollama.chat(      # terminalden yaptigimiz konusma islemini  Python'dan otomatik olarak yapiyor. Ollama'ya arka plandan bir istek atar.
    model="qwen2.5-coder:7b",
    # bir liste ile modele gonderilecek mesajlar belirlenir.
    # role: user -> kullanicidan gelen mesaj oldugunu modele bildirir.
    # content: user -> kullanicidan gelen mesajin icerigini belirler.
    messages=[
        {"role": "user", "content": "Write a SQL query to select all rows from a table called machines."}
    ]
)
# response message ile modelin mesaj kismina gidilir ve de content ile modelin urettigi "ham cikti" alinir.
print(response["message"]["content"])  