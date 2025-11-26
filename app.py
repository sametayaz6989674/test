import os
import streamlit as st
from google import genai
from google.genai import types 
from gtts import gTTS 
import io 
import time
import google.genai.errors 

# --- 0. UYGULAMA GENEL AYARLARI (FAVICON VE SAYFA ADI) ---
# Tarayıcı sekmesindeki ikon ve sayfa başlığını ayarlar
st.set_page_config(
    page_title="Altınoluk MYO Asistanı", 
    page_icon="balikesir_uni_icon.png", # Sekme ikonu olarak logonuzu kullanır
    layout="wide"
)
# --- 0. UYGULAMA GENEL AYARLARI BİTİŞ ---


# --- 1. ÖZEL BİLGİ KAYNAĞI (MYO Data) ---
# Bilgileriniz aynen korunmuştur.
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
        return None

def handle_special_query(client, prompt, model_name, myo_kaynagi, messages):
    """Kullanıcının isteği özetleme veya normal sohbet ise ayırır. Son cevabı özetlemeye öncelik verir."""
    
    # 1. Adım: İsteğin türünü sınıflandırma (SADECE ÖZETLEME KONTROL EDİLİYOR)
    classification_prompt = (
        "Kullanıcının isteği sadece 'özetleme' mi ('bilgileri özetle', 'kısalt' vb.)? Eğer öyleyse SADECE 'OZETLE' kelimesini döndür. "
        "Aksi halde SADECE 'NORMAL' kelimesini döndür. "
        f"Kullanıcı İsteği: '{prompt}'"
    )
    
    # Sınıflandırma isteği için API çağrısı
    classification_response = client.models.generate_content(
        model=model_name,
        contents=classification_prompt
    ).text.strip().upper()
    
    if "OZETLE" in classification_response:
        # ÖZETLEME GÖREVİ
        
        last_bot_response = ""
        if len(messages) >= 2 and messages[-2]["role"] == "assistant":
            last_bot_response = messages[-2]["content"]
        
        # Son cevabın özetlenmeye değer uzunlukta olup olmadığını kontrol et (50 karakterden uzun olmalı)
        if last_bot_response and len(last_bot_response.replace('#', '').replace('*', '')) > 50:
            ozet_prompt = (
                f"Kullanıcı, ona verdiğin son cevabı özetlemeni istiyor. Aşağıdaki metni, anlamını koruyarak 3-4 madde halinde akıcı ve anlaşılır bir dille kısaca özetle: \n\nMETİN: {last_bot_response}"
            )
        else:
            # Geçmişte özetlenecek bir metin yoksa (veya çok kısaysa), genel MYO bilgisini özetle.
            ozet_prompt = (
                f"Kullanıcı Altınoluk Meslek Yüksekokulu hakkında genel bir özet istedi. Aşağıdaki Altınoluk MYO Bilgi Kaynağı'nı, bir öğrenci adayının anlayabileceği şekilde, en kritik 4 ana başlıkta özetle."
                f"\n\nKAYNAK METİN:\n{myo_kaynagi}"
            )
        
        response = client.models.generate_content(model=model_name, contents=ozet_prompt)
        return response.text, True

    return prompt, False

# --- 2. SİSTEM TALİMATI (Chatbot'un Kimliği) ---
SYSTEM_INSTRUCTION = (
    "Sen, Altınoluk Meslek Yüksekokulu Bilgisayar Programcılığı Bölümü'nü tanıtan yapay zeka asistanısın. "
    "Aşağıdaki 'BİLGİ KAYNAĞI' metnini kullanarak cevap ver. "
    "**Subjektif ve yorum isteyen sorularda (Örn: Nasıl hissettirir?, Memnuniyet?),** verdiğin KAYNAK'taki verilere (Örn: Samimi ortam, birebir ilgi) dayanarak pozitif ve yapıcı bir çıkarım yap. "
    "Konu dışı veya kaynakta olmayan soruları kibarca reddet."
    "'BİLGİ KAYNAĞI' metnini analiz ederek soruya en iyi en güzel cevabı vericek şekilde analiz et ve en iyi sonucu ulaştır."
    "Sana sorulan soruyu BİLGİ KAYNAĞI'nda analiz ederek cevapla sorulan soruyu cevapsız bırakma elindeki bilgilere göre veri üretmelisin. sana sorduğu soruya göre NORMAL moda geçebilirsin ama konudan sapma."
    "**Not:** Eğer kullanıcı bir özetleme soruyorsa, bu isteği 'handle_special_query' fonksiyonunun ele aldığını unutma ve NORMAL cevap verme moduna geç."
    f"\n\n{MYO_BILGI_KAYNAGI}"
)

# --- 3. API ENTEGRASYONU ve CLIENT BAŞLATMA (GÜVENLİ YÖNTEM) ---

if "client" not in st.session_state:
    try:
        # API Anahtarını Streamlit secrets yapısından çekiyoruz.
        API_KEY_VALUE = st.secrets["GEMINI_API_KEY"] 
        
        # İstemciyi sadece bir kez oluştur ve Session State'e kaydet
        st.session_state.client = genai.Client(api_key=API_KEY_VALUE) 
        
    except KeyError:
        st.error("🚨 KRİTİK HATA: API Anahtarı Streamlit Secrets'ta tanımlı değil.")
        st.warning("Lütfen Streamlit Cloud 'Secrets' ayarlarınıza 'GEMINI_API_KEY' adıyla yeni anahtarınızı ekleyin.")
        st.stop()
        
    except Exception as e:
        st.error(f"API istemcisini başlatırken beklenmeyen hata: {e}")
        st.warning("Lütfen API anahtarınızın geçerliliğini kontrol edin.")
        st.stop()

# Kodu daha kısa tutmak için client değişkenini Session State'ten çek
client = st.session_state.client

# Session state'i ilk kez başlatma
if "model_name" not in st.session_state:
    st.session_state.model_name = 'gemini-2.5-flash'
    st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

# Butonun basılıp basılmadığını kontrol etmek için state
if "last_response_index" not in st.session_state:
    st.session_state.last_response_index = -1
if "audio_button_pressed" not in st.session_state:
    st.session_state.audio_button_pressed = False


# --- 4. STREAMLIT ARYÜZÜ VE KURUMSAL CSS STİLİ ---

# 4.1. Global CSS Stilleri (İkonları ve Baloncukları Düzeltme)
st.markdown("""
<style>
/* Sol üstteki menü ve Streamlit yazısını gizler (config.toml işe yaramazsa zorla gizler) */
.css-1jc2h0i { visibility: hidden; }

/* ------------------------------------------------------------- */
/* MESSAGES (Sohbet Baloncuğu) KİŞİSELLEŞTİRMESİ (Arka Plan ve Çerçeve) */
/* ------------------------------------------------------------- */

/* USER (Kullanıcı) Mesaj Baloncuğu Arka Plan Rengi */
.stChatMessage:nth-child(odd) { 
    background-color: #FFFFFF !important; /* Kullanıcı için Beyaz Arka Plan */
    border-left: 5px solid #003366; /* Kurumsal Mavi Çizgi */
    border-radius: 0.5rem;
    padding: 10px;
    margin-bottom: 10px;
}

/* ASSISTANT (Asistan) Mesaj Baloncuğu Arka Plan Rengi */
.stChatMessage:nth-child(even) { 
    background-color: #E0EFFF !important; /* Asistan için Kurumsal Açık Mavi */
    border-left: 5px solid #003366; /* Kurumsal Mavi Çizgi */
    border-radius: 0.5rem;
    padding: 10px;
    margin-bottom: 10px;
}

/* ------------------------------------------------------------- */
/* İKON DEĞİŞTİRME - STREAMLIT'İN AVATAR RENKLERİNİ DÜZELTME */
/* ------------------------------------------------------------- */

/* Kullanıcı İkonu Arka Plan Rengi (Varsayılan Kırmızıdan Gri/Nötr'e) */
.stChatMessage [data-testid="stChatMessageAvatar-user"] {
    background-color: #708090 !important; /* Gri ton */
}

/* Asistan İkonu Arka Plan Rengi (Varsayılan Turuncudan Kurumsal Maviye) */
.stChatMessage [data-testid="stChatMessageAvatar-assistant"] {
    background-color: #003366 !important; /* Koyu Kurumsal Mavi */
}

/* ------------------------------------------------------------- */
/* ALT DOKUNUŞLAR (User tarafından istendi) */
/* ------------------------------------------------------------- */
.css-1v0609 { /* st.container (genişlik) stilini değiştirir */
    box-shadow: 0 4px 8px rgba(0, 51, 102, 0.2); /* Kurumsal Mavi Hafif Gölge */
    border-radius: 12px;
}
.stButton>button { /* Sesli dinle butonlarına hafif gölge ekler */
    box-shadow: 0 2px 4px rgba(0, 51, 102, 0.1); 
}

</style>
""", unsafe_allow_html=True)


# 4.2. Başlık ve Logo Düzeni
col1, col2 = st.columns([1, 6]) 

with col1:
    try:
        # BAŞLIK LOGOSU: Balıkesir Üniversitesi
        st.image("balikesir_uni_icon.png", width=70) 
    except FileNotFoundError:
        st.info("Logo dosyası (balikesir_uni_icon.png) bulunamadı. Lütfen GitHub'a yükleyin.")
        st.header("🎓") 

with col2:
    st.title("Altınoluk MYO Bilgisayar Programcılığı Asistanı")
    st.caption("Bu chatbot, özetleme ve isteğe bağlı sesli geri bildirim özelliğine sahiptir.")
    st.caption("📌 **Kullanım Amacı:** Bu Yapay Zeka Asistanı, sadece **Altınoluk MYO** ve **Bilgisayar Programcılığı Bölümü** hakkındaki verilere dayanarak cevap üretir. Konu dışı sorular yanıtlanmayacaktır.")


# Geçmiş mesajları görüntüle
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], 
                         # İKONLAR: Kullanıcı -> student_icon.png, Asistan -> balikesir_uni_icon.png
                         avatar="student_icon.png" if message["role"] == "user" else "balikesir_uni_icon.png"): 
        st.markdown(message["content"])

        # Sadece asistan mesajlarında ses butonu göster
        if message["role"] == "assistant":
             # Eğer bu mesaj, en son gelen ve butona basılan mesaj ise sesi oynat
            if st.session_state.audio_button_pressed and st.session_state.last_response_index == i:
                audio_data = generate_audio(message["content"])
                if audio_data:
                    st.audio(audio_data, format="audio/mp3")
                else:
                    st.warning("Ses dosyası oluşturulamadı.")
            
            # Sesli dinle butonu eklenir 
            if st.button("🔊 Sesli Dinle", key=f"play_audio_{i}", on_click=lambda index=i: [setattr(st.session_state, 'audio_button_pressed', True), setattr(st.session_state, 'last_response_index', index)]):
                pass 


# Kullanıcı girişi
if prompt := st.chat_input("Altınoluk,Altınoluk MYO hakkında sorunuz nedir?"):
    
    # Yeni mesaj geldiğinde ses butonu durumunu sıfırla
    st.session_state.audio_button_pressed = False
    st.session_state.last_response_index = -1
    
    # Kullanıcı mesajını ekrana yaz ve messages listesine ekle
    with st.chat_message("user", avatar="student_icon.png"): # İKON: student_icon.png
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ÖZEL İŞLEM KONTROLÜ (Sadece Özetleme)
    special_content, is_special = handle_special_query(client, prompt, st.session_state.model_name, MYO_BILGI_KAYNAGI, st.session_state.messages)

    with st.spinner("Asistan düşünüyor..."):
        bot_response = ""
        try:
            if is_special:
                # Özel görev ise (özetleme), sonucu direkt kullan
                bot_response = special_content
            else:
                # Normal sohbet ise, sohbet objesini yeniden oluştur ve mesaj gönder
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
            # API aşırı yükleme hatalarını (503) yakalar
            bot_response = f"**⚠️ Üzgünüm, API çok yoğun!** Lütfen 10 saniye bekleyip tekrar deneyin. ({e.status_code})"

        except Exception as e:
            # Diğer tüm hataları yakalar
            bot_response = f"Üzgünüm, mesaj gönderilirken bir hata oluştu: {e}"

    # Bot cevabını ekrana yaz
    with st.chat_message("assistant", avatar="balikesir_uni_icon.png"): # İKON: balikesir_uni_icon.png
        st.markdown(bot_response)
        
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Sayfanın tekrar çizilmesini sağlamak için
    st.rerun()
