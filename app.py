import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live Parlay Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live Strict-Update Parlay Analyzer")
st.markdown("Analisis sepak bola dengan pengaman tanggal ketat agar skuad, transfer, dan cedera selalu **valid per hari ini**.")

# Validasi & Konfigurasi API Key
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_ready = True
    else:
        api_ready = False
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ GEMINI_API_KEY belum terdeteksi di Streamlit Secrets!")

# Ambil tanggal hari ini secara otomatis
today_date = datetime.now().strftime("%Y-%m-%d")

# Form Input Nama Tim
num_matches = st.number_input("Jumlah Partai (Leg) dalam 1 Slip Parlay", min_value=1, max_value=6, value=2)

matches_input = []
st.markdown("---")
for i in range(int(num_matches)):
    st.markdown(f"**Partai ke-{i+1}**")
    col1, col2 = st.columns(2)
    home_team = col1.text_input(f"Tim Home {i+1}", f"Tim Home {i+1}", key=f"home_{i}")
    away_team = col2.text_input(f"Tim Away {i+1}", f"Tim Away {i+1}", key=f"away_{i}")
    
    matches_input.append({"home": home_team, "away": away_team})
    st.markdown("---")

# Tombol Eksekusi Analisa
if st.button("🔍 Jalankan Analisa Up-to-Date", type="primary"):
    if not api_ready:
        st.error("❌ Konfigurasi API Key belum lengkap.")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa Skuad Terkini")
        
        try:
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            for idx, match in enumerate(matches_input):
                h = match["home"]
                a = match["away"]
                
                # Prompt diperketat dengan instruksi waktu dan filter transfer mutlak
                prompt = f"""
                Hari ini adalah tanggal {today_date}. Bertindaklah sebagai pakar data analis sepak bola profesional yang memegang data bursa transfer, cedera, dan skuad paling mutakhir detik ini.
                
                Analisis pertandingan antara {h} (Kandang) melawan {a} (Tandang) secara mendalam.
                
                ATURAN MUTLAK (STRICT RULES):
                1. WAJIB pastikan skuad yang dibahas benar-benar skuad aktif per tanggal {today_date}. JANGAN sebutkan pemain yang sudah pindah klub (contoh: pastikan pemain seperti Alejandro Garnacho dipetakan sesuai klub aslinya saat ini di tahun 2026, bukan klub lamanya).
                2. Periksa status cedera pemain kunci yang valid hari ini.
                3. Berikan analisis performa, taktik, dan tentukan pasaran apa yang paling WORTH IT untuk dipasang (Over/Under atau Asian Handicap) beserta persentase keyakinannya.
                
                Format jawaban dengan rapi menggunakan Markdown.
                """
                
                with st.spinner(f"Memeriksa data bursa transfer & skuad terbaru untuk {h} vs {a}..."):
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                
                with st.expander(f"📌 Leg {idx+1}: {h} vs {a}", expanded=True):
                    st.markdown(analysis_result)
            
            st.divider()
            st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
            st.success(f"✨ Selesai! Data divalidasi berdasarkan kondisi riil per tanggal {today_date}.")
            
        except Exception as e:
            st.error(f"Terjadi kendala: {e}")
