import streamlit as st
from database import get_db
from datetime import datetime
import hashlib
import time

# Sayfa Ayarları (Mobil Uyumluluk İçin)
st.set_page_config(page_title="Sivas Lojistik Mobil", layout="centered", initial_sidebar_state="collapsed")

# --- CSS ile Mobil Görünümü Güzelleştirme ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #2e7d32; 
        color: white; 
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input { border-radius: 10px; }
    div.stInfo { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

# --- VERİTABANI BAĞLANTISI (GÜVENLİ MOD) ---
@st.cache_resource # Bağlantıyı bir kez kur ve sakla
def veritabani_baglan():
    try:
        db = get_db()
        if db is not None:
            return db
        return None
    except Exception as e:
        st.error(f"Bağlantı Kurulamadı: {e}")
        return None

db = veritabani_baglan()

if db is not None:
    col_seferler = db["Seferler"]
    col_kullanicilar = db["Kullanıcılar"]
else:
    st.error("⚠️ Veritabanı bağlantısı koptu. Lütfen sayfayı yenileyin.")
    st.stop() # Bağlantı yoksa çalışmayı durdur

st.title("🚚 Sivas Lojistik Mobil")

# --- GİRİŞ SİSTEMİ ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.subheader("Sürücü Girişi")
    with st.container():
        kullanici = st.text_input("Kullanıcı Adı (Plaka)", placeholder="Örn: 58ABC123").upper().strip()
        sifre = st.text_input("Şifre", type="password", placeholder="****")
        submit = st.button("Sisteme Giriş Yap")
        
        if submit:
            if kullanici and sifre:
                with st.spinner('Kontrol ediliyor...'):
                    # Şifreyi hashleyip MongoDB'de arıyoruz
                    user_data = col_kullanicilar.find_one({"ad": kullanici, "sifre": sifre_hashle(sifre)})
                    
                    if user_data:
                        st.session_state['logged_in'] = True
                        st.session_state['user'] = kullanici
                        st.rerun()
                    else:
                        st.error("❌ Hatalı plaka veya şifre!")
            else:
                st.warning("Lütfen tüm alanları doldurun.")
else:
    st.success(f"Hoş geldin, {st.session_state['user']}")
    
    # --- ŞOFÖRÜN BEKLEYEN SEFERLERİ ---
    # Sadece giriş yapan plakanın ve BEKLİYOR durumundaki seferini getir
    sefer = col_seferler.find_one({"plaka": st.session_state['user'], "durum": "BEKLİYOR"})
    
    if sefer:
        st.info(f"📍 **Aktif Sefer:** {sefer.get('sefer_id', 'Bilinmiyor')}")
        st.write(f"**Rota:** {sefer.get('rota_ozet', 'Belirtilmemiş')}")
        st.write(f"**Planlanan Mesafe:** {sefer.get('km', '0')} KM")
        
        st.divider()
        
        # KM Giriş Alanları
        cikis_km = st.number_input("Depo Çıkış KM", min_value=0, step=1, help="Aracın çıkış yaparkenki kilometresi")
        varis_km = st.number_input("Dönüş/Varış KM", min_value=0, step=1, help="Aracın dönüşteki kilometresi")
        
        if st.button("Seferi Tamamla ve Verileri Gönder"):
            if varis_km > cikis_km:
                fiili_km = varis_km - cikis_km
                try:
                    with st.spinner('Buluta kaydediliyor...'):
                        col_seferler.update_one(
                            {"sefer_id": sefer['sefer_id']},
                            {"$set": {
                                "durum": "TAMAMLANDI",
                                "depo_cikis_km": str(cikis_km),
                                "donus_km": str(varis_km),
                                "fiili_km": str(fiili_km),
                                "bitis_tarihi": datetime.now().strftime("%d/%m/%Y %H:%M")
                            }}
                        )
                        st.balloons()
                        st.success(f"✅ Sefer Kapatıldı! Kat edilen: {fiili_km} KM")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"Kayıt sırasında hata oluştu: {e}")
            else:
                st.warning("⚠️ Varış KM, Çıkış KM'den büyük olmalıdır!")
    else:
        st.warning("📭 Şu an üzerinize tanımlı aktif bir sefer bulunmuyor.")
        if st.button("Listeyi Yenile"):
            st.rerun()

    st.divider()
    if st.button("Güvenli Çıkış"):
        st.session_state['logged_in'] = False
        st.rerun()