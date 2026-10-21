import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live Parlay Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live Parlay Analyzer")
st.markdown("Analisis mendalam otomatis berdasarkan data dan berita sepak bola terkini.")

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
if st.button("🔍 Jalankan Analisa Mendalam", type="primary"):
    if not api_ready:
        st.error("❌ Konfigurasi API Key belum lengkap.")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa & Rekomendasi Worth It Bet")
        
        try:
            # Menggunakan model standar tanpa fungsi tambahan yang memicu kuota berlebih
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            for idx, match in enumerate(matches_input):
                h = match["home"]
                a = match["away"]
                
                prompt = f"""
                Bertindaklah sebagai pakar data analis sepak bola profesional dan bursa taruhan yang sangat akurat dan up-to-date.
                Analisis pertandingan antara {h} (Kandang) melawan {a} (Tandang) secara mendalam.
                
                PENTING: Pastikan skuad, status cedera, dan kondisi bursa transfer pemain saat ini valid (misalnya pastikan pemain yang sudah pindah klub tidak lagi dianggap di klub lamanya).
                
                Berikan poin-poin berikut:
                1. Performa terkini, statistik xG, dan head-to-head.
                2. Kondisi ruang ganti, pemain kunci, dan faktor kelelahan.
                3. Kesimpulan pasaran apa yang paling WORTH IT dan aman untuk dipasang (Over/Under atau Asian Handicap) beserta alasannya secara spesifik.
                
                Format jawaban dengan rapi menggunakan Markdown.
                """
                
                with st.spinner(f"Sedang menganalisis laga {h} vs {a}..."):
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                
                with st.expander(f"📌 Leg {idx+1}: {h} vs {a}", expanded=True):
                    st.markdown(analysis_result)
            
            st.divider()
            st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
            st.success("✨ Selesai! Analisa berhasil digenerate.")
            
        except Exception as e:
            st.error(f"Terjadi kendala kuota atau koneksi: {e}. Coba tunggu beberapa saat lagi sebelum menekan tombol analisa.")
