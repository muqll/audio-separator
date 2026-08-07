import os
from flask import Blueprint, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from services.spleeter_service import SpleeterSeparatorService

audio_bp = Blueprint('audio', __name__)

UPLOAD_FOLDER = os.path.abspath('temp_uploads')
OUTPUT_FOLDER = os.path.abspath('temp_output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# حقن الخدمة (Dependency Injection)
separator_service = SpleeterSeparatorService()

@audio_bp.route('/api/separate', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'لم يتم العثور على ملف مرفق'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'اسم الملف غير صحيح'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        results = separator_service.separate(input_path, OUTPUT_FOLDER)
        file_stem = os.path.splitext(filename)[0]

        # إنشاء روابط لتنزيل الملفات عبر الـ Frontend
        vocal_url = url_for('audio.get_processed_file', folder=file_stem, filename='vocals.wav', _external=True)
        music_url = url_for('audio.get_processed_file', folder=file_stem, filename='accompaniment.wav', _external=True)

        return jsonify({
            'message': 'تم فصل الصوت بنجاح',
            'vocal_url': vocal_url,
            'music_url': music_url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@audio_bp.route('/media/<folder>/<filename>', methods=['GET'])
def get_processed_file(folder, filename):
    folder_path = os.path.join(OUTPUT_FOLDER, folder)
    return send_from_directory(folder_path, filename)