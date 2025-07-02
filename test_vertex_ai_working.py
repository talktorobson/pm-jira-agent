#\!/usr/bin/env python3

"""
Test script to verify Vertex AI SDK is working
"""

try:
    # Test core imports
    from google.cloud import aiplatform
    import vertexai
    from google.cloud import secretmanager
    import requests
    
    print("✅ All required packages imported successfully\!")
    print("")
    print("📦 Available modules:")
    print("  - google.cloud.aiplatform ✅")
    print("  - vertexai ✅") 
    print("  - google.cloud.secretmanager ✅")
    print("  - requests ✅")
    print("")
    print("🚀 Ready to start Phase 2: Multi-Agent Development\!")
    print("")
    print("📋 Next steps:")
    print("1. Create PM Agent implementation")
    print("2. Create Tech Lead Agent implementation") 
    print("3. Create Jira Creator Agent implementation")
    print("4. Build multi-agent orchestration")
    print("5. Deploy to Vertex AI Agent Engine")
    print("")
    print("🎯 Your working Cloud Function URLs:")
    print("GitBook API: https://gitbook-api-jlhinciqia-od.a.run.app")
    print("Jira API: https://jira-api-jlhinciqia-od.a.run.app")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

