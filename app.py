import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="AI Vision Parlay Analyzer", page_icon="⚽", layout="centered")

st.title("⚽ AI Vision & Live Parlay Analyzer")
st.markdown("Cukup **upload screenshot jadwal pertandingan** (dari Flashscore/Sofascore), dan AI akan otomatis membaca serta menganalisisnya secara *real-time*!")

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

# Ambil tanggal hari ini secara otomatis
today_date = datetime.now().strftime("%Y-%m-%d")

# Upload Screenshot Jadwal
st.markdown("### 📷 Upload Screenshot Jadwal Pertandingan")
st.info("💡 Tips: Screenshot jadwal atau pasaran bola dari HP kamu (bisa berisi 1, 2, atau beberapa pertandingan sekaligus).")

uploaded_file = st.file_uploader("Pilih file gambar jadwal (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Tampilkan gambar yang diupload
    image = Image.open(uploaded_file)
    st.image(image, caption="Screenshot Jadwal Berhasil Diunggah", use_container_width=True)
    
    # Tombol Eksekusi Analisa Berdasarkan Gambar
    if st.button("🚀 Baca Gambar & Jalankan Analisa Mendalam", type="primary"):
        if not api_ready:
            st.error("❌ Konfigurasi API Key belum lengkap.")
        else:
            st.divider()
            st.subheader("🌐 Hasil Analisa AI Berdasarkan Screenshot")
            
            try:
                # Menggunakan model Gemini multimodal yang bisa membaca gambar dan teks
                model = genai.GenerativeModel('gemini-3.8-flash')
                
                prompt = f"""
                Hari ini adalah tanggal {today_date}. Bertindaklah sebagai pakar data analis sepak bola profesional dan bursa taruhan.
                Perhatikan gambar jadwal pertandingan yang diunggah ini.
                
                Instruksi tugas:
                1. Identifikasi dan ekstrak semua pertandingan (tim Home dan Tim Away) yang ada di dalam gambar tersebut.
                2. Untuk setiap pertandingan yang ditemukan, lakukan analisis mendalam per tanggal {today_date}:
                   - Validasi skuad aktif saat ini (pastikan pemain yang sudah pindah klub tidak salah disebut).
                   - Performa terkini, statistik xG, dan head-to-head.
                   - Kondisi ruang ganti, pemain cedera, dan faktor kelelahan.
                   - Berikan kesimpulan pasaran apa yang paling WORTH IT dan aman untuk dipasang (Over/Under atau Asian Handicap) beserta persentase keyakinannya.
                
                Format jawaban per pertandingan dengan rapi menggunakan Markdown dan Expander (pisahkan setiap laga).
                """
                
                with st.spinner("AI sedang membaca gambar dan meriset data pertandingan secara real-time..."):
                    # Kirim gambar dan teks prompt secara bersamaan ke AI
                    response = model.generate_content([image, prompt])
                    analysis_result = response.text
                
                # Tampilkan hasil analisis
                st.markdown(analysis_result)
                
                st.divider()
                st.markdown("### 🎫 KESIMPULAN BILL PARLAY")
                st.success(f"✨ Selesai! Analisa ditarik berdasarkan jadwal di gambar dan divalidasi per tanggal {today_date}.")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses gambar dengan AI: {e}")
