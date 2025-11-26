import os
import streamlit as st
from google import genai
from google.genai import types 
from gtts import gTTS 
import io 
import time
import google.genai.errors 

# Bu kısımlar SİLİNDİ:
# DİKKAT: API anahtarı, test amaçlı olarak direkt koda GÖMÜLMÜŞTÜR.
# MY_API_KEY = ""

# --- 1. ÖZEL BİLGİ KAYNAĞI (MYO Data) ---
# En son güncellediğiniz tüm bilgiler buraya dahil edilmiştir.
MYO_BILGI_KAYNAGI = """
### ALTINOLUK MESLEK YÜKSEKOKULU BİLGİ BANKASI ###
* **Bölümler:** Altınoluk MYO'da toplam **3 bölüm** bulunmaktadır: Bilgisayar Programcılığı, Bitkisel ve Hayvansal Üretim Bölümü, ve Kimya ve Kimyasal İşleme Teknolojileri Bölümü.
* **Program:** Bilgisayar Programcılığı, 2 yıllık (4 dönem) ön lisans programıdır. hepsi böyledir altınoluk bir Meslek YüksekOkulu'dur 
* **Ders İçeriği:** Temel olarak **Algoritma ve Programlama (algoritmaya giriş, başlangıç seviyesinde kod yazma bilgisi temel bilgiler)**, Web Tasarımı (HTML/CSS/JavaScript), Veritabanı Yönetimi ve Nesne Tabanlı Programlama (Java/C#) konularına odaklanır. Ağ sistemleri dersinde ağ toplojisi switch hub tarzı kavramlar temel digital elektornik dersinde devre elemanları kullanım amaçları kullanım yerleri devre elemanları ne için kullanılır temel düzeyde bilgi ofis programları güncel ofis programları world,excel,powerpoint Acccess database tarzı uygulamalar ve temel düzeyde bilgi geri kalan dersler hakkında güncel müfredata uygun dersler işlenmektedir yada bu dersler hakkında araştırma yapıp yazabilirsin sorulan soruyu cevapsız bırakma.
* **Eğitmen Kadrosu:** Bilgisayar programcılığı bölümündeki öğretim üyeleri Gönüllülük Çalışmaları Dersine Cenk Paşa girmekte aynı zamanda İletişim dersine de giriyor. Atatürk ilkeleri ve inklap tarihi dersine Uğur yıldırım girmekte. İngilizce dersine Gamze Yavaş Çelik Girmekte. Algoritma ve Programlama Temelleri dersine Ali ERFİDAN girmekte. Ağ yönetimi ve Bilgi güvenliği dersine Emre Selman CANIAZ girmekte aynı zamanda Temel ve Digital Elektronik dersine de girmekte. Türk Dili dersine Gülfiye Bulut girmekte. Ofis yazılımları dersine Aykut DURGUT girmekte Matematik I dersine Tuğba KÜÇÜKSEYHAN girmekte aynı zamanda bu dersler Bilgisayar Programcılığı 1.sınıfın gördüğü tüm derslerdir. tüm dersler müfredata uygun ilerlemektedir. akademisyenlerimizin hepsi güleryüzlü neşeli işini seven öğrencilerini seven değer veren kişilerdir.
* **Kariyer Fırsatları:** Mezunlar Junior Yazılımcı, Veri Analizi Asistanı, Teknik Destek Uzmanı ve Front-end Geliştirici olarak özel sektörde iş bulabilmektedir.
* **Staj Durumu:** Tüm öğrencilerin 3. ve 4. yarıyıl arasında **zorunlu 30 iş günü staj** yapma yükümlülüğü vardır.
* **Okul İklimi:** Öğrenci yorumlarına göre okul samimi, küçük ve eğitmenler birebir ilgi gösterebilmektedir.
* **Okul iletişim:**Adres: İskele, Atatürk Cd. No:103, 10870 Edremit/Balıkesir okulun tam adresi bu ve Telefon: (0266) 396 15 52 hafta için 08.00 17.00 arası açık hafta sonu kapalı.
* **Altınoluk Meslek Yüksek Okulu Müdür:**Balıkesir Üniversitesi Altınoluk Meslek Yüksekokulu, 2007 yılından bu yana zengin doğal güzellikleriyle dikkat çeken, zeytin ağaçlarıyla çevrili ve Kazdağları’nın eteğinde yer alan Altınoluk’ta eğitim-öğretim faaliyetlerini sürdürmektedir. Genç ve dinamik akademik kadrosuyla yüksekokulumuz, Bilgisayar Programcılığı, Tıbbi ve Aromatik Bitkiler Programı ve Kimya Teknolojileri Programı olmak üzere üç örgün programda eğitim vermektedir. Hedefimiz, bilgi ve teknoloji üreten, doğa ve çevre bilinci gelişmiş, toplumsal değerleri önemseyen, araştırmacı ve çağdaş bir öğretim kültürünü benimsemiş bireyler yetiştirmektir. Öğrencilerimizi, yalnızca akademik bilgiyle değil, aynı zamanda iş dünyasında sorumluluk alabilen, yenilikçi ve üretken bireyler olarak hayata hazırlıyoruz. Bu doğrultuda, üniversite-sanayi-toplum iş birliğini esas alarak, yaşadığımız kentin kalkınmasına katkıda bulunacak, ülkemizin sorunlarına duyarlı ve sosyal sorumluluk bilinci yüksek mezunlar yetiştirmeyi amaçlıyoruz. Altınoluk Meslek Yüksekokulu olarak, Atatürk ilke ve inkılaplarını rehber edinen; çağın gerektirdiği bilgi, beceri ve teknolojik gelişmelere uyum sağlayan; uluslararası platformlarda aranılan niteliklere sahip bireyler yetiştirme gayretiyle çalışmalarımızı sürdürüyoruz. Güzel ülkemizin aydınlık yarınlarını inşa edecek olan siz değerli gençlerimizi, Altınoluk Meslek Yüksekokulu ailesine katılmaya davet ediyoruz. Sayın müdürümüz Altınoluk Meslek Yüksek Okulu Müdürü Sakin Vural VARLI değerli öğrencilerimize ve tercih etmek isteynlere bunları diyor.
* **Altınoluk Meslek Yüksek Okulu imkanları:**Bilgi ve teknoloji üreten, toplumsal değerleri önemseyen, doğa ve çevre bilinci gelişmiş, araştırmacı ve çağdaş bir öğretim kültürü ile topluma liderlik yapabilecek, Atatürk ilke ve inkılaplarına bağlı bireyler yetiştirmektir. Üniversite-Sanayi-Toplum işbirliği çerçevesinde; ilimiz ve bölgemiz başta olmak üzere ülkemizin sorunlarını çözmeye yönelik çalışmalar yapan, sosyal sorumluluk bilinci ile ülke sorunlarına duyarlı, yaşadığı kentin kalkınmasına ve gelişmesine katkıda bulunan bireyler yetiştirmek ve Türkiye ve dünyada tanınan bir kurum olmaktır. Altınoluk Meslek Yüksekokulu olarak, bilgi ve teknoloji üreten, toplumsal değerleri önemseyen, doğa ve çevre bilinci gelişmiş, araştırmacı ve çağdaş bir öğretim anlayışını benimsiyoruz. Atatürk ilke ve inkılaplarına bağlı bireyler yetiştirerek, sosyal sorumluluk bilinciyle ülkemizin ve bölgemizin sorunlarına çözüm üretmeyi ve yaşadığımız kentin kalkınmasına katkıda bulunmayı hedefliyoruz. Üniversite-sanayi-toplum işbirliği çerçevesinde, Türkiye ve dünyada tanınan bir eğitim kurumu olma yolunda ilerlerken, öğrencilerimizi topluma liderlik edebilecek yetkinliklerle donatmayı amaçlıyoruz. Altınoluk Meslek Yüksekokulu, Y.Ö.K. Genel Kurulunun 16.10.2007 tarihli kararıyla açılmıştır. Altınoluk Meslek Yüksekokulu 2007-2008 Eğitim-Öğretim yılında ek kontenjanla Tıbbi Aromatik Bitkiler Bölümünde 15, Bilgisayar Teknolojileri ve Programlama Bölümünde ise 36 öğrenci olmak üzere toplam 51 öğrenci ile Eğitim Öğretime başlamıştır. 2008-2009 öğretim yılı yeni açılmış olan Kimya Teknolojileri Programı ve her üç bölümün ikinci öğretimleri ile beraber öğrenci sayısı 250 ye çıkmıştır. 2009-2010 öğretim yılında Öğrenci Sayımız 430 ‘a yükselmekle beraber 2010-2011 öğretim yılında bu sayının 500’ü geçmesi beklenmektedir. Yüksekokul binasında 11 derslik, 1 bilgisayar, 1 kimya, 1 botanik laboratuarının yanı sıra bir kapalı spor salonu bulunmaktadır.
* **Bu okul hakkında bilgi ver:**Altınoluk Meslek Yüksekokulu, Balıkesir Üniversitesi’ne bağlı, 2007 yılında kurulan ve Edremit Körfezi’nde yer alan bir önlisans eğitim kurumudur. Doğayla iç içe kampüsü, modern laboratuvarları ve deneyimli akademik kadrosu ile öğrencilerine hem teorik hem de uygulamalı eğitim sunar. Özellikle Bilgisayar Programcılığı bölümü, yazılım ve teknoloji meraklılarını kendine çeker; öğrenciler burada yazılım geliştirme, veri tabanı yönetimi, web ve mobil uygulama tasarımı gibi alanlarda kapsamlı bir eğitim alır ve projelerle sektöre hazır hâle gelir. Bölümün çağdaş müfredatı ve modern laboratuvarları, öğrencilerin yaratıcı ve analitik düşünme yetilerini geliştirir. Okulun diğer programları arasında Kimya Teknolojisi ve Tıbbi ve Aromatik Bitkiler yer alır. 2025 itibarıyla Bilgisayar Programcılığı bölümü için taban puan yaklaşık 317 civarındadır ve kontenjan 50 kişidir. Altınoluk MYO, öğrencilere mesleki bilgi kazandırmanın yanı sıra çevre bilinci, toplumsal sorumluluk ve bölgesel katkı gibi değerleri de ön planda tutar; mezunları bilişim sektöründe geniş iş olanaklarına sahip olur ve geleceğin teknolojilerini şekillendirecek fırsatlarla karşılaşır.
* **Bilgisayar Programcılığı bölümü hakkında:**Bilgisayar Programcılığı bölümü, teknoloji ve yazılım tutkunlarını kendine çeker. Bu bölüm, öğrencilerini yazılım geliştirme, veri tabanı yönetimi, web ve mobil uygulama tasarımı gibi alanlarda donanımlı hale getirir. Öğrenciler, hem teorik bilgileri hem de uygulamalı projeleriyle sektöre hazır bir şekilde yetişir. Bölümün çağdaş müfredatı, modern laboratuvarları ve deneyimli akademik kadrosu, öğrencilere hem yaratıcı hem de analitik düşünme becerisi kazandırır. Mezunları, bilişim sektöründe geniş iş olanaklarına sahip olarak, geleceğin teknolojilerini şekillendirecek fırsatlarla karşılaşır
**"**Altınoluk nasıl bir yer altınoluk hakkında bilgi:**Altınoluk, Edremit Körfezi’nin incisi olarak, hem deniz hem doğa tutkunlarını kendine çeker. Kaz Dağları’nın eteklerinde yer alan bu sahil kasabası, yemyeşil zeytinlikler ve çam ormanlarıyla çevrilidir. Yazları sıcak ve güneşli, kışları ise ılık geçen iklimiyle yılın her dönemi ziyaretçilerini ağırlayabilir. Tarihi dokusu, Rum ve Osmanlı izleri taşıyan yapıları ve leziz yerel mutfağıyla Altınoluk, huzurlu bir tatil deneyimi sunar.
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
        # 🚨 ANAHTAR OKUMA YÖNTEMİ: Streamlit secrets yapısından 'GEMINI_API_KEY' adıyla çekiyoruz.
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


# --- 4. STREAMLIT ARYÜZÜ ---

st.title("🎓 Altınoluk MYO Bilgisayar Programcılığı Asistanı")
st.caption("Bu chatbot, özetleme ve isteğe bağlı sesli geri bildirim özelliğine sahiptir.")
st.caption("📌 **Kullanım Amacı:** Bu Yapay Zeka Asistanı, sadece **Altınoluk MYO** ve **Bilgisayar Programcılığı Bölümü** hakkındaki verilere dayanarak cevap üretir. Konu dışı sorular yanıtlanmayacaktır.")

# Geçmiş mesajları görüntüle
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
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
    with st.chat_message("user"):
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
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Sayfanın tekrar çizilmesini sağlamak için
    st.rerun()
