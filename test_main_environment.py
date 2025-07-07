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
        from enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator
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
