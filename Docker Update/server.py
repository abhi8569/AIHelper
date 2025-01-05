from flask import Flask, jsonify, request
import os
import sys

# Add parent directory to Python path to import docker_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
docker_manager_path = os.path.join('docker_manager.py')

# Import the update_docker_container function
import importlib.util
spec = importlib.util.spec_from_file_location("docker_manager", docker_manager_path)
docker_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docker_manager)
update_docker_container = docker_manager.update_docker_container

app = Flask(__name__)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/list-directories')
def list_directories():
    try:
        path = request.args.get('path', '')
        if not path:
            return jsonify({'error': 'No path provided'})
        
        # Get all directories in the specified path
        directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return jsonify(directories)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/update-docker', methods=['POST'])
def update_docker():
    try:
        path = request.json.get('path')
        if not path:
            return jsonify({'error': 'No path provided'})
        
        success, error = update_docker_container(path)
        return jsonify({
            'success': success,
            'error': error if error else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Ensure the static folder exists
    os.makedirs('static', exist_ok=True)
    # Copy index.html to static folder
    import shutil
    shutil.copy('index.html', 'static/index.html')
    # Run the server
    app.run(debug=True)
