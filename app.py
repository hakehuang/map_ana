from flask import Flask, render_template, request, redirect, url_for
import re
from collections import defaultdict

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

DEBUG_SECTIONS = sorted({
    '.debug', '.debug_info', '.debug_abbrev', '.debug_line',
    '.debug_str', '.comment', '.note.GNU-stack', '.stab',
    '.stabstr', '.gnu.build.attributes'
})  # sorted() 返回排序后的列表

def analyze_map(content, exclude_debug=False):
    try:
        section_pattern = re.compile(r'^\s*(\.\S+)\s+0x[0-9a-f]+\s+(0x[0-9a-f]+|\d+)\s+([^\s]+\.o)')
        file_sections = defaultdict(lambda: defaultdict(int))
        
        for line in content.split('\n'):
            match = section_pattern.search(line)
            if match:
                section, size_str, filename = match.groups()
                if exclude_debug and section in DEBUG_SECTIONS:
                    continue
                size = int(size_str, 16) if size_str.startswith('0x') else int(size_str)
                file_sections[filename][section] += size
        return {f: dict(s) for f, s in file_sections.items()}
    except Exception as e:
        print(f"Analysis Error: {str(e)}")
        return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            if 'map_file' not in request.files:
                return redirect(request.url)
            
            file = request.files['map_file']
            if file.filename == '':
                return redirect(request.url)
            
            if file and file.filename.endswith('.map'):
                exclude_debug = request.form.get('exclude_debug') == 'on'
                content = file.read().decode('utf-8')
                result = analyze_map(content, exclude_debug)
                return render_template('result.html',
                                        result=result,
                                        exclude_debug=exclude_debug,
                                        DEBUG_SECTIONS=DEBUG_SECTIONS)
        return render_template('upload.html')
    except Exception as e:
        print(f"Route Error: {str(e)}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # 显式指定host和port