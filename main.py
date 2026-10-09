import os
import pandas as pd
from apify_client import ApifyClient
import google.generativeai as genai

# 1. Inisialisasi API Key dari Secrets
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

apify_client = ApifyClient(APIFY_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# 2. Ambil Komentar dari Instagram via Apify
run_input = {
    "directUrls": [
        "https://www.instagram.com/p/C_example_krakatau/"  # Ganti dengan link postingan IG target
    ],
    "resultsLimit": 8
}

print("Sedang mengambil komentar Instagram dari Apify...")
run = apify_client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
dataset_items = apify_client.dataset(run["defaultDatasetId"]).list_items().items

# 3. Analisis Sentimen Komentar Menggunakan Gemini AI
model = genai.GenerativeModel('gemini-2.5-flash')

results = []
print("Sedang menganalisis sentimen komentar dengan Gemini AI...")

for idx, item in enumerate(dataset_items[:8], start=1):
    comment_text = item.get("text", "")
    owner_username = item.get("ownerUsername", "Anonim")
    post_url = item.get("postUrl", "https://www.instagram.com")
    
    prompt = f"""
    Analisis komentar masyarakat berikut mengenai erupsi/abu vulkanik Anak Krakatau di Instagram.
    Tentukan sentimennya secara objektif: 'Positif', 'Negatif', atau 'Netral'.
    Berikan respons hanya berupa SATU KATA label sentimen saja.
    
    Komentar: "{comment_text}"
    """
    
    try:
        response = model.generate_content(prompt)
        sentiment_label = response.text.strip()
    except Exception as e:
        sentiment_label = "Error"
    
    results.append({
        "No": idx,
        "Username": owner_username,
        "Komentar": comment_text,
        "Link Sosmed (IG)": post_url,
        "Sentimen": sentiment_label
    })

# 4. Simpan ke File CSV
df = pd.DataFrame(results)
df.to_csv("hasil_sentimen.csv", index=False)
print("Selesai! Hasil komentar IG dan sentimen berhasil disimpan ke hasil_sentimen.csv")
