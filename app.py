from flask import Flask, request, send_file, jsonify
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

@app.route('/')
def home():
    return """
    <h1>✅ PDF Processing Service is Running!</h1>
    <p>Send POST request to /process with a PDF file</p>
    <form action="/process" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf">
        <button type="submit">Upload PDF</button>
    </form>
    """

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/process', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        result = subprocess.run(
            ['python3', 'process_pdf.py', input_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500
        
        output_path = result.stdout.strip()
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output file not found'}), 500
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f'processed_{filename}'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
```

4. اضغط **"Commit changes"**

---

### **3.4 - رفع الصور المائية (1.jpg و 2.pdf)**

الآن نحتاج رفع صورك:

1. اضغط **"Add file"** → **"Upload files"**
2. اسحب أو اختر ملف `1.jpg`
3. اضغط **"Commit changes"**
4. كرر العملية مع ملف `2.pdf`

✅ **هل رفعت الصورتين؟**

---

## **الخطوة 4: ربط GitHub مع Render**

1. ارجع إلى **Render.com**
2. اضغط **"New +"** في الأعلى
3. اختر **"Web Service"**
4. اضغط **"Connect GitHub"** (سيطلب منك تسجيل الدخول لـ GitHub)
5. اختر الـ repository: `whatsapp-pdf-processor`
6. اضغط **"Connect"**

---

## **الخطوة 5: إعدادات Render**

املأ المعلومات التالية:

- **Name:** `pdf-processor` (أي اسم تريده)
- **Region:** اختر الأقرب لك
- **Branch:** `main`
- **Runtime:** **Python 3**
- **Build Command:** 
```
  pip install -r requirements.txt
```
- **Start Command:**
```
  gunicorn app:app
