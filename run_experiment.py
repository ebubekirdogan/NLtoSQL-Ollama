# Amac: Zero-shot ve few-shot stratejilerini kullanarak 14 soruluk test setinde calistirip CSV'ye kaydetmek.
import csv #csv dosyası olusturmak icin.
from pipeline import run_query # soruyu LLM'e gonderip SQL uretmek, SQL'i calistirip sonucu almak icin run_query fonksiyonunu import et.
from db_executor import execute_sql # SQL sorgularini dogrudan veritabaninda calistirmak icin
from test_questions import TEST_QUESTIONS

STRATEGIES = ["zero_shot", "few_shot"]
OUTPUT_FILE = "experiment_results.csv"

# Referans SQL'i calistirip gercek sonucu dondurur. None ise (cevaplanamaz soru) None doner.

def get_reference_result(reference_sql, db_path="cnc.db"):
    if reference_sql is None:
        return None
    try:
        result = execute_sql(reference_sql, db_path)
        return result["rows"] # SQL sorgusunun sonucunu dondur.
    except Exception as e: # SQL calisirken hata olursa burasi calisir.
        print(f"UYARI: Referans SQL calismadi - {e}")
        return None


#     Model sonucu ile referans sonucu esit mi, basit karsilastirma.
def flatten_rows(rows):
    values = set()
    for row in rows:
        for v in row: # satirin icindeki her bir degeri tek tek al.
            if isinstance(v, float): # ayni veri tipindeler mi diye bakar.
                values.add(round(v, 2)) # oyleyse virgulden sonra 2 basamak olacak sekilde ekle.
            else:
                values.add(v) # degilse oldugu gibi ekle.
    return values


def rows_match(model_rows, reference_rows):
    if reference_rows is None:
        return None

    reference_flat = flatten_rows(reference_rows)
    model_flat = flatten_rows(model_rows)

    if not reference_flat:
        return None

    return len(reference_flat & model_flat) > 0 # karsilastirma yapar, kesişim varsa True yoksa False dondurur.

# Tüm deneyin calistirilacagi ana fonksiyon.
def run_experiment():
    results = [] # deney sonuclarini burada tutacagiz.

    for item in TEST_QUESTIONS: # tum sorulari tek tek dene.
        for strategy in STRATEGIES: # her soru icin iki stratejiyi de dene.
            print(f"[{item['id']}] ({strategy}) {item['question']}")

            outcome = run_query(item["question"], strategy=strategy)

            row = { # deneyin sonucunu tutacak bir sozluk olustur.
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "strategy": strategy,
                "success": outcome["success"],
                "attempts": outcome["attempts"],
                "generated_sql": outcome.get("sql", ""),
                "is_cannot_answer": False,
                "correct": None,
            }

            if outcome["success"]: # SQL basarili ise;
                model_rows = outcome["result"]["rows"] # modelin SQL'den cikan sonucunu al.
                # CANNOT_ANSWER sinyalini kontrol et
                if "CANNOT_ANSWER" in str(model_rows):
                    row["is_cannot_answer"] = True
                    # dogru davranis mi? referans SQL None ise (gercekten cevaplanamaz soru) dogru
                    row["correct"] = (item["reference_sql"] is None)
                else:
                    reference_rows = get_reference_result(item["reference_sql"])
                    if item["reference_sql"] is None:
                        # cevaplanamaz soruydu ama model bir sonuc uretti -> YANLIS (sessiz hata)
                        row["correct"] = False
                    else:
                        row["correct"] = rows_match(model_rows, reference_rows) # cevaplanabilir bir soruysa karsilastir.(rows_match)
            else:
                row["correct"] = False # SQL basarisiz ise yanlis kabul et.

            results.append(row) # hazirlanilan deney sonucunu(row) result listesine ekle.

    # CSV'ye yaz
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f: # csv dosyasini yazmak modunda ac. acilan dosyayi f ye ata.
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSonuçlar kaydedildi: {OUTPUT_FILE}")
    return results


if __name__ == "__main__":
    run_experiment()