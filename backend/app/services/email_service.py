import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings


def generate_verification_token() -> str:
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def get_verification_token_expiry() -> datetime:
    """Get expiration datetime for verification token (24 hours from now)"""
    return datetime.utcnow() + timedelta(hours=24)


def send_verification_email(email: str, name: str, token: str) -> bool:
    """
    Send email verification email to user

    Args:
        email: User's email address
        name: User's name
        token: Verification token

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Verify your Translation Platform account'
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email

        # Create HTML and plain text versions
        text_content = f"""
Hello {name},

Thank you for registering with the Translation Platform!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Translation Platform Team
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #2563eb; margin-top: 0;">Welcome to Translation Platform!</h1>
        <p style="font-size: 16px;">Hello {name},</p>
        <p style="font-size: 16px;">Thank you for registering with the Translation Platform. We're excited to have you on board!</p>
        <p style="font-size: 16px;">Please verify your email address to activate your account:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                Verify Email Address
            </a>
        </div>

        <p style="font-size: 14px; color: #666;">This link will expire in 24 hours.</p>
        <p style="font-size: 14px; color: #666;">If the button above doesn't work, copy and paste this link into your browser:</p>
        <p style="font-size: 12px; color: #888; word-break: break-all;">{verification_url}</p>
    </div>

    <div style="font-size: 12px; color: #888; text-align: center; margin-top: 20px;">
        <p>If you didn't create an account, please ignore this email.</p>
        <p>© 2024 Translation Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""

        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        if settings.SMTP_ENABLED:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        else:
            # For development: just log the verification URL
            print(f"\n{'='*80}")
            print(f"📧 EMAIL VERIFICATION (Development Mode)")
            print(f"{'='*80}")
            print(f"To: {email}")
            print(f"Subject: {msg['Subject']}")
            print(f"\nVerification URL:")
            print(f"{verification_url}")
            print(f"{'='*80}\n")
            return True

    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False


def send_welcome_email(email: str, name: str) -> bool:
    """
    Send welcome email after email verification

    Args:
        email: User's email address
        name: User's name

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Welcome to Translation Platform!'
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email

        text_content = f"""
Hello {name},

Your email has been verified successfully!

You can now log in to your account and start using the Translation Platform.

Login URL: {settings.FRONTEND_URL}/login

Best regards,
Translation Platform Team
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #10b981; margin-top: 0;">✓ Email Verified!</h1>
        <p style="font-size: 16px;">Hello {name},</p>
        <p style="font-size: 16px;">Your email has been verified successfully! Welcome to the Translation Platform.</p>
        <p style="font-size: 16px;">You can now log in to your account and start connecting with translators or clients.</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{settings.FRONTEND_URL}/login"
               style="background-color: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                Log In to Your Account
            </a>
        </div>
    </div>

    <div style="font-size: 12px; color: #888; text-align: center; margin-top: 20px;">
        <p>© 2024 Translation Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""

        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        if settings.SMTP_ENABLED:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        else:
            print(f"\n📧 Welcome email would be sent to: {email}")
            return True

    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False
