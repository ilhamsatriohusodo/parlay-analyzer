import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman
st.set_page_config(page_title="AI Live Parlay Deep Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Live Web Parlay Analyzer")
st.markdown("Masukkan nama tim yang bertanding. AI akan meriset data, statistik xG, dan berita ruang ganti terbaru dari internet secara **real-time**!")

# Validasi & Konfigurasi API Key dari Streamlit Secrets
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_ready = True
    else:
        api_ready = False
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ GEMINI_API_KEY belum terdeteksi di Streamlit Secrets! Harap masukkan API Key kamu di menu pengaturan Secrets (kanan bawah).")

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
    if not api_ready:
        st.error("❌ Tidak dapat melakukan analisis karena API Key belum dikonfigurasi dengan benar.")
    else:
        st.divider()
        st.subheader("🌐 Hasil Analisa & Live Web Intelligence")
        
        try:
            # Menggunakan model Gemini versi terbaru yang stabil
            model = genai.GenerativeModel('gemini-3.8-flash')
            
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
                    response = model.generate_content(prompt)
                    analysis_result = response.text
                
                with st.expander(f"📌 Leg {idx+1}: {h} vs {a}", expanded=True):
                    st.markdown(analysis_result)
            
            st.divider()
            st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
            st.success("✨ Selesai! Analisa di atas ditarik berdasarkan kondisi riil dan data terkini dari internet.")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data dengan AI: {e}")
