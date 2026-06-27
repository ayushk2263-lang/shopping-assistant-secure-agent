# 🛒 Shopping Assistant Secure Agent

A secure AI-powered Shopping Assistant built with **Google Agent Development Kit (ADK) 2.0**. This project demonstrates how to build production-oriented AI agents by integrating secure coding practices, automated threat modeling, test-driven development (TDD), and security guardrails directly into the development workflow.

## ✨ Features

* 🤖 AI-powered Shopping Assistant
* 🎟️ Single-use discount code redemption
* 🛒 Secure checkout workflow
* 🔒 Input validation using Pydantic
* 🛡️ STRIDE Threat Modeling
* 🔍 Custom Semgrep security scanning
* 🚦 Git pre-commit security hooks
* 🧪 Outcome-based Pytest security testing
* 📋 TDD Planning Gate
* 🤖 Autonomous AI self-remediation
* 🌐 Google ADK Playground support

---

## 🏗️ Project Architecture

```
User
   │
   ▼
Google ADK Agent
   │
   ├── Shopping Assistant
   ├── Discount Redemption Tool
   ├── Checkout Tool
   └── Security Validation
            │
            ▼
Security Guardrails
├── STRIDE Threat Model
├── Semgrep
├── Pre-Commit Hooks
├── Agent Hooks
└── Pytest Security Tests
```

---

## 🛠️ Tech Stack

* Python
* Google Agent Development Kit (ADK) 2.0
* Google Gemini
* Pydantic
* Pytest
* Semgrep
* Pre-commit
* Git
* Antigravity IDE

---

## 🔐 Security Features

* STRIDE Threat Modeling
* Custom Semgrep Rules
* Git Pre-Commit Security Gates
* Agent Tool Validation Hooks
* Outcome-Based Security Testing
* TDD Security Planning Gate
* Environment Variable Based API Key Management

---

## 📂 Project Structure

```
shopping-assistant/
│
├── app/
├── tests/
├── .agents/
├── .semgrep/
├── threat_model.md
├── pyproject.toml
└── README.md
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/ayushk2263-lang/shopping-assistant-secure-agent.git
```

### Install Dependencies

```bash
uv sync
```

### Configure Environment

Create a `.env` file and add:

```text
GEMINI_API_KEY=YOUR_API_KEY
GOOGLE_GENAI_USE_VERTEXAI=False
```

### Run the Playground

```bash
uv run adk web . --port 8081
```

Open:

```
http://127.0.0.1:8081
```

---

## 🧪 Testing

Run all tests:

```bash
uv run pytest
```

Run linting:

```bash
agents-cli lint
```

---

## 📸 Demo

Add screenshots of:

* ADK Playground
* Shopping Assistant interaction
* Threat Model output
* Successful security tests

---

## 📚 What I Learned

Through this project I gained hands-on experience with:

* Secure AI Agent Development
* Google ADK 2.0
* STRIDE Threat Modeling
* Secure Tool Design
* Test-Driven Development
* Automated Security Validation
* AI-assisted Software Engineering

---

## 📄 License

This project was developed for educational purposes as part of Kaggle's **5-Day AI Agents: Intensive Vibe Coding** course with Google.
