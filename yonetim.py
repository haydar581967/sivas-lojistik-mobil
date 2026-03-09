import streamlit as st
from database import get_db
import pandas as pd

# YÖNETİCİ PANELİNİ ZORLA AÇAN KOD
st.set_page_config(page_title="Sivas Lojistik YÖNETİM", layout="wide")

db = get_db()
col_kullanicilar = db["Kullanıcılar"]
col_seferler = db["Seferler"]
col_araclar = db["Araclar"]

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🏗️ YÖNETİCİ GİRİŞİ")
    kullanici = st.text_input("Kullanıcı Adı").upper().strip()
    if st.button("SİSTEMİ AÇ"):
        if kullanici == "HYDSNL":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Sadece HYDSNL girebilir.")
else:
    st.header("👑 SÜPER YÖNETİCİ PANELİ")
    tab1, tab2 = st.tabs(["📍 Sefer Ata", "📋 Kayıtlar"])
    with tab1:
        st.subheader("Yeni Görev Tanımla")
        soforler = [u["ad"] for u in col_kullanicilar.find()]
        st.selectbox("Şoför Seç", soforler)
        st.button("Seferi Onayla")
    with tab2:
        df = pd.DataFrame(list(col_seferler.find().limit(20)))
        if not df.empty: st.dataframe(df.drop(columns=['_id']))
    
    if st.sidebar.button("Çıkış"):
        st.session_state.clear()
        st.rerun()
