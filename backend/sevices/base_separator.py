from abc import ABC, abstractmethod
from typing import Dict

class BaseAudioSeparator(ABC):
    """
    Abstract Base Class (Interface) لتطبيق مبدأ Dependency Inversion (DIP)
    يتيح تغيير أداة الفصل المستقبلي (Demucs, Spleeter, etc.) دون المساس بالـ Controller.
    """

    @abstractmethod
    def separate(self, input_file_path: str, output_directory: str) -> Dict[str, str]:
        """
        تأخذ مسار الملف المدخل ومسار مجلد المخرجات،
        وترجع Dict يحوي مسار الصوت النقّي (vocals) ومسار الموسيقى (accompaniment).
        """
        pass