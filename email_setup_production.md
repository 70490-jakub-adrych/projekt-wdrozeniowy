# Email Setup for Production

## Setting up Postfix on Linux Server

### 1. Install Postfix
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postfix mailutils

# CentOS/RHEL
sudo yum install postfix mailx
```

### 2. Configure Postfix
Edit `/etc/postfix/main.cf`:
