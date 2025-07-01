# 🤖 PM Jira Agent

> AI-powered product management automation system that transforms simple issue requests into high-quality Jira tickets through intelligent multi-agent workflows.

## 📋 Project Overview

**PM Jira Agent** is an advanced AI system that automates the creation of comprehensive, high-quality Jira tickets from simple user requests. The system uses multi-agent AI workflows to ensure tickets meet "Definition of Ready" standards before creation.

### 🎯 Current Status: **MIGRATION IN PROGRESS**
- **Legacy System**: n8n workflow automation (✅ Production ready)
- **Target System**: **Vertex AI Agent Builder** (🚀 Migration approved)
- **Timeline**: 4-week migration plan approved and documented

## 🏗️ Architecture Evolution

### Legacy Architecture (n8n)
```
Current: n8n Workflow Engine
├── 8 interconnected workflows
├── PostgreSQL + Qdrant databases  
├── Docker containerization
└── External APIs (GitBook, Jira, Anthropic)
```

### Target Architecture (Vertex AI Agent Builder)
```
🎯 Target: Vertex AI Agent Builder
├── 🤖 PM Agent (Primary Orchestrator)
├── 👨‍💻 Tech Lead Agent (Quality Reviewer)
├── ⚙️ Jira Creation Agent (Ticket Executor)
└── 🔧 Cloud Functions (API Layer)
```

## ⚡ Key Features

- **🧠 Multi-Agent Intelligence**: PM Agent + Tech Lead Agent collaboration
- **📊 Quality Gates**: 0.8+ score requirement before ticket creation
- **🔄 Iterative Refinement**: Automatic improvement loops until standards met
- **📚 Context-Aware**: Integrates GitBook docs and existing Jira tickets
- **🎯 Structured Output**: Follows Agile best practices and Jira standards
- **🔗 Full Integration**: GitBook knowledge base + Adeo Jira instance

## 🚀 Migration Plan

### Phase 1: Foundation Setup (Week 1)
- GCP project setup and API configuration
- Cloud Functions development for API integrations
- Basic PM Agent configuration in Vertex AI

### Phase 2: Core Multi-Agent Logic (Week 2) 
- Tech Lead Agent implementation
- Agent handoff mechanisms and quality gates
- Iterative refinement loops

### Phase 3: Advanced Features (Week 3)
- GitBook grounding integration
- Business rules engine
- Monitoring and analytics setup

### Phase 4: Migration & Production (Week 4)
- A/B testing framework (parallel running)
- Performance optimization and load testing
- Production cutover and n8n deprecation

## 🔧 Current Integrations

### GitBook Knowledge Management ✅
- **API Endpoint**: `https://api.gitbook.com/v1/spaces/Jw57BieQciFYoCHgwVlm`
- **Authentication**: Bearer token (stored in Secret Manager)
- **Content Types**: Product overview, technical architecture, standards

### Adeo Jira Integration ✅
- **Instance**: `jira.adeo.com`
- **Project**: AHSSI (Project ID: 14921)
- **Authentication**: Basic auth with API token (stored in Secret Manager)
- **Features**: Ticket creation, story retrieval, quality validation

## 📊 Expected Migration Benefits

| Metric | Current (n8n) | Target (Vertex AI) | Improvement |
|--------|---------------|-------------------|-------------|
| **Response Time** | 3-5s | <2s | **40-60% faster** |
| **Uptime** | 99.5% | >99.9% | **Better reliability** |
| **Operational Cost** | $100/month | $60-70/month | **30-40% reduction** |
| **Maintenance** | 4h/week | <1h/week | **75% less overhead** |
| **Scalability** | Manual scaling | Auto-scaling | **10x capacity** |

## 🛠️ Development Setup

### Current n8n System (Legacy)
```bash
# Clone repository
git clone https://github.com/talktorobson/pm-jira-agent.git
cd pm-jira-agent

# Start n8n system (Docker required)
docker compose --profile cpu up
```

### Future Vertex AI System (In Development)
```bash
# Phase 1 setup (coming soon)
# GCP project configuration
# Cloud Functions deployment
# Vertex AI Agent Builder setup
```

## 📚 Documentation

- **[Migration Plan](CLAUDE.md)**: Comprehensive 4-week migration strategy
- **[Current Workflows](n8n/backup/workflows/)**: n8n workflow configurations
- **[Project Context](CLAUDE.md)**: Extended documentation and implementation details

## 🔐 Security & Configuration

- **API Keys**: Managed via GCP Secret Manager (migration target)
- **Authentication**: GitBook Bearer tokens + Jira Basic auth
- **Credentials**: Encrypted n8n format (current) → GCP Secrets (target)

## 📈 Quality Metrics

### Ticket Quality Scoring (0-1 scale)
- **Summary Clarity**: Clear and actionable ticket titles
- **User Story**: Well-formed "As a... I want... So that..." format
- **Acceptance Criteria**: Comprehensive and testable requirements
- **Technical Feasibility**: Realistic scope and implementation approach
- **Completeness**: All required fields and context provided

### Success Criteria
- ✅ Quality score ≥ 0.8 required for ticket creation
- ✅ Average iteration cycles < 2.0
- ✅ User satisfaction ≥ 4.5/5.0
- ✅ Technical review efficiency ≥ 85%

## 🤝 Contributing

This project is currently in migration phase. Contributions welcome after Vertex AI migration completion (estimated 4 weeks).

## 📞 Contact

- **Owner**: Robson Benevenuto D'Avila Reis
- **GitHub**: [@talktorobson](https://github.com/talktorobson)
- **Project**: Personal AI automation system

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

---

**🚀 Migration Status**: Phase 1 ready to begin  
**⏱️ Timeline**: 4 weeks from start date  
**🎯 Success Criteria**: Zero production disruption + 30-40% cost reduction + <2s response times