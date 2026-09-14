# main.py
from pipeline import run_query # tum pipeline'i calistiran fonksiyonu import et.


def print_result(result):
    columns = result["columns"]
    rows = result["rows"]

    if not rows:
        print("(Sonuç bulunamadı)")
        return

    # Kolon başlıklarını yazdır
    print(" | ".join(columns))
    print("-" * (len(" | ".join(columns))))

    # Satırları yazdır
    for row in rows:
        print(" | ".join(str(value) for value in row))


def main():
    print("=== CNC Text-to-SQL Sistemi ===")
    print("Oturum baslatildi.")
    print("Sorunuzu Türkçe/İngilizce yazabilirsiniz. Cikmak için 'q' yaziniz.\n")

    while True: # sonsuz dongu, kullanici cikmak isteyene kadar devam et.
        question = input("Soru: ").strip()
        if question.lower() in ("q", "quit", "exit"):
            print("Oturum sonlandirildi!")
            break

        if not question: # kullanici bos soru gonderirse, tekrar sor.
            continue

        outcome = run_query(question)

        print(f"\n(Üretilen SQL - {outcome['attempts']}. denemede)")
        print(outcome["sql"])
        print()

        if outcome["success"]:
            # CANNOT_ANSWER sinyalini kontrol et
            if "CANNOT_ANSWER" in str(outcome["result"]["rows"]):
                print("Bu soruyu mevcut veritabanı ile cevaplayamıyorum.")
            else:
                print_result(outcome["result"])
        else:
            print(f"Sorgu {outcome['attempts']} denemede de başarısız oldu.")
            print(f"Son hata: {outcome['error']}")

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()