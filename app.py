import os
import streamlit as st
from google import genai
from google.genai import types 
from gtts import gTTS 
import io 
import time
import google.genai.errors 
from streamlit_mic_recorder import speech_to_text

# --- 0. UYGULAMA GENEL AYARLARI ---
st.set_page_config(
    page_title="Altınoluk MYO Asistanı", 
    page_icon="balikesir_uni_icon.png", 
    layout="centered" 
)

# --- 1. ÖZEL BİLGİ KAYNAĞI ---
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
    mp3_fp = io.BytesIO()
    try:
        tts = gTTS(text=text, lang='tr')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        return None

def handle_special_query(client, prompt, model_name, myo_kaynagi, messages):
    classification_prompt = (
        "Kullanıcının isteği sadece 'özetleme' mi? Eğer öyleyse SADECE 'OZETLE' kelimesini döndür. "
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
            ozet_prompt = f"Kullanıcı, ona verdiğin son cevabı özetlemeni istiyor. Aşağıdaki metni kısaca özetle: \n\nMETİN: {last_bot_response}"
        else:
            ozet_prompt = f"Kullanıcı Altınoluk MYO hakkında genel bir özet istedi. Aşağıdaki metni özetle:\n\n{myo_kaynagi}"
        
        response = client.models.generate_content(model=model_name, contents=ozet_prompt)
        return response.text, True

    return prompt, False

# --- 2. SİSTEM TALİMATI ---
SYSTEM_INSTRUCTION = (
    "Sen, Altınoluk Meslek Yüksekokulu Bilgisayar Programcılığı Bölümü'nü tanıtan yapay zeka asistanısın. "
    "Aşağıdaki 'BİLGİ KAYNAĞI' metnini kullanarak cevap ver. "
    "**Subjektif ve yorum isteyen sorularda (Örn: Nasıl hissettirir?, Memnuniyet?),** verdiğin KAYNAK'taki verilere (Örn: Samimi ortam, birebir ilgi) dayanarak pozitif ve yapıcı bir çıkarım yap. "
    "Konu dışı veya kaynakta olmayan soruları kibarca reddet."
    f"\n\n{MYO_BILGI_KAYNAGI}"
)

# --- 3. API ENTEGRASYONU ---
if "client" not in st.session_state:
    try:
        API_KEY_VALUE = st.secrets["GEMINI_API_KEY"] 
        st.session_state.client = genai.Client(api_key=API_KEY_VALUE) 
    except KeyError:
        st.error("🚨 KRİTİK HATA: API Anahtarı Streamlit Secrets'ta tanımlı değil.")
        st.stop()
    except Exception as e:
        st.error(f"API hatası: {e}")
        st.stop()

client = st.session_state.client

# Session state'ler
if "model_name" not in st.session_state: st.session_state.model_name = 'gemini-2.5-flash'
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = []
if "last_response_index" not in st.session_state: st.session_state.last_response_index = -1
if "audio_button_pressed" not in st.session_state: st.session_state.audio_button_pressed = False
# Giriş yönetimi için state
if 'user_prompt_content' not in st.session_state: st.session_state.user_prompt_content = None
if 'processed_prompt' not in st.session_state: st.session_state.processed_prompt = None # ÇİFT MESAJ ÖNLEME

def set_audio_state(index):
    st.session_state.audio_button_pressed = True
    st.session_state.last_response_index = index

# Metin kutusu 'on_change' fonksiyonu
def submit_text():
    # Eğer input boş değilse kaydet
    if st.session_state.widget_input:
        st.session_state.user_prompt_content = st.session_state.widget_input
        st.session_state.widget_input = "" # Kutuyu temizle

def submit_click():
    if st.session_state.widget_input:
        st.session_state.user_prompt_content = st.session_state.widget_input
        st.session_state.widget_input = ""

# --- 4. CSS STİLİ (SOLDA) ---
st.markdown("""
<style>
.css-1jc2h0i { visibility: hidden; }

/* KULLANICI MESAJI (SOLDA) */
.stChatMessage:nth-child(odd) { 
    flex-direction: row; 
    text-align: left; 
    background-color: #FFFFFF !important; 
    border-left: 5px solid #003366 !important; 
    border-right: none !important; 
    border-radius: 0.5rem; 
}
.stChatMessage:nth-child(odd) div[data-testid="stMarkdownContainer"] {
    text-align: left !important;
}
.stChatMessage:nth-child(odd) [data-testid="stChatMessageAvatar-user"] {
    background-color: #708090 !important; 
    margin-right: 10px; 
}

/* ASİSTAN MESAJI (SOLDA) */
.stChatMessage:nth-child(even) { 
    flex-direction: row; 
    text-align: left; 
    background-color: #E0EFFF !important; 
    border-left: 5px solid #003366 !important; 
    border-right: none !important; 
    border-radius: 0.5rem; 
}
.stChatMessage:nth-child(even) [data-testid="stChatMessageAvatar-assistant"] {
    background-color: #003366 !important; 
    margin-right: 10px; 
}

/* BUTONLAR */
.stButton>button { box-shadow: 0 2px 4px rgba(0, 51, 102, 0.1); }
</style>
""", unsafe_allow_html=True)


# --- 5. ARAYÜZ (BAŞLIK VE LOGO) ---
col1, col2 = st.columns([1, 6]) 
with col1:
    try:
        st.image("balikesir_uni_icon.png", width=70) 
    except FileNotFoundError:
        st.header("🎓") 
with col2:
    st.title("Altınoluk MYO Bilgisayar Programcılığı Asistanı")
    st.caption("📌 **Kullanım Amacı:** Bu Yapay Zeka Asistanı, sadece **Altınoluk MYO** ve **Bilgisayar Programcılığı Bölümü** hakkındaki verilere dayanarak cevap üretir.")

# --- 6. MESAJ GEÇMİŞİNİ GÖSTER ---
for i, message in enumerate(st.session_state.messages):
    avatar_icon = "student_icon.png" if message["role"] == "user" else "balikesir_uni_icon.png"
    
    with st.chat_message(message["role"], avatar=avatar_icon): 
        st.markdown(message["content"])

        if message["role"] == "assistant":
            if st.session_state.audio_button_pressed and st.session_state.last_response_index == i:
                audio_data = generate_audio(message["content"])
                if audio_data:
                    st.audio(audio_data, format="audio/mpeg")
            
            if st.button("🔊 Sesli Dinle", key=f"play_{i}", on_click=set_audio_state, args=(i,)):
                pass 

# --- 7. GİRİŞ ALANI (YAN YANA DÜZEN) ---
st.markdown("---") 

final_prompt = None

# Yan yana 3 kolon: Mikrofon (%10), Yazı Alanı (%80), Gönder Butonu (%10)
mic_col, text_col, btn_col = st.columns([1, 8, 1])

with mic_col:
    # Mikrofon butonu
    text_from_mic = speech_to_text(
        language='tr',
        start_prompt="🎙️",
        stop_prompt="⏹️",
        just_once=True,
        key='STT',
        use_container_width=True
    )

with text_col:
    # Yazı alanı (Enter'a basınca 'submit_text' çalışır)
    st.text_input(
        label="Mesajınızı yazın",
        placeholder="Sorunuzu buraya yazın...", 
        key="widget_input", 
        on_change=submit_text, 
        label_visibility="collapsed"
    )

with btn_col:
    st.button("➤", on_click=submit_click, use_container_width=True)

# --- 8. İŞLEM MANTIĞI (DÜZELTİLMİŞ) ---

# Giriş kaynaklarını kontrol et
if st.session_state.user_prompt_content:
    final_prompt = st.session_state.user_prompt_content
    st.session_state.user_prompt_content = None # Temizle

elif text_from_mic:
    final_prompt = text_from_mic

# HATA DÜZELTMESİ: Aynı mesajın tekrar işlenmesini engelle
# Eğer final_prompt varsa VE bu prompt daha önce işlenmemişse işle
if final_prompt and final_prompt != st.session_state.processed_prompt:
    
    # İşlenen prompt'u kaydet (tekrarı önlemek için)
    st.session_state.processed_prompt = final_prompt
    
    st.session_state.audio_button_pressed = False
    st.session_state.last_response_index = -1
    
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    
    # Özel sorgu kontrolü
    special_content, is_special = handle_special_query(client, final_prompt, st.session_state.model_name, MYO_BILGI_KAYNAGI, st.session_state.messages)

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
                response = current_chat.send_message(final_prompt)
                bot_response = response.text
                st.session_state.history = current_chat.get_history()

        except google.genai.errors.ClientError as e: # Client error yakalama
             bot_response = f"**⚠️ İstemci Hatası:** İsteğinizle ilgili bir sorun oluştu. Lütfen tekrar deneyin. ({e})"
        except google.genai.errors.ServerError as e:
            bot_response = f"**⚠️ Üzgünüm, API çok yoğun!** Lütfen 10 saniye bekleyip tekrar deneyin. ({e.status_code})"
        except Exception as e:
            bot_response = f"Üzgünüm, beklenmedik bir hata oluştu: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    st.rerun()
