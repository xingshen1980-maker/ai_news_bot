#!/usr/bin/env python3
"""Email Sender - Send reports via QQ Mail SMTP"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# QQ Mail SMTP settings
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "24318868@qq.com"
SENDER_PASSWORD = "cdxdjhsvmahbbijg"

def send_email(to_email, subject, html_content, image_path=None):
    """Send email via QQ Mail SMTP with optional image attachment"""
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    # Create alternative part for HTML
    alt_part = MIMEMultipart('alternative')

    # If image exists, embed it in HTML
    if image_path and os.path.exists(image_path):
        html_with_image = f"""
        <html>
        <body style="background-color: #1a1a2e; padding: 20px;">
            <div style="max-width: 1200px; margin: 0 auto;">
                <img src="cid:report_image" style="width: 100%; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            </div>
            <div style="margin-top: 30px; padding: 20px; background: #16213e; border-radius: 10px; color: #fff;">
                <h3 style="color: #e94560;">📋 Full Analysis Report</h3>
                <pre style="white-space: pre-wrap; font-family: Arial, sans-serif; color: #a0a0a0; font-size: 14px;">{html_content}</pre>
            </div>
        </body>
        </html>
        """
        html_part = MIMEText(html_with_image, 'html', 'utf-8')
        alt_part.attach(html_part)
        msg.attach(alt_part)

        # Attach image
        with open(image_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<report_image>')
            img.add_header('Content-Disposition', 'inline', filename='report.png')
            msg.attach(img)

        # Also attach as downloadable file
        with open(image_path, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename='AI_Report.png')
            msg.attach(attachment)
    else:
        html_part = MIMEText(html_content, 'html', 'utf-8')
        alt_part.attach(html_part)
        msg.attach(alt_part)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("Testing QQ Mail SMTP...")
    success = send_email(SENDER_EMAIL, "Test Email", "<h1>Test</h1>")
    print("✅ Done" if success else "❌ Failed")
