from flask import Flask, render_template_string, request, jsonify
import eng_to_ipa as ipa
import speech_recognition as sr
import io
from pydub import AudioSegment
from langdetect import detect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string(open('index.html').read())

def convert_to_wav(audio_bytes, audio_format):
    audio_data = io.BytesIO(audio_bytes)
    audio_segment = AudioSegment.from_file(audio_data, format=audio_format)
    wav_io = io.BytesIO()
    audio_segment.export(wav_io, format='wav')
    wav_io.seek(0)
    return wav_io

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

    audio_file = request.files['audio'].read()
    audio_format = request.files['audio'].content_type.split('/')[1]

    if audio_format not in ['wav', 'ogg']:
        return jsonify({'error': 'Please upload an uncompressed audio format like .WAV or .OGG'}), 400

    try:
        audio_data = convert_to_wav(audio_file, audio_format)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_data) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        language = detect(text)
        
        if language == 'en':
            ipa_transcription = ipa.convert(text)
        else:
            ipa_transcription = custom_ipa_mapping(text)

        return jsonify({'ipa': ipa_transcription})
    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Could not request results from Google Speech Recognition service; {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
