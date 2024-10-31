import subprocess
import sys

# Path to the requirements file
requirements_file = r"D:\CustomizationAndCreationPrograms\Applicaitons\RecRoom-Shirt-Printer-main\RecRoom-Shirt-Printer-main\requirements.txt"

def install_packages():
    try:
        print("Installing packages...")
        # Use sys.executable to ensure we use the current Python interpreter
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("All packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing packages: {e}")
        exit(1)

if __name__ == "__main__":
    install_packages()

    input("Press Enter to exit...")