from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
import json
import os
import uuid
import time
import threading

app = Flask(__name__, template_folder='.')

# Clean up temp files every 12 hours
CLEANUP_INTERVAL = 12 * 3600

def load_templates():
    with open('templates.json', 'r') as file:
        return json.load(file)

templates = load_templates()

def load_latest_served(session_id):
    session_file = os.path.join('.temp_templates', 'sessions', f"{session_id}.json")
    if os.path.exists(session_file):
        with open(session_file, 'r') as file:
            return json.load(file)
    return {}

def save_latest_served(session_id, data):
    session_file = os.path.join('.temp_templates', 'sessions', f"{session_id}.json")
    with open(session_file, 'w') as file:
        json.dump(data, file)

def clean_old_templates():
    print("Cleaning up temp files...")
    current_time = time.time()
    for filename in os.listdir('.temp_templates'):
        if filename.endswith('.html'):
            filepath = os.path.join('.temp_templates', filename)
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > CLEANUP_INTERVAL:
                os.remove(filepath)
    
    session_dir = os.path.join('.temp_templates', 'sessions')
    for filename in os.listdir(session_dir):
        filepath = os.path.join(session_dir, filename)
        file_age = current_time - os.path.getmtime(filepath)
        if file_age > CLEANUP_INTERVAL:
            os.remove(filepath)

# Clean up temp files periodically
def start_cleanup_thread():
    while True:
        clean_old_templates()
        time.sleep(CLEANUP_INTERVAL)

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    
    latest_served = load_latest_served(session_id)
    temp_files = os.listdir('.temp_templates')
    
    response = make_response(render_template('index.html', templates=templates, temp_files=temp_files, latest_served=latest_served))
    response.set_cookie('session_id', session_id)
    return response

@app.route('/template/<template_name>')
def show_template(template_name):
    if template_name in templates:
        return render_template(templates[template_name]['path'])
    else:
        return "Template not found", 404

@app.route('/temp/<temp_id>')
def show_temp_template(temp_id):
    return send_from_directory('.temp_templates', f"{temp_id}.html")

@app.route('/get_template_html/<template_name>', methods=['GET'])
def get_template_html(template_name):
    if template_name in templates:
        with open(os.path.join('templates', templates[template_name]['path']), 'r') as file:
            html_content = file.read()
        return jsonify({"html": html_content}), 200
    else:
        return jsonify({"error": "Template not found"}), 404

@app.route('/get_temp_template_html', methods=['GET'])
def get_temp_template_html():
    temp_id = request.cookies.get('session_id')
    temp_path = f"{temp_id}.html"
    try:
        with open(os.path.join('.temp_templates', temp_path), 'r') as file:
            html_content = file.read()
        return jsonify({"html": html_content}), 200
    except FileNotFoundError:
        return jsonify({"error": "Template not found"}), 404

@app.route('/add_template', methods=['POST'])
def add_template():
    new_template = request.json
    template_name = new_template['name']
    template_description = new_template['description']
    template_html = new_template['html']

    # Save the HTML template
    template_path = f"{template_name}.html"
    with open(os.path.join('templates', template_path), 'w') as file:
        file.write(template_html)

    # Update the templates JSON
    templates[template_name] = {
        'description': template_description,
        'path': template_path
    }
    with open('templates.json', 'w') as file:
        json.dump(templates, file, indent=4)

    return jsonify({"message": "Template added successfully!"}), 200

@app.route('/serve_template', methods=['POST'])
def serve_template():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({"error": "No session ID found"}), 400

    latest_served = load_latest_served(session_id)
    
    template_html = request.json['html']
    temp_path = f"{session_id}.html"
    with open(os.path.join('.temp_templates', temp_path), 'w') as file:
        file.write(template_html)
        latest_served['html'] = template_html

    latest_served = load_latest_served(session_id)
    
    latest_served['temp_id'] = session_id
    save_latest_served(session_id, latest_served)

    return jsonify({"message": "Template served successfully!", "temp_id": session_id}), 200

@app.route('/delete_temp_template/<temp_id>', methods=['DELETE'])
def delete_temp_template(temp_id):
    temp_path = f"{temp_id}.html"
    try:
        os.remove(os.path.join('.temp_templates', temp_path))
        session_id = request.cookies.get('session_id')
        if session_id:
            latest_served = load_latest_served(session_id)
            if latest_served.get('temp_id') == temp_id:
                latest_served.clear()
                save_latest_served(session_id, latest_served)
        return jsonify({"message": "Temporary template deleted successfully!"}), 200
    except FileNotFoundError:
        return jsonify({"error": "Template not found"}), 404

if __name__ == '__main__':
    if not os.path.exists('.temp_templates'):
        os.makedirs('.temp_templates')
    if not os.path.exists(os.path.join('.temp_templates', 'sessions')):
        os.makedirs(os.path.join('.temp_templates', 'sessions'))

    cleanup_thread = threading.Thread(target=start_cleanup_thread)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    app.run(debug=True)
