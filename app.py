import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Auto-Run Top 5 Parlay", page_icon="⚽", layout="centered")

st.title("⚽ AI Top 5 Auto Parlay Builder")
st.markdown("Aplikasi pintar dengan sistem **Multi-Key Cadangan Otomatis** yang memindai jadwal hari ini dan menyusun **Top 5 Legs** terbaik begitu halaman dibuka!")

# 1. Konfigurasi Multi-API Keys dari Streamlit Secrets
try:
    # Mendukung banyak key sekaligus (pisahkan dengan koma atau buat beberapa key)
    api_keys = []
    if "GEMINI_API_KEY" in st.secrets:
        api_keys.append(st.secrets["GEMINI_API_KEY"])
    if "GEMINI_API_KEY_2" in st.secrets:
        api_keys.append(st.secrets["GEMINI_API_KEY_2"])
    if "GEMINI_API_KEY_3" in st.secrets:
        api_keys.append(st.secrets["GEMINI_API_KEY_3"])
        
    FOOTBALL_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
    api_ready = len(api_keys) > 0 and bool(FOOTBALL_KEY)
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ Konfigurasi API Key belum lengkap diatur di Streamlit Secrets!")

today_date = datetime.now().strftime("%Y-%m-%d")

# 2. Fungsi Mengambil Otomatis Jadwal Pertandingan Hari Ini
@st.cache_data(ttl=600)
def fetch_todays_matches(api_key):
    url = "https://api.football-data.org/v4/matches"
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

st.markdown(f"📅 **Jadwal Hari Ini:** `{today_date}`")
st.divider()

# 3. Proses Auto-Run dengan Sistem Cadangan API Key Otomatis
if api_ready:
    st.subheader("🏆 Rekomendasi Top 5 Parlay Hari Ini (Auto-Generated)")
    
    with st.spinner("Sedang memindai seluruh jadwal bola hari ini dan menyaring 5 pertandingan terbaik..."):
        raw_matches = fetch_todays_matches(FOOTBALL_KEY)
        
        if not raw_matches:
            st.warning("⚠️ Tidak ada jadwal pertandingan yang tersedia di server untuk hari ini.")
        else:
            all_available_matches = []
            for m in raw_matches:
                all_available_matches.append({
                    "home": m['homeTeam']['name'],
                    "away": m['awayTeam']['name'],
                    "competition": m['competition']['name']
                })
            
            selection_prompt = f"""
            Hari ini adalah tanggal {today_date}. Berikut adalah daftar pertandingan bola hari ini:
            {all_available_matches}
            
            Tugasmu:
            Pilih tepat **5 pertandingan (Top 5 Legs)** yang paling "WORTH IT" dan memiliki probabilitas tembus tertinggi untuk dipasang dalam satu slip parlay.
            Berikan rekomendasi pasaran spesifik (Over/Under atau Handicap) beserta alasannya.
            Format jawaban dengan rapi menggunakan Markdown.
            """
            
            # --- SISTEM PERCOBAAN OTOMATIS (FALLBACK KEY) ---
            success = False
            analysis_text = ""
            
            for idx, current_key in enumerate(api_keys):
                try:
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    response = model.generate_content(selection_prompt)
                    analysis_text = response.text
                    success = True
                    break # Berhasil, keluar dari perulangan key
                except Exception as e:
                    # Jika key ke-1 gagal/limit, otomatis lanjut mencoba key berikutnya
                    continue
            
            if success:
                st.markdown(analysis_text)
                
                # --- KESIMPULAN TIKET TOP 5 PARLAY ---
                st.divider()
                st.markdown("### 🎫 KESIMPULAN TIKET TOP 5 PARLAY HARI INI")
                st.success(f"✨ Selesai! Dari total seluruh pertandingan hari ini, sistem telah menyaring 5 laga terbaik per tanggal {today_date}.")
                st.info("💡 **Tips:** Salin pilihan pasaran di atas ke bursa taruhanmu. Batasi dan pasang dengan bijak!")
            else:
                st.error("❌ Semua API Key cadangan yang kamu masukkan telah mencapai batas kuota harian. Silakan tambahkan Key baru.")
else:
    st.error("❌ Konfigurasi API belum lengkap di Secrets.")
