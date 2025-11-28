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
# (Bilgi kaynağı içeriği aynı kalacak, yer kaplamaması için kısalttım ama siz tam halini kullanın)
MYO_BILGI_KAYNAGI = """
### ALTINOLUK MESLEK YÜKSEKOKULU BİLGİ BANKASI ###
... (Buraya önceki uzun metninizin tamamı gelecek) ...
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
        
        if last_bot_response and len(last_bot_response) > 50:
            ozet_prompt = f"Kullanıcı, ona verdiğin son cevabı özetlemeni istiyor. Aşağıdaki metni kısaca özetle: \n\nMETİN: {last_bot_response}"
        else:
            ozet_prompt = f"Kullanıcı Altınoluk MYO hakkında genel bir özet istedi. Aşağıdaki metni özetle:\n\n{myo_kaynagi}"
        
        response = client.models.generate_content(model=model_name, contents=ozet_prompt)
        return response.text, True

    return prompt, False

# --- 2. SİSTEM TALİMATI ---
SYSTEM_INSTRUCTION = (
    "Sen, Altınoluk Meslek Yüksekokulu Bilgisayar Programcılığı Bölümü'nü tanıtan yapay zeka asistanısın. "
    f"\n\n{MYO_BILGI_KAYNAGI}"
)

# --- 3. API ENTEGRASYONU ---
if "client" not in st.session_state:
    try:
        API_KEY_VALUE = st.secrets["GEMINI_API_KEY"] 
        st.session_state.client = genai.Client(api_key=API_KEY_VALUE) 
    except Exception as e:
        st.error(f"API hatası: {e}")
        st.stop()

client = st.session_state.client

if "model_name" not in st.session_state: st.session_state.model_name = 'gemini-2.5-flash'
if "messages" not in st.session_state: st.session_state.messages = []
if "audio_button_pressed" not in st.session_state: st.session_state.audio_button_pressed = False
if "last_response_index" not in st.session_state: st.session_state.last_response_index = -1
if 'temp_mic_text' not in st.session_state: st.session_state.temp_mic_text = None

def set_audio_state(index):
    st.session_state.audio_button_pressed = True
    st.session_state.last_response_index = index

# --- 4. CSS STİLİ (DÜZELTİLDİ: HER ŞEY SOLDA) ---
st.markdown("""
<style>
.css-1jc2h0i { visibility: hidden; }

/* KULLANICI MESAJI (SOLDA + SOL ÇİZGİ) */
.stChatMessage:nth-child(odd) { 
    flex-direction: row; /* Normal akış (Soldan sağa) */
    text-align: left; 
    background-color: #FFFFFF !important; 
    
    /* ÇİZGİ: SOLDA */
    border-left: 5px solid #003366 !important; 
    border-right: none !important;
    
    border-radius: 0.5rem; 
}
/* Kullanıcı mesaj içeriğini sola yasla */
.stChatMessage:nth-child(odd) div[data-testid="stMarkdownContainer"] {
    text-align: left !important;
}
/* Kullanıcı ikonu */
.stChatMessage:nth-child(odd) [data-testid="stChatMessageAvatar-user"] {
    background-color: #708090 !important; 
    margin-right: 10px;
}

/* ASİSTAN MESAJI (SOLDA + SOL ÇİZGİ) */
.stChatMessage:nth-child(even) { 
    flex-direction: row; 
    text-align: left; 
    background-color: #E0EFFF !important; 
    
    /* ÇİZGİ: SOLDA */
    border-left: 5px solid #003366 !important; 
    border-right: none !important;
    
    border-radius: 0.5rem; 
}
/* Asistan İkonu */
.stChatMessage:nth-child(even) [data-testid="stChatMessageAvatar-assistant"] {
    background-color: #003366 !important; 
    margin-right: 10px; 
}

/* BUTONLAR */
.stButton>button { box-shadow: 0 2px 4px rgba(0, 51, 102, 0.1); }
</style>
""", unsafe_allow_html=True)


# --- 5. ARAYÜZ ---
col1, col2 = st.columns([1, 6]) 
with col1:
    try:
        st.image("balikesir_uni_icon.png", width=70) 
    except: st.header("🎓") 
with col2:
    st.title("Altınoluk MYO Asistanı")
    st.caption("📌 **Kullanım Amacı:** Sadece Altınoluk MYO hakkında bilgi verir.")

# --- 6. MESAJ GEÇMİŞİ ---
for i, message in enumerate(st.session_state.messages):
    avatar_icon = "student_icon.png" if message["role"] == "user" else "balikesir_uni_icon.png"
    with st.chat_message(message["role"], avatar=avatar_icon): 
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.session_state.audio_button_pressed and st.session_state.last_response_index == i:
                audio = generate_audio(message["content"])
                if audio: st.audio(audio, format="audio/mpeg")
            st.button("🔊 Sesli Dinle", key=f"play_{i}", on_click=set_audio_state, args=(i,))

# --- 7. GİRİŞ ALANI (MIKROFON ALTTA) ---
prompt = None 
if st.session_state.temp_mic_text:
    prompt = st.session_state.temp_mic_text
    st.session_state.temp_mic_text = None

# Önce Chat Input (Metin Girişi)
if not prompt:
    prompt = st.chat_input("Sorunuzu buraya yazın...")

# Sonra Mikrofon (Altına)
# Streamlit'te chat_input en alta sabitlenir, bu yüzden mikrofonu
# bir container içinde gösterip chat_input'un üzerinde gibi durmasını sağlayamayız.
# Ancak, chat_input'u kullanmadığımız bir "dummy" container içine alıp
# mikrofonu onun altına koymak zordur.
# EN İYİ YOL: Mikrofonu chat_input'un varsayılan yerinin ÜZERİNDE tutmaktır (Önceki kod gibi).
# AMA SİZ ALTINDA İSTEDİNİZ. Streamlit standart chat_input, sayfanın EN ALTINA yapışır.
# Onun altına bir şey koymak teknik olarak mümkün değildir.
# ÇÖZÜM: Mikrofonu chat input'un hemen ÜSTÜNE ama daha estetik koyuyorum.

with st.container():
    # Mikrofonu ortala ve şıklaştır
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        text_from_mic = speech_to_text(
            language='tr',
            start_prompt="🎙️ Sesli Soru İçin Tıkla",
            stop_prompt="⏹️ Gönder",
            just_once=True,
            key='STT',
            use_container_width=True
        )
    if text_from_mic:
        st.session_state.temp_mic_text = text_from_mic
        st.rerun()

# --- 8. İŞLEM ---
if prompt:
    st.session_state.audio_button_pressed = False
    st.session_state.last_response_index = -1
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="student_icon.png"): st.markdown(prompt)

    special_content, is_special = handle_special_query(client, prompt, st.session_state.model_name, MYO_BILGI_KAYNAGI, st.session_state.messages)

    with st.spinner("Düşünüyor..."):
        try:
            if is_special: bot_resp = special_content
            else:
                chat = client.chats.create(model=st.session_state.model_name, history=st.session_state.history, config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION))
                bot_resp = chat.send_message(prompt).text
                st.session_state.history = chat.get_history()
        except Exception as e: bot_resp = "Hata oluştu."

    st.session_state.messages.append({"role": "assistant", "content": bot_resp})
    st.rerun()
