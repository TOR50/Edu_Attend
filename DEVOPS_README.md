# 🎓 EduAttend - DevOps Implementation

**AI-Powered Attendance System with Complete DevOps Pipeline**

[![CI/CD](https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)

---

## 📋 Overview

EduAttend is a face recognition-based attendance management system built with Django, demonstrating modern DevOps practices including **Infrastructure as Code (Terraform)**, **Configuration Management (Ansible)**, and **Monitoring (Nagios)**.

### 🌐 Live Deployments

- **Production:** https://edu-attend.onrender.com (Render PaaS)
- **DevOps Demo:** Azure VM (Deployed via Terraform + Ansible)
- **Monitoring:** Nagios dashboard monitoring both deployments

---

## 🚀 Features

### Application Features
- ✅ **Face Recognition** - Real-time attendance using OpenCV & dlib
- ✅ **Multi-Role System** - Admin, Teacher, Student dashboards
- ✅ **Academic Year Management** - Track attendance across years
- ✅ **Cloud Storage** - Cloudinary for media, Neon for PostgreSQL
- ✅ **Responsive UI** - Mobile-friendly design

### DevOps Features
- ✅ **Infrastructure as Code** - Terraform provisions Azure resources
- ✅ **Configuration Management** - Ansible automates deployment
- ✅ **Continuous Monitoring** - Nagios tracks uptime & performance
- ✅ **CI/CD Pipeline** - GitHub Actions for automated testing & deployment
- ✅ **Multi-Cloud** - Production on Render, demo on Azure
- ✅ **Containerization** - Docker for consistent environments

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Repository                           │
│                                                              │
│  Developers Push Code → GitHub Actions CI/CD                │
│                         ├─ Build & Test                     │
│                         ├─ Security Scanning                │
│                         ├─ Docker Build                     │
│                         └─ Deploy to Render                 │
└────────────────────────┬────────────────────────────────────┘
                         │
              Manual: DevOps Demo Pipeline
                         │
         ┌───────────────┴────────────────┐
         │                                │
    ┌────▼────┐                      ┌────▼────┐
    │Terraform│                      │ Ansible │
    │(Infra)  │─────────────────────>│(Deploy) │
    └─────────┘                      └─────────┘
         │                                │
         └────────────┬───────────────────┘
                      ▼
         ┌─────────────────────────┐
         │   Azure Virtual Machine │
         │  ┌──────────────────┐   │
         │  │  Docker Container│   │
         │  │  Django App:8000 │   │
         │  └──────────────────┘   │
         │  ┌──────────────────┐   │
         │  │ Nagios Monitor   │   │
         │  │ Dashboard :8080  │   │
         │  └──────────────────┘   │
         └─────────────────────────┘
                      │
          ┌───────────┴──────────┐
          │                      │
    ┌─────▼──────┐      ┌────────▼──────┐
    │   Render   │      │     Azure     │
    │ Production │      │   Demo App    │
    └────────────┘      └───────────────┘
```

---

## 📂 Project Structure

```
Django App/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml                    # Production CI/CD
│       └── devops-demo-pipeline.yml     # Terraform + Ansible
├── terraform/                           # Infrastructure as Code
│   ├── main.tf                         # Azure resources
│   ├── variables.tf                    # Configuration
│   ├── outputs.tf                      # Deployment info
│   └── README.md                       # Terraform guide
├── ansible/                            # Configuration Management
│   ├── inventory/
│   │   └── azure_hosts.yml            # VM inventory
│   ├── playbooks/
│   │   ├── 01-setup-vm.yml           # VM setup
│   │   ├── 02-deploy-app.yml         # App deployment
│   │   └── 03-install-nagios.yml     # Monitoring
│   └── README.md                      # Ansible guide
├── nagios/                            # Monitoring Configuration
│   └── README.md                      # Nagios guide
├── docs/                              # Documentation
│   └── DEVOPS_SETUP_GUIDE.md         # Complete setup guide
├── core/                              # Django application
├── config/                            # Django settings
├── Dockerfile                         # Container definition
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🛠️ Technology Stack

### Application
- **Backend:** Django 5.0, Python 3.11
- **AI/ML:** face_recognition, OpenCV, dlib, NumPy
- **Database:** PostgreSQL (Neon), SQLite (dev)
- **Storage:** Cloudinary (media files)
- **Web Server:** Gunicorn, WhiteNoise

### DevOps
- **IaC:** Terraform 1.6+
- **Config Mgmt:** Ansible 2.15+
- **Monitoring:** Nagios Core 4.x
- **CI/CD:** GitHub Actions
- **Containers:** Docker, Docker Compose
- **Cloud:** Azure, Render

---

## 🚀 Quick Start

### Option 1: Access Production (Instant)
```
🌐 https://edu-attend.onrender.com
```

### Option 2: DevOps Demo Deployment (45 minutes)

**Prerequisites:**
- Azure Student Subscription
- Azure CLI, Terraform, Ansible installed
- GitHub Personal Access Token

**Deploy:**
```powershell
# 1. Clone repository
git clone https://github.com/TOR50/TOR50-Capstone_KC739_CSE399.git
cd "TOR50-Capstone_KC739_CSE399/Django App"

# 2. Login to Azure
az login
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# 3. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 4. Configure and deploy application
cd ../ansible
# Update inventory/azure_hosts.yml with VM IP
ansible-playbook playbooks/01-setup-vm.yml
ansible-playbook playbooks/02-deploy-app.yml
ansible-playbook playbooks/03-install-nagios.yml

# 5. Access deployment
# Application: http://<vm-ip>:8000
# Nagios:      http://<vm-ip>:8080/nagios
```

**📖 Detailed Guide:** See [`docs/DEVOPS_SETUP_GUIDE.md`](docs/DEVOPS_SETUP_GUIDE.md)

---

## 📊 DevOps Demonstration

### What This Project Demonstrates

#### 1. Infrastructure as Code (Terraform)
- Provisions Azure VM, networking, storage
- Reproducible infrastructure
- Version-controlled configuration
- Cost-effective resource management

**Files:** [`terraform/`](terraform/)

#### 2. Configuration Management (Ansible)
- Automated server setup
- Application deployment
- Monitoring installation
- Idempotent operations

**Files:** [`ansible/`](ansible/)

#### 3. Continuous Monitoring (Nagios)
- Uptime monitoring (Render + Azure)
- HTTP health checks
- Response time tracking
- Alert notifications

**Files:** [`nagios/`](nagios/)

#### 4. CI/CD Pipeline (GitHub Actions)
- Automated testing
- Security scanning (Bandit, Safety, Trivy)
- Container building & registry
- Multi-environment deployment

**Files:** [`.github/workflows/`](.github/workflows/)

---

## 🎓 College Project Highlights

### Why This Project is Impressive

✅ **Real-World Application** - Solves actual attendance management problem  
✅ **Modern Tech Stack** - Uses industry-standard tools  
✅ **Complete DevOps** - Shows full software lifecycle  
✅ **Cloud Native** - Multi-cloud deployment (Azure + Render)  
✅ **Automation** - Infrastructure and deployment fully automated  
✅ **Monitoring** - Proactive system health tracking  
✅ **Security** - Automated vulnerability scanning  
✅ **Documentation** - Comprehensive guides and README  

### Demonstration Flow (10 minutes)

1. **Show Production** (2 min)
   - Access live Render deployment
   - Demo face recognition features
   - Explain architecture

2. **Infrastructure as Code** (2 min)
   - Walk through Terraform configuration
   - Run `terraform plan`
   - Explain resource provisioning

3. **Configuration Management** (3 min)
   - Show Ansible playbooks
   - Explain automation benefits
   - Demo deployment process

4. **Monitoring** (2 min)
   - Access Nagios dashboard
   - Show service status
   - Explain alert system

5. **CI/CD Pipeline** (1 min)
   - Show GitHub Actions workflow
   - Display successful pipeline run
   - Explain automation value

---

## 🔐 Security Features

- ✅ SSH key-based authentication
- ✅ Azure Network Security Groups (firewall)
- ✅ UFW firewall on VM
- ✅ Fail2ban for brute-force protection
- ✅ HTTPS on production (Render)
- ✅ Environment variable secrets
- ✅ Automated dependency scanning
- ✅ Docker image vulnerability scanning

---

## 📈 Monitoring & Observability

### What's Monitored

| Service | Check | Interval | Alert |
|---------|-------|----------|-------|
| Render Production | HTTPS | 5 min | Email |
| Azure Demo | HTTP | 5 min | Email |
| Response Time | HTTP | 10 min | Email |
| Database | Connection | On-demand | Log |
| Docker | Container Status | On-demand | Log |

### Access Monitoring

```
🌐 Nagios Dashboard: http://<azure-vm-ip>:8080/nagios
👤 Username: nagiosadmin
🔑 Password: nagiosadmin123
```

---

## 💰 Cost Breakdown

### Azure Resources (Monthly)

| Resource | Specs | Cost |
|----------|-------|------|
| VM (B2s) | 2 vCPU, 4GB RAM | ~$30 |
| Storage | Standard LRS | ~$2 |
| Bandwidth | Normal usage | ~$3 |
| **Total** | | **~$35** |

### Cost Optimization

- ✅ Use **Azure Student Pack** ($100 free credits)
- ✅ Stop VM when not demoing (`az vm deallocate`)
- ✅ Use Render free tier for production
- ✅ Neon PostgreSQL free tier
- ✅ Cloudinary free tier

**Total Project Cost:** $0 with free tiers + student credits!

---

## 🧪 Testing

### Run Tests Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run Django tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### CI/CD Testing

Every push triggers:
- Unit tests
- Security scanning (Bandit)
- Dependency checking (Safety)
- Container image scanning (Trivy)
- Django deployment checks

---

## 📚 Documentation

- **[Complete Setup Guide](docs/DEVOPS_SETUP_GUIDE.md)** - Full deployment instructions
- **[Terraform Guide](terraform/README.md)** - Infrastructure provisioning
- **[Ansible Guide](ansible/README.md)** - Configuration management
- **[Nagios Guide](nagios/README.md)** - Monitoring setup
- **Application Docs** - In-code documentation

---

## 🤝 Contributing

This is a college project, but contributions for learning purposes are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is part of a college capstone project for educational purposes.

---

## 👨‍💻 Author

**Rauhan Ahmed**
- Email: rauhan.official@gmail.com
- University Project: Capstone KC739 CSE399
- GitHub: [@TOR50](https://github.com/TOR50)

---

## 🙏 Acknowledgments

- GitHub Student Developer Pack (Azure credits)
- Render (Free hosting)
- Neon (Free PostgreSQL)
- Cloudinary (Free media storage)
- Open source community

---

## 📞 Support

For setup help or questions:

1. Check [troubleshooting guide](docs/DEVOPS_SETUP_GUIDE.md#troubleshooting)
2. Review component README files
3. Check GitHub Actions logs
4. Open an issue (for learning purposes)

---

## 🎯 Project Status

- ✅ Application: **Production Ready**
- ✅ Terraform: **Configured & Tested**
- ✅ Ansible: **Configured & Tested**
- ✅ Nagios: **Configured & Tested**
- ✅ CI/CD: **Fully Automated**
- ✅ Documentation: **Complete**

**Ready for college demonstration! 🚀**

---

<div align="center">

**⭐ Star this repo if you find it helpful for your DevOps learning! ⭐**

Made with ❤️ for CSE399 Capstone Project

</div>
