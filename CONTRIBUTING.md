# 🤝 Contributing to NeuraCity

Welcome to NeuraCity — the world’s first AI Nervous System for Smart Campuses & Institutions! 🚀  
This document outlines the rules and best practices for contributing to this collaborative AI product.

---

## 📁 Folder-Level Ownership

Each module or component lives in a dedicated folder:

| Folder | Owner | Responsibility |
|--------|--------|----------------|
| `modules/cv_watchtower/` | Member A | Computer Vision |
| `modules/neuranlp_agent/` | Member B | LLM + Chatbot |
| `modules/iot_pulsenet/` | Member C | IoT + Sensors |
| `frontend/` | Member D | UI + Dashboard |
| `backend/` | Member E | API services |
| `docs/` | All | Vision, design |

✅ **Only modify files in your assigned folder** unless explicitly collaborating with the owner.

---

## 🛡️ Git Rules

### ✅ Daily Workflow

1. **Pull latest code before coding**
   ```bash
   git pull origin main
   ```
2. **Stage only your files**
    ```bash
    git add modules/module_name/*
    ```
3. **Commit with a message**
    ```bash
    git commit -m "Added fall detection model - v1"
    ```
4. **Push your changes**
    ```bash
    git push origin main
    ```
5. **If Push shows error (Optional)**
    ```bash
    git pull --rebase origin main
    ```
    Again run the Step-4

---

## ❌ Don’t
	•	Never run git add .
	•	Never modify someone else’s module
	•	Never force push unless explicitly approved

## ✅ Naming Conventions
	Commits: verb: summary
 	Example: add: YOLO inference for fall detection

---

## 📦 Folder Setup (Template)

    ```bash
    README.md           # Explains what this module does
    models/             # Model weights or configs
    scripts/            # Training, inference code
    data/               # Sample data (if small)
    ```

---

## 🔬 Testing

Add related test files in tests/:
    ```bash
    tests/test_cv_watchtower.py
    tests/test_neuranlp_agent.py
    ```
Use pytest or unittest for coverage.

---

## 🧠 Tips
	•	Work modularly — your folder is your responsibility.
	•	Push all commits once per day.
	•	Document what you’ve done inside your folder’s README.md.

---

## 🙌 Need Help?

Ask the team lead or open an issue in GitHub. Collaboration and clean code > rushing and bugs.

---

Thanks for being part of the NeuraCity mission! 💙
Let me know if you'd like this:
- Auto-added to your local repo
- Modified per actual member names
- Split into “contributor onboarding” and “advanced workflow”

Shall we continue by generating the initial `README.md` too?
