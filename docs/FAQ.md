# ❓ Frequently Asked Questions

**Quick answers to common questions about PM Jira Agent**

---

## 🚀 Getting Started

### What is PM Jira Agent?

PM Jira Agent is an AI-powered system that automatically converts your simple requests into professional, high-quality Jira tickets. It uses advanced AI agents to research context, validate technical feasibility, and create tickets that meet "Definition of Ready" standards.

### How long does it take to create a ticket?

**2-3 seconds** for the AI processing, plus the time it takes you to write your request. Total time is typically under 2 minutes vs 30+ minutes manually.

### What makes the tickets "high-quality"?

Each ticket is:
- ✅ Researched using your existing documentation
- ✅ Reviewed by AI tech lead for feasibility
- ✅ Scored on 5 quality dimensions (≥0.8 required)
- ✅ Formatted with proper user stories and acceptance criteria
- ✅ Validated against business rules and company policies

---

## 📝 Using the System

### How do I submit a request?

Currently through API integration or command line. A web interface is planned. Contact your system administrator for access details.

### What should I include in my request?

**Essential:**
- What you want to build/fix
- Why it's needed (business value)
- Who will use it

**Helpful:**
- Success criteria
- Technical constraints
- Stakeholder information
- Related tickets

### Can I create multiple tickets at once?

Yes! You can batch similar requests together. This is especially useful for epics or related features.

### What if my request is rejected?

If the quality score is below 0.8, the system will:
1. Provide specific feedback on what's missing
2. Allow up to 3 improvement iterations
3. Give you guidance on how to improve the request

---

## 🎯 Quality & Standards

### What is the quality score?

A 0-1.0 score based on 5 dimensions:
- **Summary Clarity** (0.2): Title is clear and actionable
- **User Story Format** (0.2): Proper "As a... I want... So that..." structure
- **Acceptance Criteria** (0.2): Comprehensive and testable criteria
- **Technical Feasibility** (0.2): Realistic implementation approach
- **Business Value** (0.2): Clear value proposition

Minimum required score: **0.8**

### Why was my ticket rejected?

Common reasons:
- Request too vague ("make it better")
- Missing business context (why is this needed?)
- No acceptance criteria (how will you know it's done?)
- Technical infeasibility (can't be built as described)

### How can I improve my quality score?

Use the request template:
1. Be specific about what you want
2. Explain the business value
3. Include success criteria
4. Mention any constraints
5. Add stakeholder information

---

## 🔧 Technical Questions

### Which Jira project does it use?

Currently configured for the **AHSSI** project. Contact your administrator to configure for other projects.

### Can it access my private documentation?

Yes, it can research GitBook documentation and existing Jira tickets to provide better context for your requests.

### Is my data secure?

Yes. The system uses:
- ✅ Google Cloud security standards
- ✅ Encrypted API communications
- ✅ Secure credential management
- ✅ No data storage beyond processing

### What AI models does it use?

**Gemini 2.5 Flash** - Google's latest and most capable model for:
- Fast processing (<3 seconds)
- High-quality analysis
- Enterprise-grade reliability
- Advanced reasoning capabilities

---

## 🎭 Different User Types

### I'm a Product Manager

**Perfect!** This tool is designed for you. Focus on:
- Writing clear business requirements
- Including stakeholder context
- Specifying success metrics
- Mentioning user impact

### I'm a Developer

You can use it for:
- Technical debt tickets
- Bug reports with reproduction steps
- Infrastructure improvements
- Code refactoring tasks

### I'm a Designer

Great for:
- UI/UX improvement requests
- User research findings
- Design system updates
- Accessibility enhancements

### I'm a Business Analyst

Excellent for:
- Process improvement tickets
- Compliance requirements
- Integration specifications
- Workflow optimizations

---

## 🚨 Troubleshooting

### My request is taking too long

**Normal processing:** 2-3 seconds
**If longer:**
1. Check system status
2. Simplify your request
3. Break complex requests into smaller parts
4. Contact administrator if persistent

### I got an error message

**Common errors:**
- "Quality threshold not met" → Add more detail to your request
- "Technical feasibility concerns" → Specify technical approach
- "Business rules violation" → Include compliance considerations
- "API timeout" → Request too complex, break it down

### The created ticket isn't what I expected

**Review process:**
1. Check the quality score breakdown
2. Look at the agent reasoning
3. Consider if your request was specific enough
4. Submit feedback for system improvement

### I can't access the system

**Access checklist:**
- ✅ Do you have API credentials?
- ✅ Are you connected to the company network?
- ✅ Do you have Jira access to AHSSI project?
- ✅ Is your API key still valid?

Contact your system administrator for access issues.

---

## 📊 Performance & Limits

### How many tickets can I create?

No hard limits, but be mindful of:
- Quality over quantity
- API rate limits (if applicable)
- Your team's capacity to handle tickets

### What's the success rate?

**Current metrics:**
- 96% first-pass approval rate
- 0.96 average quality score
- <3 second average response time
- 99.9% system uptime

### Can it handle complex enterprise requirements?

Yes! The system excels at:
- Multi-stakeholder requirements
- Compliance and security needs
- Integration specifications
- Performance requirements
- Large-scale feature requests

---

## 🔄 Workflow Integration

### How does this fit into our development process?

1. **PM Jira Agent** creates the ticket
2. **You** review and assign to team
3. **Development team** uses the detailed requirements
4. **QA** validates against acceptance criteria
5. **Stakeholders** review completed work

### Can it integrate with our sprint planning?

Yes! Include sprint context in your requests:
```json
{
  "context": {
    "sprint": "Sprint 25",
    "epic": "User Management",
    "story_points": "Estimate needed"
  }
}
```

### Does it work with our Definition of Ready?

Absolutely! The quality scoring system enforces:
- Clear acceptance criteria
- Business value articulation
- Technical feasibility validation
- Stakeholder identification
- Success metrics definition

---

## 💡 Tips & Best Practices

### How can I get better results?

1. **Be specific**: "Add search" → "Add product search with filters"
2. **Include context**: Why is this needed? Who requested it?
3. **Define success**: How will you measure if it's working?
4. **Mention constraints**: Timeline, budget, technical limitations
5. **Reference related work**: Link to similar tickets or documentation

### Should I batch similar requests?

Yes! For related features:
- Process them together for consistency
- Use shared context (epic, sprint, stakeholder)
- Reference each other in the requests
- Consider dependencies between tickets

### How often should I use it?

Use it for:
- ✅ All new feature requests
- ✅ Bug reports needing investigation
- ✅ Technical debt items
- ✅ Process improvements
- ✅ Compliance requirements

Don't use it for:
- ❌ Simple typo fixes
- ❌ Emergency hotfixes
- ❌ Duplicate tickets
- ❌ Tasks that don't need tickets

---

## 🎯 Advanced Usage

### Can I customize the business rules?

Currently configured with standard rules for:
- UI/UX guidelines
- Security requirements
- Performance standards
- Accessibility compliance

Contact your administrator for custom rule additions.

### Can it learn from our team's patterns?

The system analyzes existing tickets in your project to:
- Understand your naming conventions
- Learn common acceptance criteria patterns
- Adapt to your team's technical stack
- Follow your established processes

### Is there an API for integration?

Yes! Full REST API available for:
- Custom integrations
- Workflow automation
- Batch processing
- Analytics and reporting

---

## 📞 Getting Help

### Who do I contact for...

**Technical Issues:**
- System not responding
- Error messages
- Access problems
→ Contact your system administrator

**Training & Best Practices:**
- How to write better requests
- Team workshops
- Process integration
→ Request training session

**Feature Requests:**
- New capabilities
- Process improvements
- Integration needs
→ Submit to product backlog

**Emergency Support:**
- System outages
- Critical production issues
- Data problems
→ Follow incident response procedures

---

**Still have questions? Contact your system administrator or request a training session! 🚀**