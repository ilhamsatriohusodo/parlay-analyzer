import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Top 5 Auto Parlay Builder", page_icon="⚽", layout="centered")

st.title("⚽ AI Top 5 Auto Parlay Builder")
st.markdown("Aplikasi pintar yang otomatis memindai seluruh jadwal hari ini, menyaring, dan memilih **5 pertandingan terbaik (Top 5 Legs)** dengan probabilitas menang tertinggi untuk *bill parlay*.")

# 1. Konfigurasi API Keys dari Streamlit Secrets
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    api_ready = True
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ GEMINI_API_KEY atau FOOTBALL_DATA_API_KEY belum lengkap diatur di Streamlit Secrets!")

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

# Tombol Utama untuk Generate Top 5 Parlay
st.markdown(f"📅 **Jadwal Hari Ini:** `{today_date}`")
if st.button("🚀 Pilih & Analisa Top 5 Matches untuk Parlay", type="primary"):
    if not api_ready:
        st.error("❌ Konfigurasi API belum lengkap.")
    else:
        with st.spinner("Sedang memindai seluruh laga hari ini dan menyaring 5 pertandingan paling layak pasang..."):
            raw_matches = fetch_todays_matches(FOOTBALL_KEY)
            
            if not raw_matches:
                st.warning("⚠️ Tidak ada jadwal pertandingan yang tersedia di server untuk hari ini.")
            else:
                # Kumpulkan semua daftar tim yang bertanding hari ini
                all_available_matches = []
                for m in raw_matches:
                    all_available_matches.append({
                        "home": m['homeTeam']['name'],
                        "away": m['awayTeam']['name'],
                        "competition": m['competition']['name']
                    })
                
                st.divider()
                st.subheader("🏆 Proses Penyaringan & Analisa Top 5 Legs")
                
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Kirim daftar semua pertandingan ke AI, lalu minta AI memilih 5 terbaik
                    selection_prompt = f"""
                    Hari ini adalah tanggal {today_date}. Berikut adalah daftar pertandingan bola hari ini:
                    {all_available_matches}
                    
                    Tugasmu:
                    Pilih tepat **5 pertandingan (Top 5 Legs)** yang paling "WORTH IT" dan memiliki probabilitas tembus tertinggi untuk dipasang dalam satu slip parlay (hindari laga yang terlalu berisiko atau seimbang ketat).
                    
                    Untuk masing-masing dari 5 pertandingan pilihanmu, berikan:
                    1. Nama Tim Home dan Away serta Kompetisinya.
                    2. Alasan singkat mengapa laga ini dipilih (xG, tren performa, keamanan).
                    3. Rekomendasi pasaran spesifik yang paling aman (Contoh: Over 1.5, Double Chance 1X, atau Handicap aman).
                    
                    Format jawaban dengan rapi. Di bagian paling akhir, buatkan ringkasan tiket dalam format khusus agar mudah dibaca sistem dengan awalan: "TOP_5_SUMMARY:" diikuti daftar 5 leg tersebut.
                    """
                    
                    response = model.generate_content(selection_prompt)
                    analysis_text = response.text
                    
                    # Tampilkan hasil analisis lengkap AI
                    st.markdown(analysis_text)
                    
                    # --- KESIMPULAN TIKET TOP 5 PARLAY ---
                    st.divider()
                    st.markdown("### 🎫 KESIMPULAN TIKET TOP 5 PARLAY HARI INI")
                    st.success(f"✨ Selesai! Dari total seluruh pertandingan hari ini, sistem telah menyaring 5 laga terbaik per tanggal {today_date}.")
                    st.info("💡 **Tips:** Salin pilihan pasaran di atas ke bursa taruhanmu. Batasi dan pasang dengan bijak!")
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses data otomatis: {e}")
