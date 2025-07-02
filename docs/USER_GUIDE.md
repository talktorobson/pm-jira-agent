# 🎯 PM Jira Agent - User Guide

**Transform simple requests into professional Jira tickets in under 2 minutes**

---

## 🚀 Quick Start

### What This Does for You

The PM Jira Agent automatically:
- ✅ **Converts** your ideas into professional Jira tickets
- ✅ **Researches** context from your documentation
- ✅ **Validates** technical feasibility
- ✅ **Creates** actual tickets in AHSSI project
- ✅ **Saves** 25+ minutes per ticket

### 30-Second Demo

**Your Input:**
```
"Add user authentication to the dashboard"
```

**AI Creates:**
- ✅ Professional user story with acceptance criteria
- ✅ Technical feasibility analysis
- ✅ Quality score: 0.96/1.0
- ✅ Jira ticket: AHSSI-2876

---

## 📥 How to Use

### Step 1: Access the System

**For Business Users:**
```bash
# Contact your system administrator for:
# - API endpoint URL
# - API key for authentication
# - Access to Jira project AHSSI
```

### Step 2: Submit Your Request

**Option A: Web Interface (Coming Soon)**
- Simple form with text area for your request
- Optional fields for priority and context
- Click "Create Ticket" button

**Option B: API Integration**
```json
{
  "user_request": "Add secure login with two-factor authentication",
  "priority": "High",
  "context": {
    "stakeholder": "Security Team",
    "deadline": "Q2 2025"
  }
}
```

### Step 3: Review the Output

You'll receive:
- ✅ **Ticket URL**: Direct link to your new Jira ticket
- ✅ **Quality Score**: Confidence level (target: 0.8+)
- ✅ **Execution Time**: How long it took (typically <3 seconds)
- ✅ **Next Steps**: What to do with your new ticket

---

## 🤖 How It Works

### The AI Workflow (Behind the Scenes)

```
1. 🧠 PM Agent
   ├── Researches your documentation
   ├── Analyzes similar tickets
   └── Creates initial draft

2. 📋 Business Rules
   ├── Applies company policies
   ├── Checks UI/UX guidelines
   └── Validates security requirements

3. 👨‍💻 Tech Lead Review
   ├── Validates technical feasibility
   ├── Scores quality (must be ≥0.8)
   └── Provides improvement feedback

4. 🎯 Jira Creation
   ├── Creates actual ticket
   ├── Adds metadata
   └── Returns ticket URL
```

**Total Time:** 2-3 seconds

---

## 💡 Writing Great Requests

### ✅ Good Examples

**Specific Feature Request:**
```
"Add real-time notifications for order status updates that work 
across web and mobile platforms, supporting 1000+ concurrent users"
```

**Bug Report:**
```
"Fix dashboard loading issue where page takes 8+ seconds to load 
due to slow database queries on user analytics"
```

**Enhancement:**
```
"Improve search functionality with filters for date, category, 
and price range to help users find products faster"
```

### ❌ Avoid These

```
"Make the app better"           → Too vague
"Add notifications"             → No context
"Change button color"           → No business value
"Build complete CRM"            → Too broad
```

### 📝 Request Template

```
**What**: [What you want to build/fix]

**Why**: [Business value and impact]

**Who**: [Who will use this]

**Context**: 
- Current problem: [What's not working]
- Success looks like: [How you'll measure success]
- Constraints: [Any limitations]

**Additional Info**:
- Stakeholders: [Who cares about this]
- Related work: [Any connected tickets]
```

---

## 🔧 Troubleshooting

### Common Issues

**❌ Quality Score Too Low (<0.8)**
```
Problem: "Request needs more detail"
Solution: Add specific requirements, business context, and success criteria
```

**❌ Technical Concerns**
```
Problem: "Technical approach unclear"
Solution: Specify preferred technologies, performance needs, integration points
```

**❌ Business Rules Violation**
```
Problem: "Violates company policies"
Solution: Include security considerations, compliance requirements, accessibility needs
```

### Getting Help

1. **Check Ticket Quality**: Aim for 0.8+ scores
2. **Review Created Tickets**: Visit [AHSSI Project](https://jira.adeo.com/projects/AHSSI)
3. **Contact Support**: Reach out to your system administrator

---

## 📊 What Success Looks Like

### Metrics to Track

| Metric | Target | Your Goal |
|--------|--------|----------|
| **Quality Score** | ≥0.8 | Create tickets that meet standards |
| **Time Saved** | 25+ min | Focus on strategy, not formatting |
| **First-Pass Approval** | 95%+ | Reduce back-and-forth with dev team |
| **Ticket Clarity** | High | Developers understand requirements |

### Business Impact

- **Faster Development**: Clear requirements reduce clarification time
- **Better Quality**: Consistent ticket standards improve delivery
- **Team Efficiency**: Developers can focus on building, not deciphering
- **Stakeholder Confidence**: Professional tickets demonstrate thorough planning

---

## 🆘 Support

### Quick Help

- **System Status**: Check if ticket creation is working
- **Recent Tickets**: Review your created tickets in Jira
- **Quality Trends**: Monitor your average quality scores

### Contact Information

- **Technical Issues**: Contact your system administrator
- **Training**: Request user training session
- **Feature Requests**: Submit to product backlog

---

**Ready to create your first professional ticket in under 2 minutes? 🚀**