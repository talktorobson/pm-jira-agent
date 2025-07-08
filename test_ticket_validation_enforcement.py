#!/usr/bin/env python3
"""
Test Ticket Validation Enforcement
Verify that agents are forced to follow formatting guidelines
"""

import asyncio
import json
from enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator

async def test_enforcement():
    """Test that validation enforcement actually works"""
    
    print("🧪 Testing Ticket Validation Enforcement")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = EnhancedMultiAgentOrchestrator()
    
    # Test request that typically generates verbose tickets
    request = """
    Create a monitoring API for AHS activation status that SSI can use to check 
    if Business Units have AHS enabled before showing service offers.
    """
    
    print("📋 Request:", request)
    print("\n🚀 Processing with STRICT validation enforcement...")
    
    try:
        # Process just the PM agent to test validation
        pm_result = await orchestrator.process_pm_agent(request)
        
        print("\n📊 VALIDATION RESULTS:")
        print("=" * 40)
        
        # Check validation results
        validation = pm_result.get("validation_results", {})
        word_count = validation.get("word_count", 0)
        passes = validation.get("passes_validation", False)
        issues = validation.get("issues", [])
        
        print(f"✅ Passes Validation: {passes}")
        print(f"📝 Word Count: {word_count}/250")
        print(f"📊 Quality Score: {pm_result.get('quality_score', 0):.3f}")
        
        if issues:
            print(f"\n❌ Issues Found ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ No formatting issues found")
        
        # Show actual ticket content
        ticket_desc = pm_result.get("response", {}).get("jira_ticket", {}).get("fields", {}).get("description", "")
        if ticket_desc:
            print(f"\n📄 GENERATED TICKET DESCRIPTION:")
            print("=" * 40)
            print(ticket_desc)
            print("=" * 40)
            
            # Manually check key requirements
            print("\n🔍 MANUAL VALIDATION CHECK:")
            print(f"   📏 Word count: {len(ticket_desc.split())} words")
            print(f"   📊 Has Objective: {'**Objective:**' in ticket_desc}")
            print(f"   🔧 Has Requirements: {'#### 🔧 Requirements:' in ticket_desc}")
            print(f"   📚 Has References: {'#### 📚 References:' in ticket_desc}")
            print(f"   ✅ Has Acceptance: {'#### ✅ Acceptance Criteria:' in ticket_desc}")
            print(f"   📖 GitBook refs: {ticket_desc.count('GitBook')}")
            print(f"   🎫 AHSSI refs: {ticket_desc.count('AHSSI-')}")
            
            # Check for forbidden content
            forbidden_terms = ["testing strategy", "unit tests", "junit", "mockito", "owasp"]
            found_forbidden = [term for term in forbidden_terms if term.lower() in ticket_desc.lower()]
            if found_forbidden:
                print(f"   ❌ Forbidden content: {found_forbidden}")
            else:
                print(f"   ✅ No forbidden methodology content")
        
        # Overall assessment
        print(f"\n🎯 ENFORCEMENT TEST RESULT:")
        if passes and word_count <= 250:
            print("✅ SUCCESS: Agent follows formatting guidelines!")
        else:
            print("❌ FAILURE: Agent still violating guidelines")
            
        return passes and word_count <= 250
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_validation_function():
    """Test the validation function directly"""
    
    print("\n\n🧪 Testing Validation Function Directly")
    print("=" * 60)
    
    orchestrator = EnhancedMultiAgentOrchestrator()
    
    # Test cases
    test_cases = [
        {
            "name": "Good Ticket",
            "description": """### 📊 AHS Status API
**Objective:** Create API for SSI to check AHS activation status per Business Unit.

#### 🔧 Requirements:
1. GET endpoint /ahs/activation/status/{businessUnitId}
2. Response format: {businessUnitId, isAHSActivated, status}
3. Performance target: <200ms response time

#### 📚 References:
- **GitBook**: [AHS Integration](https://app.gitbook.com/ahs)
- **Related**: [AHSSI-2801](https://jira.adeo.com/browse/AHSSI-2801) - AHS setup

#### ✅ Acceptance Criteria:
1. API responds correctly for valid businessUnitId
2. Error handling for 400/404/500 status codes
3. Performance meets <200ms target"""
        },
        {
            "name": "Bad Ticket (Too Long)",
            "description": """### 📊 AHS Status API Implementation with Comprehensive Testing Strategy

**Objective:** Create a comprehensive API solution for the Sales Service Integrator (SSI) to determine AHS activation status for Business Units and stores with full testing strategy.

#### 🔧 Technical Requirements:
1. Implement REST API endpoint with GET method
2. Create comprehensive data access layer with caching
3. Implement full security framework with API key validation
4. Add comprehensive logging and monitoring solution
5. Create detailed error handling for all scenarios

#### 🧪 Testing Strategy:
**Unit Tests:**
- Test individual components using JUnit and Mockito
- Achieve 90% code coverage target
- Test all business logic and data transformations

**Integration Tests:**
- Test component interactions using Spring Test
- Validate data flow between all layers
- Test caching mechanisms and database connectivity

**End-to-End Tests:**
- Complete workflow testing using Selenium
- Test entire user journey from request to response
- Validate all authentication and authorization flows

**Performance Tests:**
- Load testing using JMeter and Gatling
- Stress testing for peak load scenarios
- Resource utilization monitoring

**Security Tests:**
- OWASP vulnerability scanning using ZAP
- Penetration testing for all endpoints
- Security code review using static analysis

#### 📚 References:
- **GitBook**: [AHS Integration](https://app.gitbook.com/ahs)

#### ✅ Acceptance Criteria:
1. API responds correctly for valid businessUnitId
2. All test suites pass with required coverage
3. Performance meets targets under all load conditions
4. Security requirements fully implemented
5. Complete documentation and runbooks created"""
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print("-" * 40)
        
        validation = orchestrator._validate_ticket_format(test_case['description'])
        
        print(f"✅ Passes: {validation['passes_validation']}")
        print(f"📝 Words: {validation['word_count']}/250")
        print(f"📊 Score: {validation['score']:.2f}")
        
        if validation['issues']:
            print(f"❌ Issues ({len(validation['issues'])}):")
            for i, issue in enumerate(validation['issues'], 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ No issues found")

if __name__ == "__main__":
    async def main():
        # Test validation function
        await test_validation_function()
        
        # Test enforcement in agent
        print("\n" + "="*80)
        success = await test_enforcement()
        
        print(f"\n🎯 FINAL RESULT: {'SUCCESS' if success else 'FAILURE'}")
        print("="*80)
    
    asyncio.run(main())