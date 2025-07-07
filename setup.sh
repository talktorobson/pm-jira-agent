#!/bin/bash

# PM Jira Agent Main Project Setup Script
# GitBook Full Content Integration - Main Folder Environment Setup

set -e

echo "🚀 PM Jira Agent - GitBook Full Content Integration Setup"
echo "========================================================"

# Check if we're in the right directory
if [ ! -f "enhanced_multi_agent_orchestrator.py" ]; then
    echo "❌ Error: Please run this script from the main project directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python version: $python_version"

# Python 3.9+ check - simplified
major_version=$(echo "$python_version" | cut -d'.' -f1)
minor_version=$(echo "$python_version" | cut -d'.' -f2)

if [ "$major_version" -lt 3 ] || [ "$major_version" -eq 3 -a "$minor_version" -lt 9 ]; then
    echo "❌ Error: Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check Google Cloud authentication
echo "🔐 Checking Google Cloud authentication..."
if ! command -v gcloud &> /dev/null; then
    echo "⚠️ Warning: gcloud CLI not found. Please install it for full functionality."
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
else
    echo "✅ gcloud CLI found"
    
    # Check if authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        echo "✅ Google Cloud authentication active"
    else
        echo "⚠️ Warning: No active Google Cloud authentication found"
        echo "   Run: gcloud auth application-default login"
    fi
fi

# Check project configuration
echo "🏗️ Checking project configuration..."
if [ -f "gcp/setup-scripts/01-enable-apis.sh" ]; then
    echo "✅ GCP setup scripts available"
else
    echo "⚠️ Warning: GCP setup scripts not found. Manual configuration may be required."
fi

# Create test script if it doesn't exist
if [ ! -f "test_main_environment.py" ]; then
cat > test_main_environment.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test for main project environment
"""
import sys
import asyncio

def test_imports():
    """Test that all required imports work"""
    try:
        import httpx
        print("✅ httpx imported successfully")
        
        from google.cloud import secretmanager
        print("✅ google-cloud-secret-manager imported successfully")
        
        import vertexai
        from vertexai import agent_engines
        print("✅ vertexai imported successfully")
        
        from enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator
        print("✅ EnhancedMultiAgentOrchestrator imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_orchestrator():
    """Test basic orchestrator initialization"""
    try:
        orchestrator = EnhancedMultiAgentOrchestrator()
        print("✅ Orchestrator initialized successfully")
        print(f"   Project: {orchestrator.project_id}")
        print(f"   Location: {orchestrator.location}")
        print(f"   Agents: {len(orchestrator.agents)} configured")
        return True
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return False

def main():
    print("🧪 Main Environment Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test orchestrator
    try:
        result = asyncio.run(test_orchestrator())
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Async test error: {e}")
        sys.exit(1)
    
    print("\n🎉 Main environment test successful!")
    print("Ready to run GitBook full content integration tests.")

if __name__ == "__main__":
    main()
EOF

chmod +x test_main_environment.py
fi

echo ""
echo "🎉 Setup complete! Main project environment ready."
echo ""
echo "📋 Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Test installation: python test_main_environment.py"
echo "3. Run GitBook test: python test_direct_gitbook_content.py"
echo "4. Run 5-agent workflow: python test_working_5_agent_final.py"
echo "5. Create tickets: python enhanced_multi_agent_orchestrator.py"
echo ""
echo "📚 Key files:"
echo "- enhanced_multi_agent_orchestrator.py: Main 5-agent orchestrator"
echo "- test_direct_gitbook_content.py: GitBook full content integration test"
echo "- test_working_5_agent_final.py: Complete 5-agent workflow test"
echo "- test_main_environment.py: Environment validation test"
echo "- simple_local_pm_agent_rest.py: REST API PM agent"
echo ""
echo "🔗 For authentication setup, check gcp/setup-scripts/"