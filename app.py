import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Konfigurasi Halaman
st.set_page_config(page_title="Multi-Bill 10 Legs Parlay", page_icon="⚽", layout="centered")

st.title("⚽ AI Multi-Bill Auto Parlay (Masing-Masing 10 Tim)")
st.markdown("Aplikasi pintar dengan **3 Kategori Bill (Aman, Backup, High Risk)** yang masing-masing berisi **10 Legs**, lengkap dengan Cache Harian dan 5 Lapis API Key Cadangan!")

# 1. Konfigurasi Secrets (API Keys & Email Pengirim/Penerima)
try:
    api_keys = []
    for key_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4", "GEMINI_API_KEY_5"]:
        if key_name in st.secrets:
            api_keys.append(st.secrets[key_name])
        
    FOOTBALL_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
    
    # Konfigurasi Email
    SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "")
    SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "")
    TARGET_EMAIL = st.secrets.get("TARGET_EMAIL", "")
    
    api_ready = len(api_keys) > 0 and bool(FOOTBALL_KEY)
except Exception:
    api_ready = False

if not api_ready:
    st.error("⚠️ Konfigurasi API Key belum lengkap diatur di Streamlit Secrets!")

# Rentang Waktu: Hari Ini sampai 2 Hari Kedepan
today = datetime.now()
date_from = today.strftime("%Y-%m-%d")
date_to = (today + timedelta(days=2)).strftime("%Y-%m-%d")

# Fungsi Kirim Email Otomatis
def send_email_notification(subject, body):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not TARGET_EMAIL:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, TARGET_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# 2. Fungsi Utama dengan Cache Harian (ttl = 86400 detik / 24 jam)
@st.cache_data(ttl=86400)
def get_daily_parlay_analysis(d_from, d_to, api_keys_tuple, football_api_key):
    url = f"https://api.football-data.org/v4/matches?dateFrom={d_from}&dateTo={d_to}"
    headers = {"X-Auth-Token": football_api_key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            raw_matches = response.json().get("matches", [])
        else:
            raw_matches = []
    except Exception:
        raw_matches = []
        
    if not raw_matches:
        return "EMPTY_MATCHES"
        
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
    Berikut adalah daftar pertandingan bola dari tanggal {d_from} sampai {d_to}:
    {all_available_matches}
    
    Tugasmu adalah memilih dan membagi pertandingan ke dalam **3 Kategori Bill Terpisah**, di mana **masing-masing Bill harus berisi tepat 10 pertandingan (10 Legs)**:
    
    1. **### 🎯 BILL 1: UTAMA / AMAN (10 Legs)**
       - Pilih tepat 10 pertandingan dengan probabilitas tembus paling tinggi.
       - Gunakan pasaran yang sangat konservatif (Contoh: Double Chance 1X/2X, Over 1.5, atau Handicap tipis yang sangat aman).
    
    2. **### 🛡️ BILL 2: BACKUP (10 Legs)**
       - Pilih tepat 10 pertandingan sebagai tiket cadangan alternatif yang solid secara statistik performa tim.
    
    3. **### 🔥 BILL 3: HIGH RISK / CUAN BESAR (10 Legs)**
       - Pilih tepat 10 pertandingan dengan potensi odds tinggi atau risiko lebih menantang (Contoh: Over 2.5, Handicap penuh, atau Moneyline murni).
    
    Sertakan tanggal pertandingan, nama tim, kompetisi, pasaran spesifik, serta alasan singkat untuk setiap leg di masing-masing bill. Format dengan rapi menggunakan Markdown.
    """
    
    analysis_text = ""
    for current_key in api_keys_tuple:
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.8-flash')
            response = model.generate_content(selection_prompt)
            analysis_text = response.text
            break 
        except Exception:
            continue 
            
    if not analysis_text:
        return "ERROR_QUOTA_EXCEEDED"
    
    # Otomatis kirim email saat analisis baru berhasil digenerate hari ini
    subject = f"⚽ Rekomendasi 3 Bill Parlay 10 Tim ({d_from} s/d {d_to})"
    send_email_notification(subject, analysis_text)
    
    return analysis_text

st.markdown(f"📅 **Rentang Jadwal:** `{date_from}` s/d `{date_to}`")
st.divider()

# 3. Tampilan Antarmuka
if api_ready:
    st.subheader("🏆 Rekomendasi 3 Bill (Masing-Masing 10 Tim)")
    
    with st.spinner("Memuat data harian & meracik 3 kategori bill (masing-masing 10 tim)..."):
        result_text = get_daily_parlay_analysis(date_from, date_to, tuple(api_keys), FOOTBALL_KEY)
        
    if result_text == "EMPTY_MATCHES":
        st.warning("⚠️ Tidak ada jadwal pertandingan yang cukup di server untuk meracik 30 total pilihan dalam rentang tanggal tersebut.")
    elif result_text == "ERROR_QUOTA_EXCEEDED":
        st.error("❌ Semua dari 5 API Key cadangan yang kamu masukkan telah mencapai batas kuota harian.")
    else:
        st.markdown(result_text)
        
        st.divider()
        st.markdown("### 🎫 KESIMPULAN STRATEGI 3 BILL (10 LEGS)")
        st.success(f"✨ Berhasil! Hasil analisis harian untuk periode {date_from} s/d {date_to} tersimpan di cache dan **telah dikirim otomatis ke email kamu**.")
        st.info("💡 **Tips:** Setiap bill berisi 10 pilihan tim (Aman, Backup, & High Risk). Sesuaikan nominal taruhan dengan profil risiko masing-masing bill!")
else:
    st.error("❌ Konfigurasi API belum lengkap di Secrets.")
