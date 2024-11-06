import subprocess
import sys
import os

# Path to the requirements file
requirements_file = r"D:\CustomizationAndCreationPrograms\Applicaitons\RecRoom-Shirt-Printer-main\RecRoom-Shirt-Printer-main\requirements.txt"

def install_chocolatey():
    """Install Chocolatey if it is not already installed."""
    try:
        # Check if Chocolatey is installed by looking for its executable
        subprocess.check_call(['choco', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Chocolatey is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Chocolatey is not installed. Installing Chocolatey...")
        # Install Chocolatey using PowerShell
        try:
            # PowerShell command to install Chocolatey
            subprocess.check_call([
                "powershell", 
                "-Command", 
                "Set-ExecutionPolicy Bypass -Scope Process -Force; "
                "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; "
                "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
            ], shell=True)
            print("Chocolatey installed successfully.")
        except Exception as e:
            print(f"Failed to install Chocolatey: {e}")

def install_pip():
    try:
        # Check if pip is already installed
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        print("Pip already installed.")
    except subprocess.CalledProcessError:
        print("Pip is not installed. Installing using ensurepip...")
        try:
            # Use ensurepip to install pip
            subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
            print("Pip installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pip: {e}")

def update_pip():
    try:
        # Check the current pip version
        output = subprocess.check_output([sys.executable, '-m', 'pip', '--version']).decode().strip()
        current_version = output.split()[1]
        print(f"Current pip version: {current_version}")
        
        # Update pip to the latest version
        print("Checking for pip updates...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("Pip has already been updated to the latest version.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update pip: {e}")

def check_get_pip():
    # Check if get-pip.py exists
    print("Current Directory:", os.getcwd())
    if os.path.exists('get-pip.py'):
        print("\nget-pip.py found.")
    else:
        print("\nget-pip.py not found.\nIf the rest of the program runs successfully, this is not a cause for concern.")

def check_pip():
    try:
        output = subprocess.check_output([sys.executable, '-m', 'pip', '--version'])
        print(output.decode().strip())
    except subprocess.CalledProcessError as e:
        print(f"\nError checking pip version: {e}")
    except FileNotFoundError:
        print("\npip is not installed.")

def is_cairo_installed():
    try:
        # Attempt to import the Cairo module
        import cairo
        return True
    except ImportError:
        return False

def install_cairo():
    try:
        print("\nChecking if Cairo is installed...")
        if not is_cairo_installed():
            print("Cairo is not installed. Installing Cairo...")
            # Install Cairo using Chocolatey (Windows-specific)
            subprocess.check_call(['choco', 'install', 'cairo', '-y'])  
            print("Cairo installed successfully.")
        else:
            print("Cairo is already installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing Cairo: {e}")

def install_packages():
    try:
        print("\nInstalling packages...")
        # Use sys.executable to ensure we use the current Python interpreter
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("All packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing packages: {e}")
        input("Press Enter To Exit...")
        exit(1)

if __name__ == "__main__":
    #install_chocolatey()  # Ensure Chocolatey is installed first
    check_get_pip()
    check_pip()
    install_pip()
    update_pip()  # Automatically check and update pip if necessary
    #install_cairo()  # Ensure Cairo is installed
    install_packages()
    input("Press Enter to exit...")
