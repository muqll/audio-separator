import os
import sys
import subprocess
import warnings
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import static_ffmpeg

warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def create_app() -> Flask:
    static_ffmpeg.add_paths()
    
    app = Flask(__name__)
    CORS(app)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'separated')
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"status": "success", "message": "Madar Engine Operational"})

    @app.route('/downloads/<path:filename>')
    def download_file(filename):
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

    @app.route('/separate', methods=['POST'])
    def separate_audio():
        if 'file' not in request.files:
            return jsonify({"error": "لم يتم رفع أي ملف"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "اسم الملف فارغ"}), 400

        # تسمية آمنة للملف المرفوع
        file_ext = os.path.splitext(file.filename)[1].lower()
        if not file_ext:
            file_ext = '.mp4'
            
        unique_id = str(uuid.uuid4())[:8]
        safe_base_name = f"media_{unique_id}"
        safe_filename = f"{safe_base_name}{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)

        try:
            python_exe = sys.executable
            cmd = [
                python_exe, "-m", "demucs.separate",
                "--two-stems=vocals",
                "-n", "htdemucs",
                "--shifts=1",
                "-o", app.config['OUTPUT_FOLDER'],
                filepath
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # المسار الحقيقي المتوقع للصوت البشري المفصول
            vocals_path = os.path.join(app.config['OUTPUT_FOLDER'], 'htdemucs', safe_base_name, 'vocals.wav')

            if not os.path.exists(vocals_path):
                # البحث في حال اختلاف المسار
                found_vocals = None
                for root, dirs, files in os.walk(app.config['OUTPUT_FOLDER']):
                    if 'vocals.wav' in files and safe_base_name in root:
                        found_vocals = os.path.join(root, 'vocals.wav')
                        break
                if found_vocals:
                    vocals_path = found_vocals
                else:
                    return jsonify({"error": "تعذر العثور على المقطع الصوتي المفصول."}), 500

            clean_audio_name = f"audio_no_music_{unique_id}.wav"
            final_vocals_path = os.path.join(app.config['OUTPUT_FOLDER'], clean_audio_name)
            
            if os.path.exists(final_vocals_path):
                os.remove(final_vocals_path)
            os.replace(vocals_path, final_vocals_path)

            vocals_url = f"http://127.0.0.1:5000/downloads/{clean_audio_name}"
            video_url = None

            # إن كان الملف فيديو، ندمج الصوت النقي مع الفيديو الأصلي
            if file_ext in ['.mp4', '.mkv', '.mov', '.avi', '.webm']:
                clean_video_name = f"video_no_music_{unique_id}.mp4"
                final_video_path = os.path.join(app.config['OUTPUT_FOLDER'], clean_video_name)

                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", filepath,
                    "-i", final_vocals_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    final_video_path
                ]
                subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                video_url = f"http://127.0.0.1:5000/downloads/{clean_video_name}"

            return jsonify({
                "status": "success",
                "message": "Processed successfully",
                "vocals_url": vocals_url,
                "video_url": video_url
            })

        except Exception as ex:
            print("General Error:", str(ex))
            return jsonify({"error": "حدث خطأ أثناء معالجة الملف، جرب ملفًا آخر"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)