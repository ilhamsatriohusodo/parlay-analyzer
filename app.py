import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live API Parlay Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live API Parlay Analyzer")
st.markdown("Pilih langsung pertandingan hari ini yang ditarik secara otomatis dari **server data sepak bola resmi**, lalu biarkan AI menganalisisnya secara mendalam!")

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

# 2. Fungsi Mengambil Jadwal Pertandingan Hari Ini dari API Resmi
@st.cache_data(ttl=600) # Cache data selama 10 menit agar tidak boros request
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

st.subheader("📅 Pilih Pertandingan Hari Ini")

matches_list = []
if api_ready:
    with st.spinner("Sedang memuat daftar pertandingan live dari server resmi..."):
        raw_matches = fetch_todays_matches(FOOTBALL_KEY)
        
        if raw_matches:
            # Filter atau format data pertandingan
            match_options = {}
            for m in raw_matches:
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                competition = m['competition']['name']
                utc_time = m['utcDate'] # Format waktu UTC
                
                label = f"[{competition}] {home} vs {away} ({utc_time[11:16]} UTC)"
                match_options[label] = {"home": home, "away": away, "competition": competition}
            
            # Pilihan Dropdown / Multiselect untuk user
            selected_labels = st.multiselect(
                "Pilih satu atau beberapa pertandingan untuk dimasukkan ke slip parlay:",
                options=list(match_options.keys())
            )
            
            for label in selected_labels:
                matches_list.append(match_options[label])
        else:
            st.info("ℹ️ Tidak ada jadwal pertandingan terjadwal di API untuk hari ini, atau batas kuota free tier API tercapai. Kamu tetap bisa mengetik manual di bawah jika diperlukan.")

# Opsi Cadangan Input Manual jika API kosong
if not matches_list:
    st.markdown("*(Atau masukkan manual jika daftar di atas kosong)*")
    manual_home = st.text_input("Tim Home", "")
    manual_away = st.text_input("Tim Away", "")
    if manual_home and manual_away:
        matches_list.append({"home": manual_home, "away": manual_away, "competition": "Custom Match"})

# 3. Tombol Eksekusi Analisa Mendalam
if st.button("🚀 Jalankan Analisa Mendalam Berbasis Live Data", type="primary"):
    if not matches_list:
        st.warning("⚠️ Silakan pilih minimal satu pertandingan terlebih dahulu.")
    elif not api_ready:
        st.error("❌ Konfigurasi API belum lengkap.")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa AI & Rekomendasi Worth It Bet")
        
        try:
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            for idx, match in enumerate(matches_list):
                h = match["home"]
                a = match["away"]
                comp = match["competition"]
                
                prompt = f"""
                Hari ini adalah tanggal {today_date}. Kompetisi: {comp}.
                Analisis pertandingan antara {h} (Kandang) melawan {a} (Tandang) secara sangat mendalam.
                
                ATURAN:
                1. Validasi skuad aktif saat ini per tanggal {today_date} (cek bursa transfer & cedera mutakhir).
                2. Analisis performa terkini, statistik xG, dan head-to-head.
                3. Berikan kesimpulan pasaran apa yang paling WORTH IT dan aman untuk dipasang (Over/Under atau Asian Handicap) beserta tingkat keyakinannya.
                
                Format jawaban dengan rapi menggunakan Markdown.
                """
                
                with st.spinner(f"Menganalisis laga {h} vs {a}..."):
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                
                with st.expander(f"📌 Leg {idx+1}: {h} vs {a} ({comp})", expanded=True):
                    st.markdown(analysis_result)
            
            st.divider()
            st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
            st.success(f"✨ Selesai! Kombinasi pertandingan dari server resmi berhasil dianalisa per tanggal {today_date}.")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
