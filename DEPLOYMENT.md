# Deployment Guide - CBT Examination System

## 🚀 Production Deployment

This guide covers deploying the CBT Examination System to production using common hosting platforms.

---

## 📋 Pre-Deployment Checklist

- [ ] DEBUG = False in settings.py
- [ ] SECRET_KEY changed to random value
- [ ] ALLOWED_HOSTS configured with your domain
- [ ] Database migrated
- [ ] Static files collected
- [ ] HTTPS certificate obtained
- [ ] Environment variables set
- [ ] Backup strategy in place
- [ ] Email configuration (optional)

---

## 🔧 Django Settings Changes for Production

### settings.py modifications:

```python
# SECURITY
DEBUG = False
SECRET_KEY = 'your-new-random-secret-key-here-use-environment-variable'
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# Database - Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static & Media Files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/cbt/staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/cbt/media'

# Email (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

---

## 🗄️ Database Setup (PostgreSQL)

### On your server:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

### In PostgreSQL console:

```sql
CREATE DATABASE cbt_db;
CREATE USER cbt_user WITH PASSWORD 'secure_password_here';
ALTER ROLE cbt_user SET client_encoding TO 'utf8';
ALTER ROLE cbt_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cbt_user SET default_transaction_deferrable TO on;
ALTER ROLE cbt_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cbt_db TO cbt_user;
\q
```

---

## 📦 Update requirements.txt

```bash
# Add production dependencies
pip install gunicorn psycopg2-binary python-decouple
pip freeze > requirements.txt
```

---

## 🌐 Web Server Setup (Nginx + Gunicorn)

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Create Gunicorn service file

**File:** `/etc/systemd/system/cbt-app.service`

```ini
[Unit]
Description=CBT Examination System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cbt
ExecStart=/var/www/cbt/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/cbt/cbt.sock \
    cbt_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Create Nginx configuration

**File:** `/etc/nginx/sites-available/cbt`

```nginx
upstream cbt_app {
    server unix:/var/www/cbt/cbt.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /var/www/cbt/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/cbt/media/;
    }
    
    location / {
        proxy_pass http://cbt_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Enable Nginx site

```bash
sudo ln -s /etc/nginx/sites-available/cbt /etc/nginx/sites-enabled/cbt
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (runs daily)
sudo certbot renew --quiet
```

---

## 🚀 Deployment Steps

### 1. Prepare Server

```bash
# Create directory
sudo mkdir -p /var/www/cbt
sudo chown $USER:$USER /var/www/cbt

# Clone/copy your code
cd /var/www/cbt
git clone your-repo.git .
# or cp -r /path/to/local/CBT_Django/* .
```

### 2. Setup Environment

```bash
cd /var/www/cbt

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=cbt_db
DB_USER=cbt_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
EOF

# Load environment variables
export $(cat .env | xargs)
```

### 3. Setup Django

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load sample data (optional)
python manage.py shell < load_sample_data.py
```

### 4. Start Services

```bash
# Start Gunicorn
sudo systemctl start cbt-app
sudo systemctl enable cbt-app

# Check status
sudo systemctl status cbt-app

# View logs
sudo journalctl -u cbt-app -f
```

### 5. Verify Setup

```bash
# Test SSL
curl -I https://yourdomain.com

# Check Nginx
curl http://localhost/

# View Nginx logs
sudo tail -f /var/access_log
sudo tail -f /var/error_log
```

---

## 📝 Backup Strategy

### Automated Daily Backup

**File:** `/var/www/cbt/backup.sh`

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/cbt"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump cbt_db > $BACKUP_DIR/cbt_db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/cbt/media/

# Backup code (optional)
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /var/www/cbt/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Schedule with Cron

```bash
# Edit cron jobs
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * /var/www/cbt/backup.sh >> /var/log/cbt_backup.log 2>&1
```

---

## 📊 Monitoring & Logs

### Check Application Status

```bash
# Django health check
curl -H "Host: yourdomain.com" http://localhost/login/

# Database connection
python manage.py dbshell

# Application logs
sudo tail -100 /var/log/cbt_application.log
```

### Setup Log Rotation

**File:** `/etc/logrotate.d/cbt`

```
/var/log/cbt_application.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload cbt-app > /dev/null 2>&1 || true
    endscript
}
```

---

## 🔄 Updating Code

### Deploy Updates

```bash
cd /var/www/cbt
source venv/bin/activate

# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart cbt-app
```

---

## 🛡️ Security Hardening

### Additional Security Measures

```bash
# Keep system updated
sudo apt-get update
sudo apt-get upgrade

# Setup firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp  # PostgreSQL (internal only)

# Disable unnecessary services
sudo systemctl disable telnet
sudo systemctl disable ftp
```

---

## 🐛 Troubleshooting

### Gunicorn won't start

```bash
# Check syntax
sudo systemctl status cbt-app
sudo journalctl -u cbt-app -n 50

# Manually test
cd /var/www/cbt
source venv/bin/activate
gunicorn cbt_project.wsgi:application
```

### Database connection issues

```bash
# Test PostgreSQL connection
psql -U cbt_user -d cbt_db -h localhost
```

### Static files not loading

```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/cbt/staticfiles
```

### High memory usage

```bash
# Adjust Gunicorn workers in service file
# More workers = more memory usage
# Formula: (2 x CPU_cores) + 1
# For 2 cores: 5 workers
ExecStart=/var/www/cbt/venv/bin/gunicorn \
    --workers 5 \
    ...
```

---

## 🎯 Performance Optimization

### Database Optimization

```python
# In views.py, use select_related and prefetch_related
answers = StudentAnswer.objects.select_related('question').filter(exam=exam)
```

### Caching

```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### CDN for Static Files

Use CloudFront or similar CDN for static files and CSS.

---

## 🚨 Emergency Recovery

### Restore from Backup

```bash
# Stop application
sudo systemctl stop cbt-app

# Restore database
psql cbt_db < /var/backups/cbt/cbt_db_YYYYMMDD_HHMMSS.sql

# Restore media files
tar -xzf /var/backups/cbt/media_YYYYMMDD_HHMMSS.tar.gz -C /

# Restart application
sudo systemctl start cbt-app
```

---

## 📞 Production Support

For production issues:
1. Check logs: `sudo journalctl -u cbt-app -f`
2. Verify database: `psql -U cbt_user -d cbt_db -c "SELECT COUNT(*) FROM cbt_app_question;"`
3. Test connectivity: `curl -I https://yourdomain.com`
4. Check disk space: `df -h`
5. Monitor memory: `free -h`

---

Happy deployment! 🚀🎓
