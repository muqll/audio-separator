const audioInput = document.getElementById('audio-input');
const fileNameDisplay = document.getElementById('file-name');
const processBtn = document.getElementById('process-btn');
const statusText = document.getElementById('status-text');

const vocalsPlayer = document.getElementById('vocals-player');

const downloadSection = document.getElementById('download-section');
const downloadVocalsBtn = document.getElementById('download-vocals-btn');
const downloadVideoBtn = document.getElementById('download-video-btn');

let selectedFile = null;

audioInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileNameDisplay.textContent = `الملف المختار: ${selectedFile.name}`;
        statusText.textContent = "";
        downloadSection.style.display = 'none';
        downloadVideoBtn.style.display = 'none';
    }
});

processBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert("من فضلك اختر ملفاً أولاً!");
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    statusText.textContent = "جاري عزل الصوت والذكاء الاصطناعي يعمل... قد يستغرق دقيقة ⏳";
    statusText.style.color = "#00d2ff";
    processBtn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/separate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            statusText.textContent = "🎉 تم عزل الصوت بنجاح بواسطة Madar Engine!";
            statusText.style.color = "#00ff88";

            vocalsPlayer.src = data.vocals_url;
            vocalsPlayer.load();

            // زر تحميل الصوت بدون موسيقى
            downloadVocalsBtn.href = data.vocals_url;

            // زر تحميل الفيديو بدون موسيقى (في حال رفع فيديو)
            if (data.video_url) {
                downloadVideoBtn.href = data.video_url;
                downloadVideoBtn.style.display = 'inline-block';
            } else {
                downloadVideoBtn.style.display = 'none';
            }

            downloadSection.style.display = 'flex';
        } else {
            statusText.textContent = "حدث خطأ: " + (data.error || "تعذر المعالجة");
            statusText.style.color = "#ff4d4d";
        }
    } catch (error) {
        console.error("Error:", error);
        statusText.textContent = "خطأ في الاتصال بالسيرفر! تأكد أن سيرفر Python شغال.";
        statusText.style.color = "#ff4d4d";
    } finally {
        processBtn.disabled = false;
    }
});