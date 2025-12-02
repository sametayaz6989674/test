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

# --- 1. ÖZEL BİLGİ KAYNAĞI (TAM VE EKSİKSİZ HALİ) ---
MYO_BILGI_KAYNAGI = """
### ALTINOLUK MESLEK YÜKSEKOKULU BİLGİ BANKASI ###

* **Bölümler:** Altınoluk MYO'da toplam **3 bölüm** bulunmaktadır: Bilgisayar Programcılığı, Bitkisel ve Hayvansal Üretim Bölümü, ve Kimya ve Kimyasal İşleme Teknolojileri Bölümü.

* **Program:** Bilgisayar Programcılığı, 2 yıllık (4 dönem) ön lisans programıdır. hepsi böyledir altınoluk bir Meslek YüksekOkulu'dur.

* **Ders İçeriği:** Temel olarak **Algoritma ve Programlama (algoritmaya giriş, başlangıç seviyesinde kod yazma bilgisi temel bilgiler)**, Web Tasarımı (HTML/CSS/JavaScript), Veritabanı Yönetimi ve Nesne Tabanlı Programlama (Java/C#) konularına odaklanır. Ağ sistemleri dersinde ağ toplojisi switch hub tarzı kavramlar, temel digital elektronik dersinde devre elemanları kullanım amaçları kullanım yerleri devre elemanları ne için kullanılır temel düzeyde bilgi, ofis programları güncel ofis programları word, excel, powerpoint, Access database tarzı uygulamalar ve temel düzeyde bilgi. Geri kalan dersler hakkında güncel müfredata uygun dersler işlenmektedir.

* **Eğitmen Kadrosu:** * Gönüllülük Çalışmaları ve İletişim dersine Cenk Paşa girmekte.
    * Atatürk ilkeleri ve inkılap tarihi dersine Uğur Yıldırım girmekte.
    * İngilizce dersine Gamze Yavaş Çelik Girmekte.
    * Algoritma ve Programlama Temelleri dersine Ali ERFİDAN girmekte.
    * Ağ yönetimi ve Bilgi güvenliği ile Temel ve Digital Elektronik dersine Emre Selman CANIAZ girmekte.
    * Türk Dili dersine Gülfiye Bulut girmekte.
    * Ofis yazılımları dersine Aykut DURGUT girmekte.
    * Matematik I dersine Tuğba KÜÇÜKSEYHAN girmekte.
    * Akademisyenlerimizin hepsi güleryüzlü, neşeli, işini seven, öğrencilerini seven ve değer veren kişilerdir.

* **Öğretmen İletişim Bilgileri:**
    * Tuğba Küçükseyhan: kucukseyhan@balikesir.edu.tr
    * Emre Selman CANIAZ: escaniaz@balikesir.edu.tr
    * Aykut Durgut: adurgut@balikesir.edu.tr
    * Cenk Paşa: cpasa@balikesir.edu.tr
    * Ali Erfidan: ali.erfidan@balikesir.edu.tr

* **Kariyer Fırsatları:** Mezunlar Junior Yazılımcı, Veri Analizi Asistanı, Teknik Destek Uzmanı ve Front-end Geliştirici olarak özel sektörde iş bulabilmektedir.

* **Staj Durumu:** Tüm öğrencilerin 3. ve 4. yarıyıl arasında **zorunlu 30 iş günü staj** yapma yükümlülüğü vardır.

* **Okul İklimi:** Öğrenci yorumlarına göre okul samimi, küçük ve eğitmenler birebir ilgi gösterebilmektedir.

* **Okul Eğlence, Hobi ve Yemek:** Okulumuzun Yemekhanesi mevcuttur öğrenciler 40 TL karşlığında yemek yiyebilir. Okulumuzda kantin mevcuttur, voleybol sahası vardır, öğrencilerin masa tenisi oynayabileceği alan mevcuttur. Okulumuzun kütüphanesi mevcuttur ders çalışmak için veya araştırma yapmak için öğrenciler kullanabilir. Okul bahçesi güvenlidir her saat güvenlik kapıda beklemektedir. Öğrencilere öğrenci kartı verilmektedir (sınavlarda öğrenci kartları masalara koyulur). Okulumuzun konferans salonu mevcuttur.

* **İdari Kadro:** Ersin KOCABIYIK (Yüksekokul Sekreteri), Fatma ÖZKUL (Şef), Hüseyin Çağrı ÖZSU (Bilgisayar İşletmeni), Emre Selman CANIAZ (Bilgisayar Programcılığı Danışmanı), Okul Müdürü Dr. Öğr. Üyesi Sakin Vural Varlı.

* **Okul İletişim ve Detaylar:** * Adres: İskele, Atatürk Cd. No:103, 10870 Edremit/Balıkesir. 
    * Telefon: (0266) 396 15 52. 
    * Çalışma Saatleri: Hafta içi 08.00 - 17.00 arası açık, hafta sonu kapalı.
    * Toplam Öğrenci Sayısı: 352.
    * Geçme Notu: Vizenin %40'ı, finalin %60'ı alınır. Finalden kesinlikle 50 ve üstü not almanız gerekmektedir. Ortalama 45 ve üstü ise dersi geçersiniz. Çan eğrisi yoktur.
    * Konaklama: Öğrenciler apart, kiralık daire veya Edremit'teki KYK yurtlarında kalmaktadır.
    * Puan Bilgileri (2025 YÖKATLAS): TYT Giriş Puanı 317,14553. Başarı sırası 662.855. Ortalama diploma notu 77.8.
    * okulumuzun website adresi https://altinolukmyo.balikesir.edu.tr/ bu adres üzerinden  akademik takvim detaylarına okul duyurularına bakabilirsiniz.
    * https://obs.balikesir.edu.tr/ okulun obs(öğrenci bilgi sistemidir)  ders programı, ilan edilen notlara bakabilirsiniz. öğrenci mailinize iletişim bilgilerine bakabilirsiniz

* **Akademik Takvim:** * 01 Eylül 2025: Azami Süre Sonu Sınav İlanı
    * 04-05 Eylül 2025: 1. Ek Sınavlar
    * 11-12 Eylül 2025: 2. Ek Sınavlar
    * 17-19 Eylül 2025: Güz Yarıyılı Ders Kayıtları
    * 22 Eylül 2025 - 09 Ocak 2026: GÜZ YARIYILI
    * 10-18 Kasım 2025: Ara Sınav Haftası
    * 12-23 Ocak 2026: Yarıyıl Sonu Sınavları (Final)
    * 02-06 Şubat 2026: Bütünleme Sınavları
    * 16 Şubat - 16 Haziran 2026: BAHAR YARIYILI
    * 06-14 Nisan 2026: Ara Sınav Haftası
    * 17-30 Haziran 2026: Yarıyıl Sonu Sınavları
    * 08-14 Temmuz 2026: Bütünleme Sınavları

* **Altınoluk Meslek Yüksek Okulu Müdür Mesajı (Sakin Vural VARLI):** Balıkesir Üniversitesi Altınoluk Meslek Yüksekokulu, 2007 yılından bu yana zengin doğal güzellikleriyle dikkat çeken, zeytin ağaçlarıyla çevrili ve Kazdağları’nın eteğinde yer alan Altınoluk’ta eğitim-öğretim faaliyetlerini sürdürmektedir. Genç ve dinamik akademik kadrosuyla yüksekokulumuz, Bilgisayar Programcılığı, Tıbbi ve Aromatik Bitkiler Programı ve Kimya Teknolojileri Programı olmak üzere üç örgün programda eğitim vermektedir. Hedefimiz, bilgi ve teknoloji üreten, doğa ve çevre bilinci gelişmiş, toplumsal değerleri önemseyen, araştırmacı ve çağdaş bir öğretim kültürünü benimsemiş bireyler yetiştirmektir. Öğrencilerimizi, yalnızca akademik bilgiyle değil, aynı zamanda iş dünyasında sorumluluk alabilen, yenilikçi ve üretken bireyler olarak hayata hazırlıyoruz. Bu doğrultuda, üniversite-sanayi-toplum iş birliğini esas alarak, yaşadığımız kentin kalkınmasına katkıda bulunacak, ülkemizin sorunlarına duyarlı ve sosyal sorumluluk bilinci yüksek mezunlar yetiştirmeyi amaçlıyoruz. Altınoluk Meslek Yüksekokulu olarak, Atatürk ilke ve inkılaplarını rehber edinen; çağın gerektirdiği bilgi, beceri ve teknolojik gelişmelere uyum sağlayan; uluslararası platformlarda aranılan niteliklere sahip bireyler yetiştirme gayretiyle çalışmalarımızı sürdürüyoruz. Güzel ülkemizin aydınlık yarınlarını inşa edecek olan siz değerli gençlerimizi, Altınoluk Meslek Yüksekokulu ailesine katılmaya davet ediyoruz.

* **Altınoluk Meslek Yüksek Okulu İmkanları:** Bilgi ve teknoloji üreten, toplumsal değerleri önemseyen, doğa ve çevre bilinci gelişmiş, araştırmacı ve çağdaş bir öğretim kültürü ile topluma liderlik yapabilecek bireyler yetiştirmektir. Yüksekokul binasında 11 derslik, 1 bilgisayar, 1 kimya, 1 botanik laboratuarının yanı sıra bir kapalı spor salonu bulunmaktadır.

* **Genel Bilgi:** Altınoluk Meslek Yüksekokulu, Balıkesir Üniversitesi’ne bağlı, 2007 yılında kurulan ve Edremit Körfezi’nde yer alan bir önlisans eğitim kurumudur. Doğayla iç içe kampüsü, modern laboratuvarları ve deneyimli akademik kadrosu ile öğrencilerine hem teorik hem de uygulamalı eğitim sunar.

* **Altınoluk Hakkında:** Altınoluk, Edremit Körfezi’nin incisi olarak, hem deniz hem doğa tutkunlarını kendine çeker. Kaz Dağları’nın eteklerinde yer alan bu sahil kasabası, yemyeşil zeytinlikler ve çam ormanlarıyla çevrilidir. Yazları sıcak ve güneşli, kışları ise ılık geçen iklimiyle yılın her dönemi ziyaretçilerini ağırlayabilir. Tarihi dokusu, Rum ve Osmanlı izleri taşıyan yapıları ve leziz yerel mutfağıyla Altınoluk, huzurlu bir tatil deneyimi sunar.
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
if 'temp_mic_text' not in st.session_state: st.session_state.temp_mic_text = None

def set_audio_state(index):
    st.session_state.audio_button_pressed = True
    st.session_state.last_response_index = index

# --- 4. CSS STİLİ (SOLDA) ---
st.markdown("""
<style>
.css-1jc2h0i { visibility: hidden; }

/* KULLANICI MESAJI (SOLDA + SOL ÇİZGİ) */
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

/* ASİSTAN MESAJI (SOLDA + SOL ÇİZGİ) */
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

# --- 7. GİRİŞ ALANI (MIKROFON SOLDA VE ÜSTTE) ---
prompt = None 

if st.session_state.temp_mic_text:
    prompt = st.session_state.temp_mic_text
    st.session_state.temp_mic_text = None

# GİRİŞ ALANINI YÖNETEN KONTEYNER
with st.container():
    st.markdown("---") # Ayırıcı
    
    # 1. Mikrofon Butonu (Sola Yaslı, Girişin Üstünde)
    c_mic, c_bos = st.columns([1, 3]) # Sol sütun (mikrofon) dar, sağ sütun boş
    with c_mic:
        text_from_mic = speech_to_text(
            language='tr',
            start_prompt="🎙️ Sesli Konuşmak İçin Tıkla",
            stop_prompt="⏹️ Göndermek İçin Tıkla",
            just_once=True,
            key='STT',
            use_container_width=True
        )
    
    if text_from_mic:
        st.session_state.temp_mic_text = text_from_mic
        st.rerun()

    # 2. Yazılı Giriş (En Altta, Tam Genişlik)
    if not prompt:
        prompt = st.chat_input("Sorunuzu buraya yazın...")

# --- 8. İŞLEM MANTIĞI ---
if prompt:
    st.session_state.audio_button_pressed = False
    st.session_state.last_response_index = -1
    
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

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    st.rerun()


