import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Auto-Run Top 10 Parlay", page_icon="⚽", layout="centered")

st.title("⚽ AI Top 10 Auto Parlay Builder (2 Hari Kedepan)")
st.markdown("Aplikasi pintar dengan sistem **Multi-Key 5 Lapis Cadangan Otomatis** yang memindai jadwal pertandingan hingga 2 hari ke depan dan menyusun **Top 10 Legs** terbaik begitu halaman dibuka!")

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
    st.subheader("🏆 Rekomendasi Top 10 Parlay (2 Hari Kedepan)")
    
    with st.spinner("Sedang memindai seluruh jadwal bola untuk 2 hari ke depan dan menyaring 10 pertandingan terbaik..."):
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
            
            Tugasmu:
            Pilih tepat **10 pertandingan (Top 10 Legs)** yang paling "WORTH IT" dan memiliki probabilitas tembus tertinggi untuk dipasang dalam satu slip parlay besar.
            Sertakan informasi tanggal pertandingannya untuk setiap leg.
            Berikan rekomendasi pasaran spesifik (Over/Under atau Handicap) beserta alasannya.
            Format jawaban dengan rapi menggunakan Markdown.
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
                    break # Berhasil, keluar dari loop
                except Exception:
                    continue # Gagal/limit, lanjut ke key berikutnya secara otomatis
            
            if success:
                st.markdown(analysis_text)
                
                # --- KESIMPULAN TIKET TOP 10 PARLAY ---
                st.divider()
                st.markdown("### 🎫 KESIMPULAN TIKET TOP 10 PARLAY")
                st.success(f"✨ Selesai! Sistem telah menyaring 10 laga terbaik untuk periode {date_from} s/d {date_to}.")
                st.info("💡 **Tips:** Salin pilihan pasaran di atas ke bursa taruhanmu. Batasi dan pasang dengan bijak!")
            else:
                st.error("❌ Semua dari 5 API Key cadangan yang kamu masukkan telah mencapai batas kuota harian.")
else:
    st.error("❌ Konfigurasi API belum lengkap di Secrets.")
