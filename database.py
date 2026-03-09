import json
import os
from pymongo import MongoClient
import certifi

# --- MONGODB BAĞLANTISI (GLOBAL) ---
CONNECTION_STRING = "mongodb+srv://beslerstokhyd_db_user:Hs19051905@cluster0.bjpaoen.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def get_db():
    """MongoDB veritabanı bağlantısını döner."""
    try:
        client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
        return client["SivasLojistikDB"]
    except Exception as e:
        print(f"⚠️ Veritabanı bağlantı hatası: {e}")
        return None

# Verilerin okunacağı ana yol (Yerel Yedekleme İçin)
DATA_PATH = "." 

def dosya_yolu(dosya_adi):
    return os.path.join(DATA_PATH, dosya_adi)

# --- YEREL JSON FONKSİYONLARI ---
def yukle(dosya_adi):
    """JSON dosyasını yükler, yoksa boş liste döner."""
    yol = dosya_yolu(dosya_adi)
    if not os.path.exists(yol):
        return []
    try:
        with open(yol, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def kaydet(dosya_adi, veri):
    """Veriyi JSON formatında yerel olarak kaydeder (Yedekleme)."""
    try:
        with open(dosya_yolu(dosya_adi), "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

# --- SABİT DOSYA VE KOLEKSİYON İSİMLERİ ---
# Hem JSON dosyaları hem de MongoDB tablo isimleri için ortak isimler
MAGAZALAR = "magazalar.json"
ADRESLER = "adresler.json"
RAPORLAR = "raporlar.json"
ARACLAR = "araclar.json"  # <--- BU MUTLAKA KALMALI
GIDERLER = "arac_giderleri.json"
PERSONEL = "personel.json"

# --- ÖRNEK KULLANIM ---
# db = get_db()
# if db:
#    db[ARACLAR.replace(".json","")].find() # MongoDB'den araçları çeker