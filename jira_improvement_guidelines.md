# Jira Ticket Description Improvement Guidelines

## 🎯 Core Principles for Better Jira Tickets

### ❌ Common Problems to Fix:
1. **Excessive Length** - Tickets that are 500+ words when 200 would suffice
2. **Broken Formatting** - Malformed numbered lists, inconsistent styling
3. **Missing Context** - No references to GitBook documentation or related tickets
4. **Methodology Overload** - Explaining basic concepts the team already knows
5. **Poor Scannability** - Wall of text without clear sections

### ✅ Improvement Rules:

#### 1. **Length Management**
- **Target**: 200-300 words maximum for description
- **Method**: Remove methodology explanations, focus on specifics
- **Test**: If it takes >2 minutes to read, it's too long

#### 2. **Proper Formatting**
```markdown
✅ GOOD:
1. First requirement
2. Second requirement  
3. Third requirement

❌ BAD:
1 First requirement
2.Second requirement
  3 Third requirement
```

#### 3. **Context Integration**
**Required References:**
- **GitBook Links**: Always include relevant documentation
  - Format: `[Service Name Documentation](https://app.gitbook.com/...)`
- **Similar Tickets**: Reference 2-3 related AHSSI tickets
  - Format: `[AHSSI-XXXX](https://jira.adeo.com/browse/AHSSI-XXXX) - Brief description`

#### 4. **Methodology Assumptions**
**Assume the team knows:**
- Basic testing principles (unit, integration, E2E)
- Standard tools (JUnit, Mockito, Selenium, etc.)
- GDPR and security compliance basics
- Common architectural patterns

**Don't explain:**
- What unit testing is
- How to write test cases
- Basic security principles
- Standard development practices

#### 5. **Professional Structure**
```markdown
### 📊 [Clear, Action-Oriented Title]

**Objective:** One sentence describing the goal

#### 🔧 Technical Requirements:
1. Specific requirement
2. Specific requirement
3. Specific requirement

#### 📚 References:
- **GitBook**: [Link with description]
- **Related Tickets**: [AHSSI-XXXX] - description

#### ✅ Acceptance Criteria:
1. Measurable outcome
2. Measurable outcome
3. Measurable outcome

#### 🧪 Testing Focus:
- **Key areas only** (no methodology explanation)

#### 🛡️ Compliance:
- **Specific requirements only**
```

## 🔧 Agent-Specific Instructions

### PM Agent Guidelines:
- **Focus**: Business value and clear requirements
- **Length**: Keep initial draft under 250 words
- **Research**: Include GitBook content references
- **Context**: Reference similar AHSSI tickets

### Tech Lead Agent Guidelines:  
- **Focus**: Technical feasibility and architecture
- **Avoid**: Explaining basic technical concepts
- **Include**: Specific implementation approaches
- **Limit**: Technical details to essential only

### QA Agent Guidelines:
- **Focus**: Testability and quality criteria
- **Avoid**: Explaining testing methodologies
- **Include**: Specific test scenarios and coverage targets
- **Limit**: Testing details to critical areas only

### Business Rules Agent Guidelines:
- **Focus**: Compliance requirements and governance
- **Avoid**: Explaining GDPR or basic security
- **Include**: Specific regulatory requirements
- **Limit**: Compliance details to project-specific needs

### Jira Creator Agent Guidelines:
- **Focus**: Final formatting and validation
- **Ensure**: All formatting is correct
- **Verify**: All references are included
- **Validate**: Description is concise and actionable

## 📊 Quality Metrics

### Length Targets:
- **Title**: 5-8 words
- **Objective**: 1 sentence
- **Technical Requirements**: 3-5 bullet points
- **Acceptance Criteria**: 3-5 measurable outcomes
- **Total Description**: 200-250 words maximum (STRICT LIMIT)

### ⚠️ CRITICAL: Aggressive Length Reduction Required
**Real Example**: Recent AHS API ticket was 1,200+ words, reduced to 250 words (79% reduction)

#### What to DELETE from tickets:
- ❌ **Testing Strategy sections** (team knows testing fundamentals)
- ❌ **Security explanations** (OWASP, vulnerability scanning details)
- ❌ **GDPR/Compliance explanations** (basic privacy concepts)
- ❌ **Tool lists** (JUnit, Mockito, etc. - team knows tools)
- ❌ **Methodology descriptions** (what unit testing is, etc.)
- ❌ **Detailed architecture explanations** (unless project-specific)
- ❌ **Implementation guidance** beyond 3-5 key steps
- ❌ **Verbose background** that doesn't add specific context

#### What to KEEP in tickets:
- ✅ **Specific technical requirements** (endpoints, response formats)
- ✅ **Measurable acceptance criteria** (performance targets, etc.)
- ✅ **GitBook references** to relevant documentation
- ✅ **Related AHSSI tickets** for context
- ✅ **Project-specific compliance requirements**
- ✅ **Clear implementation steps** (3-5 maximum)

### Reference Requirements:
- **Minimum**: 1 GitBook reference
- **Recommended**: 2-3 related AHSSI tickets
- **Format**: All links must be properly formatted and accessible

### Formatting Standards:
- **Consistent emoji usage** for section headers
- **Proper numbered lists** (1. 2. 3.)
- **Clear section separation** with headers
- **Bold emphasis** for key terms only

## 🎯 Success Criteria

A well-improved Jira ticket should:
1. ✅ **Read in under 2 minutes**
2. ✅ **Include relevant documentation references**
3. ✅ **Reference similar tickets for context**
4. ✅ **Focus on actionable requirements**
5. ✅ **Use professional, consistent formatting**
6. ✅ **Avoid unnecessary methodology explanations**