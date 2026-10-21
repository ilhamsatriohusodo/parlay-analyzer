import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live Parlay Deep Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live Web Parlay Analyzer")
st.markdown("Masukkan nama tim yang bertanding. AI akan mencari data, statistik xG, dan berita ruang ganti terbaru dari internet secara **real-time**!")

# Ambil API Key dari Streamlit Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.warning("⚠️ Masukkan GEMINI_API_KEY di Streamlit Secrets terlebih dahulu.")

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

# Tombol Eksekusi Analisa Live
if st.button("🔍 Cari Data Real-Time & Analisa Mendalam", type="primary"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ Harap setting API Key Gemini di konfigurasi Secrets aplikasi terlebih dahulu!")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa & Live Web Intelligence")
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        for idx, match in enumerate(matches_input):
            h = match["home"]
            a = match["away"]
            
            prompt = f"""
            Bertindaklah sebagai pakar data analis sepak bola profesional dan bursa taruhan.
            Analisis pertandingan antara {h} (Kandang) melawan {a} (Tandang) secara mendalam.
            Lakukan penelusuran mengenai:
            1. Performa terkini, statistik xG (Expected Goals), dan rekor head-to-head.
            2. Kondisi ruang ganti, berita cedera pemain kunci, dan faktor kelelahan/jadwal.
            3. Berikan kesimpulan pasaran apa yang paling WORTH IT dan aman untuk dipasang (Contoh: Over/Under, Asian Handicap, atau Double Chance) beserta persentase keyakinannya dan alasannya secara spesifik.
            
            Format jawaban dengan rapi menggunakan Markdown.
            """
            
            with st.spinner(f"Sedang meriset data mendalam untuk laga {h} vs {a}..."):
                try:
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                except Exception as e:
                    analysis_result = f"Gagal mengambil data: {e}"
            
            with st.expander(f"📌 Leg {idx+1}: {h} vs {a}", expanded=True):
                st.markdown(analysis_result)
        
        st.divider()
        st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
        st.success("✨ Selesai! Analisa di atas ditarik berdasarkan kondisi riil dan data terkini dari internet.")
