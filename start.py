#!/usr/bin/env python3
"""
Smart Startup Script for University AI Assistant
Checks all dependencies and starts the application
"""

import subprocess
import sys
import os
import time
import requests
import codecs
from pathlib import Path

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_python_version():
    """Check Python version"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.10+ required. Found: {version.major}.{version.minor}")
        return False


def check_dependencies():
    """Check if all dependencies are installed"""
    print_info("Checking dependencies...")

    required = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'streamlit': 'streamlit',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',  # ✅ FIX HERE
        'faiss': 'faiss',
        'sentence_transformers': 'sentence_transformers',
        'langchain': 'langchain',
        'crewai': 'crewai'
    }

    missing = []
    for pip_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    else:
        print_success("All dependencies installed")
        return True


def check_env_file():
    """Check if .env file exists"""
    print_info("Checking configuration...")

    if not Path('.env').exists():
        print_warning(".env file not found")
        print_info("Creating .env from .env.example...")

        if Path('.env.example').exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print_success("Created .env file")
            print_warning("Please update .env with your settings before running")
            return False
        else:
            print_error(".env.example not found")
            return False
    else:
        print_success(".env file exists")
        return True


def check_lm_studio():
    """Check if LM Studio is running"""
    print_info("Checking LM Studio connection...")

    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=500)
        if response.status_code == 200:
            print_success("LM Studio is running")
            return True
        else:
            print_warning(f"LM Studio returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("LM Studio is not running")
        print_info("Please start LM Studio and load a model")
        return False
    except Exception as e:
        print_error(f"Error connecting to LM Studio: {str(e)}")
        return False


def check_api_keys():
    """Check if required API keys are set"""
    print_info("Checking API keys...")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        serper_key = os.getenv('SERPER_API_KEY')
        google_key = os.getenv('GOOGLE_SEARCH_API_KEY')

        if serper_key or google_key:
            if serper_key:
                print_success("Serper API key found")
            if google_key:
                print_success("Google Search API key found")
            return True
        else:
            print_warning("No search API keys found")
            print_info("System will use DuckDuckGo fallback (limited functionality)")
            return True  # Non-critical
    except Exception as e:
        print_warning(f"Could not check API keys: {str(e)}")
        return True  # Non-critical


def create_directories():
    """Create necessary directories"""
    print_info("Creating directories...")

    dirs = [
        'data/faiss_index',
        'logs'
    ]

    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print_success("Directories created")
    return True


def start_backend():
    """Start FastAPI backend using uvicorn CLI"""
    print_info("Starting backend server...")

    backend_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "app:app",  # only 'app:app' if cwd=backend
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
            "--log-level", "info",
            "--no-access-log"  # Reduce logging
        ],
        cwd=os.path.join(os.getcwd(), "backend"),  # Important: cwd=backend folder
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        encoding='utf-8',
        errors='replace',
        env=dict(os.environ, PYTHONIOENCODING='utf-8')  # Force UTF-8 encoding
    )

    print_info("Waiting for backend to start...")

    # Check process output for errors
    error_output = []
    for i in range(500):
        try:
            # Try root endpoint first (simpler, doesn't require full initialization)
            response = requests.get(
                "http://127.0.0.1:8000/",
                timeout=10
            )
            if response.status_code == 200:
                print_success("Backend server started on http://127.0.0.1:8000")
                # Give it a moment for full initialization
                time.sleep(2)
                return backend_process
        except requests.exceptions.ConnectionError:
            # Server not ready yet, check if process is still alive
            if backend_process.poll() is not None:
                # Process has terminated, get error output
                try:
                    stdout, _ = backend_process.communicate(timeout=210)
                    if stdout:
                        error_output.append(stdout)
                except:
                    pass
                break
        except Exception as e:
            pass
        
        # Check process status
        if backend_process.poll() is not None:
            # Process died
            try:
                stdout, _ = backend_process.communicate(timeout=120)
                if stdout:
                    error_output.append(stdout)
            except:
                pass
            break
        
        # Show progress every 10 seconds
        if i > 0 and i % 10 == 0:
            print_info(f"Still waiting for backend... ({i}s)")
        
        time.sleep(1)

    # If we get here, backend failed to start
    print_error("Backend failed to start within 120 seconds")
    
    # Show error output if available
    if error_output:
        print_error("Backend error output:")
        for line in error_output[-20:]:  # Show last 20 lines
            if line.strip():
                print(f"  {line.strip()}")
    
    # Try to get more info
    try:
        stdout, stderr = backend_process.communicate(timeout=300)
        if stderr:
            print_error("Stderr:")
            for line in stderr.split('\n')[-10:]:
                if line.strip():
                    print(f"  {line.strip()}")
    except:
        pass
    
    backend_process.terminate()
    return None



def start_frontend():
    """Start Streamlit frontend"""
    print_info("Starting frontend...")

    frontend_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', 'frontend/streamlit_app.py',
         '--server.port', '8501'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    print_success("Frontend started on http://localhost:8501")
    return frontend_process


def main():
    """Main startup function"""
    print_header("UNIVERSITY AI ASSISTANT - SMART STARTUP")

    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_env_file),
        ("Directories", create_directories),
        ("LM Studio", check_lm_studio),
        ("API Keys", check_api_keys),
    ]

    print_header("PRE-FLIGHT CHECKS")

    all_passed = True
    for name, check_func in checks:
        if not check_func():
            if name in ["Python Version", "Dependencies", "LM Studio"]:
                # Critical checks
                all_passed = False

    if not all_passed:
        print("\n" + "=" * 70)
        print_error("Critical checks failed. Please fix the issues above.")
        print("=" * 70)
        return 1

    # Start services
    print_header("STARTING SERVICES")

    backend_process = start_backend()
    if not backend_process:
        return 1

    time.sleep(2)

    frontend_process = start_frontend()

    # Success message
    print_header("STARTUP COMPLETE")

    print_success("System is ready!")
    print()
    print(f"{Colors.BOLD}Access the application:{Colors.ENDC}")
    print(f"  🌐 Frontend:  http://localhost:8501")
    print(f"  🔌 Backend:   http://localhost:8000")
    print(f"  📚 API Docs:  http://localhost:8000/docs")
    print()
    print(f"{Colors.WARNING}Press Ctrl+C to stop all services{Colors.ENDC}")
    print("=" * 70)

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print_info("Shutting down...")

        backend_process.terminate()
        frontend_process.terminate()

        backend_process.wait(timeout=300)
        frontend_process.wait(timeout=300)

        print_success("All services stopped")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    exit(main())