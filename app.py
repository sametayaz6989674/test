import os
import streamlit as st
from google import genai
from google.genai import types 
from gtts import gTTS 
import io 
import time
import google.genai.errors 
# Sesli giriş için kütüphane
from streamlit_mic_recorder import mic_recorder 

# --- 0. UYGULAMA GENEL AYARLARI (FAVICON VE SAYFA ADI) ---
st.set_page_config(
    page_title="Altınoluk MYO Asistanı", 
    page_icon="balikesir_uni_icon.png", 
    layout="centered" # Dar, ortalanmış ekran modu
)
# --- 0. UYGULAMA GENEL AYARLARI BİTİŞ ---


# --- 1. ÖZEL BİLGİ KAYNAĞI (MYO Data) ---
MYO_BILGI_KAYNAGI = """
### ALTINOLUK MESLEK YÜKSEKOKULU BİLGİ BANKASI ###
* **Bölümler:** Altınoluk MYO'da toplam **3 bölüm** bulunmaktadır: Bilgisayar Programcılığı, Bitkisel ve Hayvansal Üretim Bölümü, ve Kimya ve Kimyasal İşleme Teknolojileri Bölümü.
* **Program:** Bilgisayar Programcılığı, 2 yıllık (4 dönem) ön lisans programıdır. hepsi böyledir altınoluk bir Meslek YüksekOkulu'dur 
* **Ders İçeriği:** Temel olarak **Algoritma ve Programlama (algoritmaya giriş, başlangıç seviyesinde kod yazma bilgisi temel bilgiler)**, Web Tasarımı (HTML/CSS/JavaScript), Veritabanı Yönetimi ve Nesne Tabanlı Programlama (Java/C#) konularına odaklanır. Ağ sistemleri dersinde ağ toplojisi switch hub tarzı kavramlar temel digital elektornik dersinde devre elemanları kullanım amaçları kullanım yerleri devre elemanları ne için kullanılır temel düzeyde bilgi ofis programları güncel ofis programları world,excel,powerpoint Acccess database tarzı uygulamalar ve temel düzeyde bilgi geri kalan dersler hakkında güncel müfredata uygun dersler işlenmektedir yada bu dersler hakkında araştırma yapıp yazabilirsin sorulan soruyu cevapsız bırakma.
* **Eğitmen Kadrosu:** Bilgisayar programcılığı bölümündeki öğretim üyeleri Gönüllülük Çalışmaları Dersine Cenk Paşa girmekte aynı zamanda İletişim dersine de giriyor. Atatürk ilkeleri ve inklap tarihi dersine Uğur yıldırım girmekte. İngilizce dersine Gamze Yavaş Çelik Girmekte. Algoritma ve Programlama Temelleri dersine Ali ERFİDAN girmekte. Ağ yönetimi ve Bilgi güvenliği dersine Emre Selman CANIAZ girmekte aynı zamanda Temel ve Digital Elektronik dersine de girmekte. Türk Dili dersine Gülfiye Bulut girmekte. Ofis yazılımları dersine Aykut DURGUT girmekte Matematik I dersine Tuğba KÜÇÜKSEYHAN girmekte aynı zamanda bu dersler Bilgisayar Programcılığı 1.sınıfın gördüğü tüm derslerdir. tüm dersler müfredata uygun ilerlemektedir. akademisyenlerimizin hepsi güleryüzlü neşeli işini seven öğrencilerini seven değer veren kişilerdir.
* **Kariyer Fırsatları:** Mezunlar Junior Yazılımcı, Veri Analizi Asistanı, Teknik Destek Uzmanı ve Front-end Geliştirici olarak özel sektörde iş bulabilmektedir.
* **Staj Durumu:** Tüm öğrencilerin 3. ve 4. yarıyıl arasında **zorunlu 30 iş günü staj** yapma yükümlülüğü vardır.
* **Okul İklimi:** Öğrenci yorumlarına göre okul samimi, küçük ve eğitmenler birebir ilgi gösterebilmektedir.
* **Okul Eğlence Hobi Yemek:** Okulumuzun Yemekhanesi mevcuttur öğrenciler 40 TL karşlığında yemek yiyebilir. Okulumuzda kantin mevcuttur voleybol sahası vardır öğrencilerin masa tenisi oynayabileceği alan mevcuttur. okulumuzun kütüphanesi mevcuttur ders çalışmak için veya araştırma yapmak için öğrenciler kullanabilir. okul bahçesi güvenlidir her saat güvenlik kapıda beklemektedir. öğrencilere öğrenci kartı verilmektedir(sınavlarda öğrenci kartları masalara koyulur) okulumuzun konferans salonu mevcuttur 
* **Akademik Takvim:** [Akademik takvim detayları korunmuştur.]
* **İdari Kadro:** Ersin KOCABIYIK Yüksekokul Sekreteri, Fatma ÖZKUL Şef, Hüseyin Çağrı ÖZSU Bilgisayar İşletmeni, Emre Selman CANIAZ Bilgisayar Programcılığı Danışmanı,
* **Okul iletişim:**Adres: İskele, Atatürk Cd. No:103, 10870 Edremit/Balıkesir okulun tam adresi bu ve Telefon: (0266) 396 15 52 hafta için 08.00 17.00 arası açık hafta sonu kapalı.
* **Altınoluk Meslek Yüksek Okulu Müdür:** [Müdür konuşması korunmuştur.]
* **Altınoluk Meslek Yüksek Okulu imkanları:** [İmkan detayları korunmuştur.]
* **Bu okul hakkında bilgi ver:** [Genel okul bilgileri korunmuştur.]
* **Bilgisayar Programcılığı bölümü hakkında:** [Bölüm detayları korunmuştur.]
* **Altınoluk nasıl bir yer altınoluk hakkında bilgi:** [Altınoluk bölge bilgisi korunmuştur.]
"""

# --- 1.5. ÖZEL GÖREV FONKSİYONLARI ---

@st.cache_data
def generate_audio(text):
    """Verilen metni gTTS kullanarak MP3 formatında ses dosyasına dönüştürür ve önbelleğe alır."""
    mp3_fp = io.BytesIO()
    try:
        tts = gTTS(text=text, lang='tr')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp.read()
    except Exception as e:
        st.warning(f"Ses oluşturulamadı: {e}")
        return None

def handle_special_query(client, prompt, model_name, myo_kaynagi, messages):
    """Kullanıcının isteği özetleme veya normal sohbet ise ayırır. Son cevabı özetlemeye öncelik verir."""
    
    classification_prompt = (
        "Kullanıcının isteği sadece 'özetleme' mi ('bilgileri özetle', 'kısalt' vb.)? Eğer öyleyse SADECE 'OZETLE' kelimesini döndür. "
        "Aksi halde SADECE 'NORMAL' kelimesini döndür. "
        f"Kullanıcı İsteği: '{prompt}'"
    )
    
    classification_response = client.models.generate_content(
        model=model_name,
        contents=classification_prompt
    ).text.strip().upper()
    
    if "OZETLE" in classification_response:
        last_bot_response = ""
        if len(messages) >= 2 and messages[-2]["role"] == "assistant":
            last_bot_response = messages[-2]["content"]
        
        if last_bot_response and len(last_bot_response.replace('#', '').replace('*', '')) > 50:
            ozet_prompt = (
                f"Kullanıcı, ona verdiğin son cevabı özetlemeni istiyor. Aşağıdaki metni, anlamını koruyarak 3-4 madde halinde akıcı ve anlaşılır bir dille kısaca özetle: \n\nMETİN: {last_bot_response}"
            )
        else:
            ozet_prompt = (
                f"Kullanıcı Altınoluk Meslek Yüksekokulu hakkında genel bir özet istedi. Aşağıdaki Altınoluk MYO Bilgi Kaynağı'nı, bir öğrenci adayının anlayabileceği şekilde, en kritik 4 ana başlıkta özetle."
                f"\n\nKAYNAK METİN:\n{myo_kaynagi}"
            )
        
        response = client.models.generate_content(model=model_name, contents=ozet_prompt)
        return response.text, True

    return prompt, False

# --- 2. SİSTEM TALİMATI (Chatbot'un Kimliği - SÜPER ZEKA MODU) ---
SYSTEM_INSTRUCTION = (
    "Sen, Altınoluk Meslek Yüksekokulu Bilgisayar Programcılığı Bölümü'nü tanıtan yapay zeka asistanısın. "
    "Aşağıdaki 'BİLGİ KAYNAĞI' metnini kullanarak cevap ver. "
    "**Subjektif ve yorum isteyen sorularda (Örn: Nasıl hissettirir?, Altınoluk güzel mi?),** verdiğin KAYNAK'taki verilere (Örn: Samimi ortam, birebir ilgi, İskele mevkiinde yer alması, doğası) dayanarak **pozitif ve yapıcı bir çıkarım yaparak akıcı, detaylı ve ikna edici bir yorum üret.** "
    "**Asla 'kaynakta yok' veya 'detaylı bilgi bulunmamaktadır' gibi cevaplar verme.** Eldeki bilgileri (konum, eğitmen kadrosu, okul iklimi vb.) kullanarak soruyu destekleyici şekilde yanıtla. "
    "Konu dışı soruları kibarca reddet."
    "'BİLGİ KAYNAĞI' metnini analiz ederek soruya en iyi en güzel cevabı vericek şekilde analiz et ve en iyi sonucu ulaştır."
    "Sana sorulan soruyu BİLGİ KAYNAĞI'nda analiz ederek cevapla sorulan soruyu cevapsız bırakma elindeki bilgilere göre veri üretmelisin. sana sorduğu soruya göre NORMAL moda geçebilirsin ama konudan sapma."
    "**Not:** Eğer kullanıcı bir özetleme soruyorsa, bu isteği 'handle_special_query' fonksiyonunun ele aldığını unutma ve NORMAL cevap verme moduna geç."
    f"\n\n{MYO_BILGI_KAYNAGI}"
)

# --- 3. API ENTEGRASYONU ve CLIENT BAŞLATMA (GÜVENLİ YÖNTEM) ---

if "client" not in st.session_state:
    try:
        API_KEY_VALUE = st.secrets["GEMINI_API_KEY"] 
        st.session_state.client = genai.Client(api_key=API_KEY_VALUE) 
    except KeyError:
        st.error("🚨 KRİTİK HATA: API Anahtarı Streamlit Secrets'ta 'GEMINI_API_KEY' adıyla tanımlı değil.")
        st.warning("Lütfen Streamlit Cloud 'Secrets' ayarlarınıza 'GEMINI_API_KEY' adıyla yeni anahtarınızı ekleyin.")
        st.stop()
    except Exception as e:
        st.error(f"API istemcisini başlatırken beklenmeyen hata: {e}")
        st.warning("Lütfen API anahtarınızın geçerliliğini kontrol edin.")
        st.stop()

client = st.session_state.client

# --- 4. SESSION STATE YÖNETİMİ VE CALLBACK FONKSİYONLARI ---

# Ses butonu state'leri
if "last_response_index" not in st.session_state:
    st.session_state.last_response_index = -1
if "audio_button_pressed" not in st.session_state:
    st.session_state.audio_button_pressed = False

# Sesli dinle butonu tıklandığında state'i güncelleyen fonksiyon
def set_audio_state(index):
    st.session_state.audio_button_pressed = True
    st.session_state.last_response_index = index

# MİKROFON İÇİN GEÇİCİ SESSION STATE'LERİ
if 'temp_mic_prompt' not in st.session_state:
    st.session_state.temp_mic_prompt = None

# YENİ HATA ÇÖZÜMÜ: Sesli girişten metin geldiğinde çalışan fonksiyon
def handle_mic_input():
    """Kayıt durduğunda çalışır ve mic_recorder'dan gelen metni kontrol eder."""
    # mic_recorder'ın sonucu session_state.mic_recorder'da saklanır
    mic_result = st.session_state.mic_recorder

    # SADECE metin varsa ve boş değilse prompt olarak ayarla
    if mic_result and mic_result.get('text') and mic_result['text'].strip():
        # Metni geçici olarak Session State'e kaydet
        st.session_state.temp_mic_prompt = mic_result['text']
        # Session State güncellendiği için yeniden çizimi zorla (İşlem 7'ye atla)
        st.rerun()

# Diğer başlangıç state'leri
if "model_name" not in st.session_state:
    st.session_state.model_name = 'gemini-2.5-flash'
    st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

# --- 5. STREAMLIT ARYÜZÜ VE KURUMSAL CSS STİLİ ---

# 5.1. Global CSS Stilleri
st.markdown("""
<style>
/* Sol üstteki menü ve Streamlit yazısını gizler */
.css-1jc2h0i { visibility: hidden; }

/* Sohbet Baloncuğu KİŞİSELLEŞTİRMESİ */
.stChatMessage:nth-child(odd) { 
    background-color: #FFFFFF !important; 
    border-left: 5px solid #003366; 
    border-radius: 0.5rem;
    padding: 10px;
    margin-bottom: 10px;
}
.stChatMessage:nth-child(even) { 
    background-color: #E0EFFF !important; 
    border-left: 5px solid #003366; 
    border-radius: 0.5rem;
    padding: 10px;
    margin-bottom: 10px;
}
.stChatMessage [data-testid="stChatMessageAvatar-user"] {
    background-color: #708090 !important; 
}
.stChatMessage [data-testid="stChatMessageAvatar-assistant"] {
    background-color: #003366 !important; 
}
.css-1v0609 { 
    box-shadow: 0 4px 8px rgba(0, 51, 102, 0.2); 
    border-radius: 12px;
}
.stButton>button { 
    box-shadow: 0 2px 4px rgba(0, 51, 102, 0.1); 
}
</style>
""", unsafe_allow_html=True)


# 5.2. Başlık ve Logo Düzeni
col1, col2 = st.columns([1, 6]) 

with col1:
    try:
        st.image("balikesir_uni_icon.png", width=70) 
    except FileNotFoundError:
        st.info("Logo dosyası bulunamadı.")
        st.header("🎓") 

with col2:
    st.title("Altınoluk MYO Bilgisayar Programcılığı Asistanı")
    st.caption("Bu chatbot, özetleme ve isteğe bağlı sesli geri bildirim özelliğine sahiptir.")
    st.caption("📌 **Kullanım Amacı:** Bu Yapay Zeka Asistanı, sadece **Altınoluk MYO** ve **Bilgisayar Programcılığı Bölümü** hakkındaki verilere dayanarak cevap üretir. Konu dışı sorular yanıtlanmayacaktır.")


# Geçmiş mesajları görüntüle
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], 
                         avatar="student_icon.png" if message["role"] == "user" else "balikesir_uni_icon.png"): 
        st.markdown(message["content"])

        if message["role"] == "assistant":
            if st.session_state.audio_button_pressed and st.session_state.last_response_index == i:
                audio_data = generate_audio(message["content"])
                if audio_data:
                    st.audio(audio_data, format="audio/mp3")
                
            if st.button("🔊 Sesli Dinle", key=f"play_audio_{i}", on_click=set_audio_state, args=(i,)):
                pass 

# --- 6. KULLANICI GİRİŞİ (Yazılı ve Sesli) ---
prompt = None # Prompt başlangıçta None

# Eğer bir önceki adımda sesli giriş alınmışsa, prompt'u buradan al ve sıfırla
if st.session_state.temp_mic_prompt:
    prompt = st.session_state.temp_mic_prompt
    st.session_state.temp_mic_prompt = None # Tekrar kullanmaması için sıfırla

# Sohbet girişini bir container içine alarak mikrofon butonuyla yan yana getirme
# Bunun için st.chat_input'un varsayılan davranışını değiştiremeyiz.
# Bu yüzden, mikrofonu ayrı bir satırda tutmaya devam ediyoruz (daha stabil)
with st.container():
    st.write("---") 
    st.markdown("##### 🎙️ Veya Sesli Sorun")
    
    # mic_recorder bileşeni
    # NOTE: Key'i 'mic_recorder' olarak kullanmak zorunludur, çünkü callback onu kullanır
    mic_recorder(
        start_prompt="🔴 Kaydı Başlat", 
        stop_prompt="⏹️ Kaydı Durdur ve Metne Çevir", 
        key='mic_recorder',
        callback=handle_mic_input, # Kayıt durduğunda handle_mic_input fonksiyonunu çağır
        use_streamlit_native_buttons=True
    )
    
    # Yazılı giriş sadece sesli giriş yoksa gösterilir
    if not prompt:
        prompt = st.chat_input("Altınoluk, Altınoluk MYO hakkında sorunuz nedir?")


# --- 7. İŞLEM BAŞLATMA ---
if prompt:
    
    st.session_state.audio_button_pressed = False
    st.session_state.last_response_index = -1
    
    with st.chat_message("user", avatar="student_icon.png"): 
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    special_content, is_special = handle_special_query(client, prompt, st.session_state.model_name, MYO_BILGI_KAYNAGI, st.session_state.messages)

    with st.spinner("Asistan düşünüyor..."):
        bot_response = ""
        try:
            if is_special:
                bot_response = special_content
            else:
                current_chat = client.chats.create(
                    model=st.session_state.model_name, 
                    history=st.session_state.history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                response = current_chat.send_message(prompt)
                bot_response = response.text
                st.session_state.history = current_chat.get_history()

        except google.genai.errors.ServerError as e:
            bot_response = f"**⚠️ Üzgünüm, API çok yoğun!** Lütfen 10 saniye bekleyip tekrar deneyin. ({e.status_code})"
        except Exception as e:
            bot_response = f"Üzgünüm, mesaj gönderilirken bir hata oluştu: {e}"

    with st.chat_message("assistant", avatar="balikesir_uni_icon.png"): 
        st.markdown(bot_response)
        
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    st.rerun()
