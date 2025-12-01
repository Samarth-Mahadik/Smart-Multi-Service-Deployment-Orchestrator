<h1 align="center">🚀 Smart Multi-Service Deployment Orchestrator</h1>
<p align="center">Intelligent Streamlit Dashboard for Deploying, Monitoring & Managing Multiple Containerized Microservices on AWS</p>

The **Smart Multi-Service Deployment Orchestrator** automates deployment, monitoring, and rollback of containerized microservices across AWS EC2 instances. It provides a single dashboard to control all services, perform health checks, and track deployment history.

---

## 📅 Project Duration
**November 2025 – December 2025**

---

## 🔍 Features

✅ Deploy multiple containerized services with a single click  
✅ Stop or restart individual services  
✅ Automatic health checks with self-healing rollback  
✅ Real-time service status & monitoring  
✅ Maintains deployment audit logs with timestamps and image versions  
✅ Streamlit dashboard for centralized control  
✅ Supports zero-downtime deployments across multiple services  

---

## 🧩 Project Architecture

```markdown
Service Definitions (services.json) → Deployment Scripts (deploy/stop/status) 
→ AWS EC2 via boto3 + SSM → Health Checks & Rollback → Logs → Streamlit Dashboard

````

---

## 🛠️ Tech Stack

- **Python 3.x**
- **AWS SDK (boto3)**
- **Streamlit**
- **Docker**
- **Pandas / Numpy**
- **AWS (EC2, SSM, IAM)**

---

## 🚀 Quick Start

```markdown
```bash
git clone https://github.com/Samarth-Mahadik/Smart-Multi-Service-Orchestrator.git
cd Smart-Multi-Service-Orchestrator/dashboard
pip install -r requirements.txt
streamlit run app.py

````

---

## 📊 Dashboard Preview

Displays:

* List of registered services
* Individual service controls: Deploy / Stop / Status
* Service health: 🟢 Healthy / 🔴 Down
* Uptime and last deployed image version
* Deployment audit logs

<img width="1920" height="977" alt="image" src="https://github.com/user-attachments/assets/acdec90d-cb47-4dd7-8cec-de0540e61ece" />

---

## 📹 Demo Video

🎥 [Watch Demo Video](https://www.linkedin.com/posts/samarth-mahadik-8a7965339_devops-cloudcomputing-aws-activity-7401262040440377345-12li?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFUJiL8Bu7meMqELvAFpli67RCHgefR5ucA)

---

## 💼 Author

**👨‍💻 Samarth Mahadik**
AWS & DevOps Enthusiast | AI + Cloud Projects | Pune, India
🔗 [LinkedIn Profile](https://www.linkedin.com/in/samarth-mahadik-8a7965339/)

---
