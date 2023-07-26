from flask import Flask, render_template, request, jsonify
import os
import inspect
import shutil
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        project_path = request.form.get('project_path')
        if project_path:
            project_structure = get_project_structure(project_path)
            return jsonify(project_structure=project_structure)
        elif 'project_file' in request.files:
            project_file = request.files['project_file']
            if project_file.filename.endswith(('.zip', '.tar', '.tar.gz')):
                project_path = os.path.join(app.config['UPLOAD_FOLDER'], project_file.filename)
                project_file.save(project_path)
                project_structure = get_project_structure(project_path)
                return jsonify(project_structure=project_structure)
            else:
                return jsonify(error='Invalid file format. Please upload a compressed archive file.')
    return render_template('form.html')

def get_project_structure(project_path):
    project_structure = []
    for root, dirs, files in os.walk(project_path):
        level = root.replace(project_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        project_structure.append({'name': '{}{}/'.format(indent, os.path.basename(root)), 'classes': [], 'functions': []})
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                classes, functions = get_file_structure(file_path)
                project_structure[-1]['classes'].extend(classes)
                project_structure[-1]['functions'].extend(functions)
    return project_structure

def get_file_structure(file_path):
    classes = []
    functions = []
    with open(file_path, 'r') as file:
        source_code = file.read()
        module = compile(source_code, file_path, 'exec')
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                classes.append(obj.__name__)
            elif inspect.isfunction(obj):
                functions.append(obj.__name__)
    return classes, functions

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run()
