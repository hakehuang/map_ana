# app.py
from flask import Flask, render_template, request
from elftools.elf.elffile import ELFFile
import os

app = Flask(__name__)

def extract_object_file_info(elfpath):
    object_files_info = []
    with open(elfpath, 'rb') as f:
        elffile = ELFFile(f)
        for section in elffile.iter_sections():
            if section.name.startswith('.text') or section.name.startswith('.data') or section.name.startswith('.rodata'):
                obj_info = {
                    'name': section.name,
                    'address': hex(section['sh_addr']),
                    'size': section['sh_size'],
                    'offset': section['sh_offset'],
                    'flags': section['sh_flags']
                }
                object_files_info.append(obj_info)
    return object_files_info

@app.route('/', methods=['GET', 'POST'])
def index():
    object_files_info = []
    error = None
    if request.method == 'POST':
        if 'elf_file' not in request.files:
            error = 'No file part'
            return render_template('index.html', error=error)
        file = request.files['elf_file']
        if file.filename == '':
            error = 'No selected file'
            return render_template('index.html', error=error)
        if file:
            filename = file.filename
            filepath = os.path.join('./uploads', filename)
            file.save(filepath)
            object_files_info = extract_object_file_info(filepath)
            if request.form.get('sort') == 'size':
                object_files_info.sort(key=lambda x: x['size'], reverse=True)
    return render_template('index.html', object_files_info=object_files_info, error=error)

if __name__ == '__main__':
    app.run(debug=True)
