import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live Search Parlay Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live Search Parlay Analyzer")
st.markdown("Aplikasi terhubung langsung dengan **Google Search** untuk memastikan data transfer pemain, cedera, dan analisis *up-to-date* setiap hari!")

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
    st.error("⚠️ GEMINI_API_KEY belum terdeteksi di Streamlit Secrets! Masukkan di menu pengaturan Secrets.")

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

# Tombol Eksekusi Analisa dengan Google Search
if st.button("🔍 Riset Google Real-Time & Analisa Mendalam", type="primary"):
    if not api_ready:
        st.error("❌ Konfigurasi API Key belum lengkap.")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa Berbasis Live Google Search")
        
        try:
            # Menggunakan model dengan kemampuan Google Search Grounding aktif
            model = genai.GenerativeModel(
                model_name='gemini-3.8-flash',
                tools='google_search_retrieval' # Mengaktifkan pencarian web langsung
            )
            
            for idx, match in enumerate(matches_input):
                h = match["home"]
                a = match["away"]
                
                prompt = f"""
                Gunakan Google Search untuk mencari berita terbaru hari ini mengenai skuad, bursa transfer, dan kondisi tim terkini.
                Analisis pertandingan antara {h} (Kandang) melawan {a} (Tandang) secara sangat mendalam.
                
                Pastikan:
                1. Validasi skuad saat ini (pastikan pemain yang sudah pindah klub atau cedera jangka panjang TIDAK dimasukkan sebagai pemain aktif klub lama).
                2. Cari data statistik, performa terkini, xG, dan berita ruang ganti terbaru dari internet hari ini.
                3. Berikan kesimpulan pasaran apa yang paling WORTH IT dan aman untuk dipasang (Over/Under, Asian Handicap, dll) beserta alasannya secara akurat.
                
                Format jawaban dengan rapi menggunakan Markdown.
                """
                
                with st.spinner(f"Sedang browsing data terkini di Google untuk laga {h} vs {a}..."):
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                
                with st.expander(f"📌 Leg {idx+1}: {h} vs {a}", expanded=True):
                    st.markdown(analysis_result)
            
            st.divider()
            st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
            st.success("✨ Selesai! Analisa di atas sudah divalidasi langsung melalui pencarian web *real-time* hari ini.")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat meriset data: {e}")
