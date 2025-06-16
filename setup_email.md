# Email Configuration Guide

## Quick Setup for Gmail:

1. **Copy the environment file:**
   ```bash
   copy config.env.example .env
   ```

2. **Edit the .env file with your details:**
   ```env
   # Gmail Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   MANAGER_EMAIL=manager@company.com
   SENDER_EMAIL=noreply@risktracker.com
   ```

3. **Get Gmail App Password:**
   - Go to Google Account Settings
   - Security → 2-Factor Authentication → App Passwords
   - Generate password for "Risk Tracker"
   - Use this password in SMTP_PASSWORD

4. **Restart the application:**
   ```bash
   python run.py
   ```

## Test Email Functionality:
- Go to any epic → Click "Request Date Change"
- Fill in reason and proposed date
- Check if email arrives at manager's inbox

## Other Email Providers:
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Use your server settings 