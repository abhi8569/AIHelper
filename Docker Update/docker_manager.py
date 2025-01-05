import os
import subprocess
from typing import Optional


def update_docker_container(path: str) -> tuple[bool, Optional[str]]:
    """
    Check for Docker configuration files and manage container accordingly.
    
    Args:
        path (str): Path to the directory containing Docker configuration files
        
    Returns:
        tuple[bool, Optional[str]]: A tuple containing:
            - bool: True if operation was successful, False otherwise
            - Optional[str]: Error message if operation failed, None if successful
    """
    try:
        # Ensure the path exists and is a directory
        if not os.path.isdir(path):
            return False, f"Invalid path: {path} is not a directory"
        
        # Check for docker-compose.yml
        compose_path = os.path.join(path, "docker-compose.yml")
        run_command_path = os.path.join(path, "docker-run-command.txt")
        
        if os.path.isfile(compose_path):
            # Handle docker-compose case
            try:
                # Store current directory
                original_dir = os.getcwd()
                # Change to the target directory
                os.chdir(path)
                
                # Execute docker-compose commands
                subprocess.run(["docker-compose", "down"], check=True)
                subprocess.run(["docker-compose", "pull"], check=True)
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                
                # Return to original directory
                os.chdir(original_dir)
                return True, None
                
            except subprocess.CalledProcessError as e:
                return False, f"Docker-compose command failed: {str(e)}"
                
        elif os.path.isfile(run_command_path):
            # Handle docker run command case
            try:
                with open(run_command_path, 'r') as f:
                    run_command = f.read().strip()
                
                if not run_command:
                    return False, "docker-run-command.txt is empty"
                
                # Execute the docker run command
                subprocess.run(run_command.split(), check=True)
                return True, None
                
            except subprocess.CalledProcessError as e:
                return False, f"Docker run command failed: {str(e)}"
            except Exception as e:
                return False, f"Error reading docker-run-command.txt: {str(e)}"
                
        else:
            return False, "No docker-compose.yml or docker-run-command.txt found in the specified path"
            
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python docker_manager.py <path>")
        sys.exit(1)
    
    success, error = update_docker_container(sys.argv[1])
    if success:
        print("Docker container updated successfully!")
    else:
        print(f"Error: {error}")
