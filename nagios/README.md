# Nagios Monitoring for EduAttend

This directory contains Nagios configuration for monitoring EduAttend application across multiple deployments.

## 📊 What is Monitored

### Production (Render)
- ✅ HTTPS availability (https://edu-attend.onrender.com)
- ✅ Response time
- ✅ SSL certificate validity
- ✅ HTTP status codes

### DevOps Demo (Azure)
- ✅ HTTP availability (http://<azure-ip>:8000)
- ✅ Response time
- ✅ Container health
- ✅ Docker service status

## 🚀 Installation

Nagios is automatically installed by running:

```powershell
cd ../ansible
ansible-playbook playbooks/03-install-nagios.yml
```

## 🌐 Access Nagios

**URL:** `http://<azure-vm-ip>:8080/nagios`

**Default Credentials:**
- Username: `nagiosadmin`
- Password: `nagiosadmin123` (⚠️ Change this!)

## 📊 Dashboard Overview

After installation, you'll see:

### Services
| Host | Service | Check Interval |
|------|---------|----------------|
| eduattend-render | HTTPS | 5 minutes |
| eduattend-render | Response Time | 10 minutes |
| eduattend-azure | HTTP | 5 minutes |
| eduattend-azure | Response Time | 10 minutes |

### Status Indicators
- 🟢 **OK** - Service is functioning normally
- 🟡 **WARNING** - Service has minor issues
- 🔴 **CRITICAL** - Service is down or non-functional
- ⚪ **UNKNOWN** - Unable to determine status

## 🔧 Configuration Files

All configurations are managed by Ansible playbook:

```
/usr/local/nagios/etc/
├── nagios.cfg                    # Main configuration
├── objects/
│   ├── eduattend.cfg            # EduAttend monitoring
│   ├── contacts.cfg             # Alert contacts
│   ├── commands.cfg             # Check commands
│   └── templates.cfg            # Service templates
└── htpasswd.users               # Web authentication
```

## 🔔 Email Alerts

**Configured Email:** rauhan.official@gmail.com

**Alert Triggers:**
- Service goes CRITICAL (down)
- Service remains WARNING for 10+ minutes
- Service recovers (OK status restored)

**To update email:**
```powershell
# Edit inventory file
nano ../ansible/inventory/azure_hosts.yml

# Change: nagios_admin_email: your-email@example.com

# Rerun Nagios playbook
ansible-playbook ../ansible/playbooks/03-install-nagios.yml
```

## 📈 Custom Checks

### Add New Service Check

1. SSH into Azure VM:
```bash
ssh -i ../.ssh/azure_vm_key azureuser@<vm-ip>
```

2. Edit configuration:
```bash
sudo nano /usr/local/nagios/etc/objects/eduattend.cfg
```

3. Add service definition:
```nagios
define service {
    use                     generic-service
    host_name               eduattend-azure
    service_description     Database Connection
    check_command           check_tcp!5432
    check_interval          10
    retry_interval          2
}
```

4. Verify and reload:
```bash
sudo /usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
sudo systemctl reload nagios
```

## 🐛 Troubleshooting

### Nagios Web Interface Not Loading

**Check Apache status:**
```bash
sudo systemctl status apache2
```

**Check if port 8080 is open:**
```bash
sudo netstat -tulpn | grep 8080
```

**Restart services:**
```bash
sudo systemctl restart apache2
sudo systemctl restart nagios
```

### Service Showing as CRITICAL

**Check from VM:**
```bash
# Test HTTP check manually
/usr/local/nagios/libexec/check_http -H edu-attend.onrender.com -S

# Test local app
/usr/local/nagios/libexec/check_http -H localhost -p 8000
```

### Forgot Nagios Password

**Reset password:**
```bash
sudo htpasswd /usr/local/nagios/etc/htpasswd.users nagiosadmin
# Enter new password when prompted
```

## 📊 Useful Commands

```bash
# Check Nagios status
sudo systemctl status nagios

# View Nagios logs
sudo tail -f /usr/local/nagios/var/nagios.log

# Verify configuration
sudo /usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg

# Restart Nagios
sudo systemctl restart nagios

# View all monitored hosts
/usr/local/nagios/bin/nagios -s /usr/local/nagios/etc/nagios.cfg
```

## 🎓 Understanding Monitoring

**Check Interval:** How often Nagios checks service  
**Retry Interval:** How often to recheck if service fails  
**Max Check Attempts:** Number of retries before marking CRITICAL  
**Notification Interval:** How often to send alerts  

**Example:**
- Service fails → Check 1 (WARNING)
- Wait 1 min → Check 2 (WARNING)
- Wait 1 min → Check 3 (CRITICAL) → Send Alert
- Every 30 min → Send reminder until fixed

## 📱 Mobile Access

Nagios web interface is mobile-responsive. Access from your phone:

```
http://<azure-vm-ip>:8080/nagios
```

## 🔐 Security Recommendations

For production:
1. Enable HTTPS for Nagios
2. Change default password
3. Restrict access by IP
4. Enable firewall rules
5. Use strong authentication

## 📚 Additional Resources

- [Nagios Core Documentation](https://www.nagios.org/documentation/)
- [Plugin Development](https://nagios-plugins.org/doc/guidelines.html)
- [Monitoring Best Practices](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/monitoring-intro.html)

## ✅ Success Indicators

After setup, verify:
- [ ] Nagios web interface accessible
- [ ] All services show status (not PENDING)
- [ ] Render app shows OK (green)
- [ ] Azure app shows OK (green)
- [ ] Email alerts configured
- [ ] Can login with credentials

**Status:** All green? ✅ Monitoring is working!
