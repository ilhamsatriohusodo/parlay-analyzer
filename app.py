import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Multi-Bill Parlay Builder", page_icon="⚽", layout="centered")

st.title("⚽ AI Multi-Bill Auto Parlay Builder (2 Hari Kedepan)")
st.markdown("Aplikasi pintar dengan sistem **Cache Harian (1x Generate per Hari)**, **5 Lapis API Key Cadangan**, dan pembagian **3 Kategori Bill** otomatis!")

# 1. Konfigurasi 5 API Keys Cadangan dari Streamlit Secrets
try:
    api_keys = []
    for key_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4", "GEMINI_API_KEY_5"]:
        if key_name in st.secrets:
            api_keys.append(st.secrets[key_name])
        
    FOOTBALL_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
    api_ready = len(api_keys) > 0 and bool(FOOTBALL_KEY)
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ Konfigurasi API Key belum lengkap diatur di Streamlit Secrets!")

# Rentang Waktu: Hari Ini sampai 2 Hari Kedepan
today = datetime.now()
date_from = today.strftime("%Y-%m-%d")
date_to = (today + timedelta(days=2)).strftime("%Y-%m-%d")

# 2. Fungsi Utama dengan Cache Harian (ttl = 86400 detik / 24 jam)
# AI hanya akan bekerja 1x sehari untuk tanggal yang sama. Buka pagi atau sore hasilnya tetap sama & instan!
@st.cache_data(ttl=86400)
def get_daily_parlay_analysis(d_from, d_to, api_keys_tuple, football_api_key):
    # Ambil jadwal dari API Football
    url = f"https://api.football-data.org/v4/matches?dateFrom={d_from}&dateTo={d_to}"
    headers = {"X-Auth-Token": football_api_key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            raw_matches = response.json().get("matches", [])
        else:
            raw_matches = []
    except Exception:
        raw_matches = []
        
    if not raw_matches:
        return "EMPTY_MATCHES"
        
    all_available_matches = []
    for m in raw_matches:
        match_date = m['utcDate'][:10]
        all_available_matches.append({
            "date": match_date,
            "home": m['homeTeam']['name'],
            "away": m['awayTeam']['name'],
            "competition": m['competition']['name']
        })
        
    selection_prompt = f"""
    Berikut adalah daftar pertandingan bola dari tanggal {d_from} sampai {d_to}:
    {all_available_matches}
    
    Tugasmu adalah memilih dan membagi pertandingan ke dalam **3 Kategori Bill Terpisah** (Total mencakup sekitar 10 pertandingan terbaik secara keseluruhan):
    
    1. **### 🎯 BILL 1: UTAMA (Aman & Stabil)**
       - Pilih 3-4 pertandingan dengan probabilitas tembus paling tinggi.
       - Gunakan pasaran yang sangat konservatif (Contoh: Double Chance 1X/2X, Over 1.5, atau Handicap tipis yang sangat aman).
    
    2. **### 🛡️ BILL 2: BACKUP (Alternatif Solid)**
       - Pilih 3-4 pertandingan sebagai tiket cadangan yang seimbang secara statistik performa tim.
    
    3. **### 🔥 BILL 3: HIGH RISK (Berani Ambil Risiko / Cuan Besar)**
       - Pilih 2-3 pertandingan dengan potensi odds tinggi atau risiko lebih menantang (Contoh: Over 2.5, Handicap penuh, atau Moneyline murni).
    
    Sertakan tanggal pertandingan, nama tim, kompetisi, pasaran spesifik, serta alasan singkat untuk setiap leg. Format dengan rapi menggunakan Markdown.
    """
    
    # Sistem percobaan otomatis beruntun (5 Key Cadangan)
    for current_key in api_keys_tuple:
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            response = model.generate_content(selection_prompt)
            return response.text
        except Exception:
            continue 
            
    return "ERROR_QUOTA_EXCEEDED"

st.markdown(f"📅 **Rentang Jadwal:** `{date_from}` s/d `{date_to}`")
st.divider()

# 3. Tampilan Antarmuka
if api_ready:
    st.subheader("🏆 Rekomendasi 3 Kategori Bill (Utama, Backup, High Risk)")
    
    # Spinner hanya muncul sekali saat pertama kali dibuka hari ini
    with st.spinner("Memuat data harian... (Jika baru pertama kali dibuka hari ini, AI meracik strategi. Kunjungan berikutnya hari ini akan instan!)"):
        result_text = get_daily_parlay_analysis(date_from, date_to, tuple(api_keys), FOOTBALL_KEY)
        
    if result_text == "EMPTY_MATCHES":
        st.warning("⚠️ Tidak ada jadwal pertandingan yang tersedia di server untuk rentang tanggal tersebut.")
    elif result_text == "ERROR_QUOTA_EXCEEDED":
        st.error("❌ Semua dari 5 API Key cadangan yang kamu masukkan telah mencapai batas kuota harian.")
    else:
        st.markdown(result_text)
        
        # --- KESIMPULAN TIKET MULTI-BILL ---
        st.divider()
        st.markdown("### 🎫 KESIMPULAN STRATEGI 3 BILL")
        st.success(f"✨ Berhasil! Hasil analisis harian untuk periode {date_from} s/d {date_to} tersimpan otomatis di cache.")
        st.info("💡 **Tips:** Kamu bisa buka web ini kapan pun hari ini (pagi, siang, atau sore), tampilannya akan langsung muncul tanpa *loading* dan hemat kuota API!")
else:
    st.error("❌ Konfigurasi API belum lengkap di Secrets.")
