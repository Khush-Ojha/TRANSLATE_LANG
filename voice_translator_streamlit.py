import streamlit as st
import pandas as pd
from googletrans import Translator
from gtts import gTTS
import os

# Streamlit App Title
st.title("Batch Translation Application")

# File Upload
uploaded_file = st.file_uploader("Upload a CSV file containing the text to translate:", type="csv")

# Select Target Language
language_dict = {'english': 'en', 'hindi': 'hi', 'french': 'fr', 'german': 'de', 'spanish': 'es'}  # Add more as needed
target_language = st.selectbox("Select the target language:", options=language_dict.keys())
target_language_code = language_dict[target_language.lower()]

if uploaded_file is not None:
    # Read CSV
    data = pd.read_csv(uploaded_file)
    
    # Display Data Preview
    st.subheader("Uploaded Data:")
    st.dataframe(data)
    
    # Check if 'text' column exists
    if "text" not in data.columns:
        st.error("The column 'text' is not found in the uploaded CSV.")
    else:
        # Translate All Rows
        translator = Translator()
        translated_texts = []

        # Iterate through each row to translate all lines
        for _, row in data.iterrows():
            text_to_translate = row["text"]
            if pd.isna(text_to_translate):
                translated_texts.append(None)
            else:
                # Translate each line (row's text) individually
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
