from flask import Flask, render_template, request, jsonify
import eng_to_ipa as ipa
import speech_recognition as sr
import os
from pydub import AudioSegment
import langdetect
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def custom_ipa_mapping(text):
    ipa_map = {
        'a': 'ɑ', 'b': 'b', 'c': 'k', 'd': 'd',
        'e': 'ɛ', 'f': 'f', 'g': 'ɡ', 'h': 'h',
        'i': 'ɪ', 'j': 'd͡ʒ', 'k': 'k', 'l': 'l',
        'm': 'm', 'n': 'n', 'o': 'oʊ', 'p': 'p',
        'q': 'k', 'r': 'ɹ', 's': 's', 't': 't',
        'u': 'ʊ', 'v': 'v', 'w': 'w', 'x': 'ks',
        'y': 'j', 'z': 'z',
        'th': 'θ', 'dh': 'ð', 'sh': 'ʃ', 'zh': 'ʒ',
        'ch': 'tʃ', 'jh': 'dʒ', 'ng': 'ŋ', 'ph': 'f',
        'gh': 'ɡ', 'kh': 'k', 'wh': 'w', 'ck': 'k',
        'qu': 'kw', 'tion': 'ʃən', 'sch': 'ʃ',
        'ea': 'iːə', 'ee': 'iː', 'ai': 'aɪ', 'ay': 'eɪ',
        'oa': 'oʊ', 'oo': 'uː', 'ou': 'aʊ', 'oy': 'ɔɪ',
        'au': 'ɑʊ', 'aw': 'ɔ', 'ew': 'ju', 'oi': 'ɔɪ',
        'ow': 'oʊ', 'ph': 'f', 'gh': 'ɡ', 'ch': 'tʃ',
        'th': 'θ', 'sh': 'ʃ', 'zh': 'ʒ', 'ng': 'ŋ',
        'x': 'ks', 'wh': 'w', 'ck': 'k', 'qu': 'kw',
        'tion': 'ʃən', 'sch': 'ʃ', 'qu': 'kw', 'sch': 'ʃ'
    }

    def handle_phonetic_combinations(ipa_text):
        replacements = {
            't͡ʃ': 'tʃ', 'd͡ʒ': 'dʒ', 'aɪ': 'aɪ', 'eɪ': 'eɪ',
            'oʊ': 'oʊ', 'aʊ': 'aʊ', 'ju': 'ju', 'ɔɪ': 'ɔɪ',
            'iːə': 'iːə'
        }
        for old, new in replacements.items():
            ipa_text = ipa_text.replace(old, new)
        return ipa_text

    lowercase_text = text.lower()
    ipa_text = ''
    i = 0
    while i < len(lowercase_text):
        if i < len(lowercase_text) - 1 and lowercase_text[i:i+2] in ipa_map:
            ipa_text += ipa_map[lowercase_text[i:i+2]]
            i += 2
        elif i < len(lowercase_text) - 2 and lowercase_text[i:i+3] in ipa_map:
            ipa_text += ipa_map[lowercase_text[i:i+3]]
            i += 3
        elif lowercase_text[i] in ipa_map:
            ipa_text += ipa_map[lowercase_text[i]]
            i += 1
        else:
            ipa_text += lowercase_text[i]
            i += 1

    ipa_text = handle_phonetic_combinations(ipa_text)
    return ipa_text

@app.route('/convert', methods=['POST'])
def convert_to_ipa_route():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    try:
        audio_file = request.files['audio']
        audio_format = audio_file.filename.rsplit('.', 1)[1].lower()

        # Save the file temporarily using NamedTemporaryFile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format}') as temp_audio_file:
            audio_file.save(temp_audio_file.name)
            temp_audio_filepath = temp_audio_file.name

        # Check if the file exists after saving
        if not os.path.exists(temp_audio_filepath):
            return jsonify({'error': 'File not saved correctly'}), 500

        # Check if the uploaded file is WAV, if not convert to WAV
        if audio_format != 'wav':
            audio = AudioSegment.from_file(temp_audio_filepath, format=audio_format)
            temp_wav_filepath = temp_audio_filepath.replace(f'.{audio_format}', '.wav')
            audio.export(temp_wav_filepath, format='wav')
        else:
            temp_wav_filepath = temp_audio_filepath

        # Recognize speech from the WAV file
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_filepath) as source:
            audio_data = recognizer.record(source)

            # Perform speech recognition
            recognized_text = recognizer.recognize_google(audio_data)
            language = langdetect.detect(recognized_text)

            # Convert recognized text to IPA
            if language == 'en':
                ipa_transcription = ipa.convert(recognized_text)
            else:
                ipa_transcription = custom_ipa_mapping(recognized_text)

        # Cleanup - remove temporary files
        os.remove(temp_audio_filepath)
        if temp_wav_filepath != temp_audio_filepath:
            os.remove(temp_wav_filepath)

        return jsonify({'ipa': ipa_transcription})

    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Could not request results from Google Speech Recognition service; {e}'}), 500
    except langdetect.LangDetectException as e:
        return jsonify({'error': f'Language detection error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
