"""
Quick Start Script - LangChain Free Version
Automatically sets up and tests the system
"""

import subprocess
import sys
import os
import codecs

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def run_command(command, description):
    """Run a shell command with proper encoding"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of failing
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(e.stderr)
        return False

def main():
    print("\n" + "="*70)
    print("🚀 University AI Assistant - Quick Setup")
    print("="*70)
    
    # Step 1: Check Python version
    print(f"\n✅ Python Version: {sys.version}")
    
    # Step 2: Install dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing dependencies (LangChain-free)"
    ):
        print("❌ Installation failed!")
        sys.exit(1)
    
    # Step 3: Run tests
    if not run_command(
        "python test_langchain_free.py",
        "Running tests"
    ):
        print("⚠️  Some tests failed - check LM Studio connection")
    
    # Step 4: Instructions
    print("\n" + "="*70)
    print("✅ Setup Complete!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("\n1. Ensure LM Studio is running:")
    print("   - Open LM Studio")
    print("   - Load a model (e.g., Qwen 2.5 7B)")
    print("   - Start server on port 1234")
    
    print("\n2. Start the backend:")
    print("   cd backend")
    print("   python app.py")
    
    print("\n3. Start the frontend:")
    print("   cd frontend")
    print("   streamlit run streamlit_app.py")
    
    print("\n4. Access the app:")
    print("   Backend API: http://127.0.0.1:8000")
    print("   Frontend UI: http://localhost:8501")
    
    print("\n" + "="*70)
    print("🎉 Happy coding!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
