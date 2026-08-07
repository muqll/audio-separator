import os
import subprocess
from typing import Dict
from .base_separator import BaseAudioSeparator

class SpleeterSeparatorService(BaseAudioSeparator):
    def __init__(self, stems: str = "spleeter:2stems"):
        self.stems = stems

    def separate(self, input_file_path: str, output_directory: str) -> Dict[str, str]:
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"الملف غير موجود: {input_file_path}")

        # أمر تشغيل spleeter عبر السطر البرمجي
        command = [
            "spleeter", "separate",
            "-p", self.stems,
            "-o", output_directory,
            input_file_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"فشلت عملية الفصل عبر Spleeter: {result.stderr}")

        file_stem = os.path.splitext(os.path.basename(input_file_path))[0]
        vocal_path = os.path.join(output_directory, file_stem, "vocals.wav")
        music_path = os.path.join(output_directory, file_stem, "accompaniment.wav")

        if not os.path.exists(vocal_path) or not os.path.exists(music_path):
            raise FileNotFoundError("لم يتم العثور على الملفات الناتجة عن المعالجة")

        return {
            "vocal": vocal_path,
            "music": music_path
        }