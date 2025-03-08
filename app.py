# app.py
from flask import Flask, render_template, request, redirect, url_for
import re
from collections import defaultdict

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 限制上传文件为2MB


@app.errorhandler(413)
def request_entity_too_large(error):
    return "File size exceeds 2MB limit", 413

# 分析函数
def analyze_map(content):
    section_pattern = re.compile(
        r'^\s*(\.\S+)\s+0x[0-9a-f]+\s+(0x[0-9a-f]+|\d+)\s+([^\s]+\.o)'
    )
    file_sections = defaultdict(lambda: defaultdict(int))
    
    for line in content.split('\n'):
        match = section_pattern.search(line)
        if match:
            section = match.group(1)
            size_str = match.group(2)
            filename = match.group(3)
            size = int(size_str, 16) if size_str.startswith('0x') else int(size_str)
            file_sections[filename][section] += size
    
    return {f: dict(s) for f, s in file_sections.items()}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'map_file' not in request.files:
            return redirect(request.url)
        
        file = request.files['map_file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and file.filename.endswith('.map'):
            content = file.read().decode('utf-8')
            result = analyze_map(content)
            return render_template('result.html', result=result)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)