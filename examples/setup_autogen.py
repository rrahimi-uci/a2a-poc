"""
Setup script for AutoGen-A2A hybrid integration.
"""

import subprocess
import sys
import os


def install_autogen():
    """Install AutoGen and dependencies."""
    print("🔧 Installing AutoGen and dependencies...")
    
    packages = [
        "pyautogen>=0.2.0",
        "openai>=1.0.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True


def setup_openai_key():
    """Guide user through OpenAI API key setup."""
    print("\\n🔑 OpenAI API Key Setup")
    print("-" * 30)
    
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key and current_key != "your-api-key-here":
        print(f"✅ OpenAI API key is already set: {current_key[:8]}...")
        return True
    
    print("To use AutoGen with LLM capabilities, you need an OpenAI API key.")
    print("\\nOptions:")
    print("1. Get a free API key from: https://platform.openai.com/api-keys")
    print("2. Set environment variable: export OPENAI_API_KEY='your-key'")
    print("3. Or create a .env file in the project root")
    
    key = input("\\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    
    if key:
        # Create .env file
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path, "w") as f:
            f.write(f"OPENAI_API_KEY={key}\\n")
        print(f"✅ API key saved to .env file")
        return True
    else:
        print("⚠️  Skipping API key setup. AutoGen will use mock responses.")
        return False


def create_demo_config():
    """Create a configuration file for the demo."""
    config = {
        "autogen_enabled": True,
        "a2a_math_agent_url": "http://localhost:8001",
        "openai_model": "gpt-3.5-turbo",
        "autogen_workspace": "autogen_workspace"
    }
    
    import json
    config_path = os.path.join(os.path.dirname(__file__), "hybrid_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created configuration file: {config_path}")


def main():
    """Main setup function."""
    print("🚀 AutoGen-A2A Hybrid Setup")
    print("=" * 40)
    
    print("This script will set up the hybrid AutoGen-A2A agent system.")
    print("\\n1. Installing AutoGen...")
    
    if install_autogen():
        print("\\n2. Setting up OpenAI API key...")
        setup_openai_key()
        
        print("\\n3. Creating demo configuration...")
        create_demo_config()
        
        print("\\n✅ Setup complete!")
        print("\\n🎯 Next steps:")
        print("1. Start A2A Math Agent: python scripts/start_math_agent.py")
        print("2. Run hybrid demo: python examples/hybrid_autogen_a2a.py")
        
    else:
        print("\\n❌ Setup failed. Please install dependencies manually:")
        print("pip install pyautogen openai")


if __name__ == "__main__":
    main()
