import streamlit as st
import pandas as pd
from googletrans import Translator
from gtts import gTTS
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
from playsound import playsound as PS

# Streamlit App Title
st.title("Batch Translation and Live Speech Translation")

# Initialize Google Translator
translator = Translator()

# Language Dictionary
language_dict = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy',
    'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs',
    'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn',
    'chinese (traditional)': 'zh-tw', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da',
    'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi',
    'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el',
    'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi',
    'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'italian': 'it', 'japanese': 'ja',
    'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'lao': 'lo',
    'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms',
    'malayalam': 'ml', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no',
    'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro',
    'russian': 'ru', 'serbian': 'sr', 'sesotho': 'st', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl',
    'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg',
    'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uzbek': 'uz',
    'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'
}

# Section 1: Batch Translation
st.header("Batch Translation from CSV")

# File Upload
uploaded_file = st.file_uploader("Upload a CSV file containing the text to translate:", type="csv")

# Select Target Language
target_language = st.selectbox("Select the target language for translation:", options=language_dict.keys())
target_language_code = language_dict[target_language.lower()]

if uploaded_file is not None:
    # Read CSV
    data = pd.read_csv(uploaded_file)

    # Display Uploaded Data
    st.subheader("Uploaded Data:")
    st.dataframe(data)

    # Check if 'text' column exists
    if "text" not in data.columns:
        st.error("The column 'text' is not found in the uploaded CSV.")
    else:
        # Translate All Rows
        translated_texts = []
        for _, row in data.iterrows():
            text_to_translate = row["text"]
            if pd.isna(text_to_translate):
                translated_texts.append(None)
            else:
                translation = translator.translate(text_to_translate, dest=target_language_code)
                translated_texts.append(translation.text)

        # Add Translated Column
        data["Translated_Text"] = translated_texts

        # Display Translated Data
        st.subheader("Translated Data:")
        st.dataframe(data)

        # Download Updated CSV
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Translated CSV", data=csv, file_name="translated_data.csv", mime="text/csv")

        # Generate Audio Files (Optional)
        generate_audio = st.checkbox("Generate audio for each translated text (may take time)")
        if generate_audio:
            for index, translated_text in enumerate(data["Translated_Text"]):
                if pd.notna(translated_text):
                    tts = gTTS(text=translated_text, lang=target_language_code, slow=False)
                    audio_file = f"audio_{index}.mp3"
                    tts.save(audio_file)
                    st.audio(audio_file)
                    os.remove(audio_file)

# Section 2: Live Speech Translation
st.header("Live Speech Translation")

# Initialize session state variables if they don't exist
if "recognized_text" not in st.session_state:
    st.session_state["recognized_text"] = ""
if "translated_text" not in st.session_state:
    st.session_state["translated_text"] = ""

# Speech Recognition Processor
class SpeechRecognitionProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv(self, frame):
        audio_data = sr.AudioData(frame.to_ndarray().tobytes(), frame.samplerate, frame.sample_width)
        try:
            # Recognize speech
            recognized_text = self.recognizer.recognize_google(audio_data, language="en")
            st.session_state["recognized_text"] = recognized_text
            # Translate speech
            translation = translator.translate(recognized_text, dest=target_language_code)
            st.session_state["translated_text"] = translation.text
        except sr.UnknownValueError:
            st.session_state["recognized_text"] = "Could not understand audio."
            st.session_state["translated_text"] = ""
        except sr.RequestError as e:
            st.session_state["recognized_text"] = f"Speech recognition error: {e}"
            st.session_state["translated_text"] = ""

# Streamlit WebRTC Component for live speech
webrtc_ctx = webrtc_streamer(
    key="speech-translation",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=SpeechRecognitionProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# Display Recognized Speech and Translated Text
if "recognized_text" in st.session_state and st.session_state["recognized_text"]:
    st.subheader("Recognized Speech:")
    st.write(st.session_state["recognized_text"])

if "translated_text" in st.session_state and st.session_state["translated_text"]:
    st.subheader("Translated Text:")
    st.write(st.session_state["translated_text"])

    # Generate and Play Audio for Translated Text in the Target Language
    tts = gTTS(text=st.session_state["translated_text"], lang=target_language_code, slow=False)
    tts.save("translated_audio.mp3")
    st.audio("translated_audio.mp3")
    os.remove("translated_audio.mp3")

# Voice-based translation (for offline usage or command-based triggering)
def take_command():
    r1 = sr.Recognizer()
    with sr.Microphone() as source:
        r1.pause_threshold = 2
        r1.energy_threshold = 300
        try:
            audio1 = r1.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            return "None"

    try:
        query_1 = r1.recognize_google(audio1, language='en-in')
        return query_1
    except sr.UnknownValueError:
        return "None"
    except sr.RequestError:
        return "None"

def destination_language():
    print("Please enter the language in which you want to convert the input:")
    to_language = take_command().lower()
    while to_language == "None" or to_language not in language_dict:
        print("The language you selected is not available. Please input another language.")
        to_language = take_command().lower()