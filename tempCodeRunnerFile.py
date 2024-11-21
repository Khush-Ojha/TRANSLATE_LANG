import os
from playsound import playsound as PS
import speech_recognition as s_r
from googletrans import Translator as Trans
from gtts import gTTS

# Dictionary mapping language names to codes for Google Translate
language_dict = {
    'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy',
    'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs',
    'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn',
    'chinese (traditional)': 'zh-tw', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da',
    'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi',
    'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el',
    'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi',
    'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig'
}

# Capture the user's voice command
def take_command():
    r1 = s_r.Recognizer()
    with s_r.Microphone() as source:
        print("Listening to the voice...")
        r1.pause_threshold = 2  # Increase to allow pauses between words
        r1.energy_threshold = 300  # Adjust microphone sensitivity if necessary
        try:
            audio1 = r1.listen(source, timeout=5, phrase_time_limit=10)  # Configure timeout limits
        except s_r.WaitTimeoutError:
            print("No speech detected. Please try again.")
            return "None"

    try:
        print("Recognizing the voice...")
        query_1 = r1.recognize_google(audio1, language='en-in')
        print(f"User said: {query_1}\n")
    except s_r.UnknownValueError:
        print("Sorry, I could not understand audio. Please speak again.")
        return "None"
    except s_r.RequestError:
        print("Could not request results from the speech recognition service.")
        return "None"
    return query_1

# Get the user's language choice for translation
def destination_language():
    print("Please enter the language in which you want to convert the input (e.g., English, Hindi, German, French, etc.):\n")
    to_language = take_command().lower()
    while to_language == "None" or to_language not in language_dict:
        print("The language you selected is not available. Please input another language.")
        to_language = take_command().lower()
    return to_language

# Main function
def main():
    # Get the destination language from the user
    to_language = destination_language()

    # Capture the user's speech input to translate
    print("Please say the text you want to translate.")
    query_1 = take_command()  # This is where the actual user input (e.g., "hello") is captured
    if query_1 == "None":
        return

    # Map language to its corresponding code
    to_language_code = language_dict[to_language]

    # Initialize Google Translator and perform translation
    translator1 = Trans()
    text_to_translate = translator1.translate(query_1, dest=to_language_code)
    translated_text = text_to_translate.text
    print(f"Translated Text: {translated_text}")

    # Use Google Text-to-Speech to generate audio of the translated text
    speak = gTTS(text=translated_text, lang=to_language_code, slow=False)
    speak.save("captured_voice.mp3")

    # Play the translated voice and delete the audio file afterward
    PS("captured_voice.mp3")
    os.remove("captured_voice.mp3")

# Run the program
if __name__ == "__main__":
    main()