# Docker Update Manager

A web-based tool for managing and updating Docker containers. This application provides a simple interface to update Docker containers using either docker-compose or custom run commands.

## 🚀 Features

- Web interface for Docker container management
- Support for both docker-compose and custom Docker run commands
- Directory browsing functionality
- RESTful API endpoints
- Cross-platform compatibility (Windows, Unix)

## 📋 Requirements

- Python 3.x
- Docker
- Docker Compose (for docker-compose.yml configurations)
- Flask (Python web framework)

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd docker-update-manager
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Start the web server:
```bash
python server.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Browse directories
   - Select Docker configuration locations
   - Update Docker containers

### Command Line Usage

You can also use the Docker manager directly from the command line:

```bash
python docker_manager.py <path-to-docker-config>
```

## 📁 File Structure

- `server.py` - Flask web server implementation
- `docker_manager.py` - Core Docker management functionality
- `requirements.txt` - Python package dependencies
- `static/index.html` - Web interface
- `index.html` - Source template for web interface

## 🔌 API Endpoints

### GET /list-directories
Lists all directories in the specified path.

**Query Parameters:**
- `path`: The directory path to list

**Response:**
```json
["directory1", "directory2", ...]
```

### POST /update-docker
Updates Docker container(s) in the specified path.

**Request Body:**
```json
{
    "path": "/path/to/docker/config"
}
```

**Response:**
```json
{
    "success": true,
    "error": null
}
```

## 🐳 Docker Configuration Support

The application supports two types of Docker configurations:

1. **docker-compose.yml**
   - Automatically handles `down`, `pull`, and `up -d` operations
   - Must be a valid docker-compose configuration file

2. **docker-run-command.txt**
   - Contains a single Docker run command
   - Used when docker-compose is not available
   - Must contain a valid Docker run command

## 🔒 Security Considerations

- Ensure proper permissions for Docker access
- Validate paths before processing
- Restrict access to authorized users in production environments

## 💡 Best Practices

1. Always use version control for Docker configurations
2. Regularly backup your Docker configurations
3. Test updates in a staging environment first
4. Monitor container logs after updates

## ⚠️ Error Handling

The application includes comprehensive error handling for:
- Invalid paths
- Missing configuration files
- Docker command failures
- File system permissions
- Network issues

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is open source and available under the MIT License.
