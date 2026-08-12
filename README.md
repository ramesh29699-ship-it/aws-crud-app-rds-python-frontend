# 🌐 Sudharam Online — AWS 3‑Tier Cloud Architecture

> **Subject:** AWS 3‑Tier Scalable Web Application Deployment  
> **Repository:** sudharam-online-cloud-architecture  
> **Author:** Ramesh (Hyderabad, India)

## 📖 About the Project
This repository contains the complete setup and documentation for deploying a 3‑tier web application on AWS.  
It includes domain configuration, DNS routing, load balancing, backend API integration, database connectivity, and auto scaling for high availability.

### 🧩 Key AWS Services
- Route 53 — Domain & DNS management  
- Application Load Balancer (ALB) — Traffic distribution  
- EC2 — Frontend (Nginx) and Backend (Flask) servers  
- RDS — Managed database  
- Auto Scaling Group — Elastic backend scaling  
- ACM — SSL certificate for HTTPS  
- CloudWatch — Monitoring and alerts

### 📂 Repository Contents
| Folder | Description |
|--------|--------------|
| `/frontend` | Nginx configuration and static files |
| `/backend` | Flask API source code |
| `/docs` | Architecture diagram and project documentation |
| `/scripts` | Deployment and user‑data scripts |
| `README.md` | Project overview and setup guide |

---

## 🚀 Live Demo
Visit: [https://sudharam.online](https://sudharam.online)

---

## 🧠 Learning Outcomes
- Understanding AWS networking and DNS routing  
- Configuring ALBs and target groups  
- Implementing Auto Scaling Groups  
- Managing secure connections with ACM  
- Building production‑grade cloud architecture

---

## 📜 License
MIT License — free to use and modify.


## 📘 Overview
`sudharam.online` is a fully deployed 3‑tier web application hosted on AWS.  
It demonstrates modern cloud architecture using **Route 53**, **Application Load Balancers**, **EC2**, **RDS**, and **Auto Scaling Groups** for high availability and scalability.

---

## 🏗️ Architecture Summary
User → Route 53 → Frontend ALB → Nginx EC2s
↓
Backend ALB → Flask EC2s (ASG)
↓
RDS (MySQL)



### Components
| Layer | Service | Description |
|-------|----------|-------------|
| **Frontend** | Nginx EC2 + Public ALB | Serves UI and proxies API requests |
| **Backend** | Flask EC2 + Private ALB | Handles business logic and connects to DB |
| **Database** | Amazon RDS | Stores persistent data securely |
| **DNS** | Route 53 | Custom domain `sudharam.online` |
| **Scaling** | Auto Scaling Group | Automatically adjusts backend EC2 count |

---

## 🚀 Deployment Steps
1. **Domain Setup**
   - Register domain on GoDaddy.
   - Update nameservers to AWS Route 53.
   - Create hosted zone for `sudharam.online`.

2. **DNS Records**
   - A record (Alias) for root → Frontend ALB.  
   - A record (Alias) for `www` → Frontend ALB.

3. **Frontend ALB**
   - Listener on port 80 (HTTP) and 443 (HTTPS).  
   - Target group → Nginx EC2s.  
   - ACM certificate for SSL.

4. **Backend ALB**
   - Internal ALB in private subnets.  
   - Target group → Flask EC2s.  
   - Nginx proxies `/products` → backend ALB.

5. **Database**
   - RDS in private subnet.  
   - Security group allows 3306 only from backend SG.

6. **Auto Scaling Group**
   - Launch template with Flask AMI + user‑data script.  
   - Min = 1, Desired = 2, Max = 4.  
   - Scaling policy: CPU > 70% → scale out; < 30% → scale in.  
   - Health check type: ELB.

---

## 🔐 Security Groups
| SG | Allowed Ports | Source |
|----|----------------|--------|
| Frontend SG | 80, 443 | 0.0.0.0/0 |
| Backend SG | 5000 | Frontend SG |
| DB SG | 3306 | Backend SG |

---

## 📊 Monitoring
- CloudWatch alarms for CPU/memory.  
- ALB access logs enabled.  
- RDS enhanced monitoring.

---

## 🧩 Tech Stack
- **Frontend:** Nginx, HTML/CSS/JS  
- **Backend:** Python Flask  
- **Database:** MySQL (RDS)  
- **Cloud:** AWS EC2, ALB, Route 53, ACM, ASG  
- **Tools:** Git, VS Code, curl, nslookup

---

## 🔮 Future Enhancements
- CI/CD pipeline with CodePipeline + CodeDeploy  
- CloudFront CDN for global caching  
- AWS WAF for security hardening  
- Terraform/IaC for automated provisioning  

---

## 👨‍💻 Author
**Ramesh** — Cloud & DevOps Engineer  
Hyderabad, India  
Passionate about scalable cloud architectures and automation.

---

## 📜 License
This project is licensed under the MIT License — feel free to use and modify.
