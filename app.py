import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Multi-Bill Parlay Builder", page_icon="⚽", layout="centered")

st.title("⚽ AI Multi-Bill Auto Parlay Builder (2 Hari Kedepan)")
st.markdown("Aplikasi pintar dengan sistem **5 Lapis API Key Cadangan** yang membagi rekomendasi menjadi **Bill Utama, Backup, dan High Risk** otomatis begitu halaman dibuka!")

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

# 2. Fungsi Mengambil Jadwal Pertandingan (Rentang 3 Hari: Hari Ini + 2 Hari Kedepan)
@st.cache_data(ttl=600)
def fetch_matches_range(api_key, d_from, d_to):
    url = f"https://api.football-data.org/v4/matches?dateFrom={d_from}&dateTo={d_to}"
    headers = {"X-Auth-Token": api_key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("matches", [])
        else:
            return []
    except Exception:
        return []

st.markdown(f"📅 **Rentang Jadwal:** `{date_from}` s/d `{date_to}`")
st.divider()

# 3. Proses Auto-Run dengan Sistem Cadangan 5 API Key Otomatis
if api_ready:
    st.subheader("🏆 Analisis 3 Kategori Bill (Utama, Backup, High Risk)")
    
    with st.spinner("Sedang memindai jadwal bola dan meracik strategi 3 jenis Bill..."):
        raw_matches = fetch_matches_range(FOOTBALL_KEY, date_from, date_to)
        
        if not raw_matches:
            st.warning("⚠️ Tidak ada jadwal pertandingan yang tersedia di server untuk rentang tanggal tersebut.")
        else:
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
            Berikut adalah daftar pertandingan bola dari tanggal {date_from} sampai {date_to}:
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
            
            # --- SISTEM PERCOBAAN OTOMATIS BERUNTUN (5 KEY CADANGAN) ---
            success = False
            analysis_text = ""
            
            for current_key in api_keys:
                try:
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    response = model.generate_content(selection_prompt)
                    analysis_text = response.text
                    success = True
                    break 
                except Exception:
                    continue 
            
            if success:
                st.markdown(analysis_text)
                
                # --- KESIMPULAN TIKET MULTI-BILL ---
                st.divider()
                st.markdown("### 🎫 RINGKASAN STRATEGI 3 BILL")
                st.success(f"✨ Selesai! Strategi Bill Utama, Backup, dan High Risk untuk periode {date_from} s/d {date_to} berhasil disusun.")
                st.info("💡 **Tips:** Pasang Bill Utama dengan nominal ideal, Bill Backup dengan nominal sedang, dan Bill High Risk secukupnya saja!")
            else:
                st.error("❌ Semua dari 5 API Key cadangan yang kamu masukkan telah mencapai batas kuota harian.")
else:
    st.error("❌ Konfigurasi API belum lengkap di Secrets.")
