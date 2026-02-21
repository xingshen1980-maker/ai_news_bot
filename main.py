#!/usr/bin/env python3
"""AI News Bot - Main script to collect, analyze and send daily AI news report"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_collector import get_all_news
from analyzer import analyze_news
from image_generator import generate_report_image
from email_sender import send_email

# Configuration
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "your_email@qq.com")
LOG_FILE = os.path.join(os.path.dirname(__file__), "bot.log")
REPORT_IMAGE = os.path.join(os.path.dirname(__file__), "report.png")

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

def main():
    """Main function to run the AI news bot"""
    log("=" * 50)
    log("AI News Bot Started")

    try:
        # Step 1: Collect news
        log("Collecting AI news from multiple sources...")
        news_items = get_all_news()
        log(f"Collected {len(news_items)} news items")

        if not news_items:
            log("No news items found. Exiting.")
            return

        # Step 2: Analyze news
        log("Analyzing news with Claude AI...")
        analysis = analyze_news(news_items)
        log("Analysis complete")

        # Step 3: Generate report image
        log("Generating report image...")
        generate_report_image(analysis, news_items, REPORT_IMAGE)
        log(f"Report image saved to {REPORT_IMAGE}")

        # Step 4: Send email with image
        log(f"Sending email to {RECIPIENT_EMAIL}...")
        date_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"🤖 Daily AI Intelligence Report - {date_str}"

        success = send_email(RECIPIENT_EMAIL, subject, analysis, REPORT_IMAGE)

        if success:
            log("✅ Daily AI report sent successfully!")
        else:
            log("❌ Failed to send email")

    except Exception as e:
        log(f"❌ Error: {str(e)}")
        import traceback
        log(traceback.format_exc())

    log("AI News Bot Finished")
    log("=" * 50)

if __name__ == "__main__":
    main()
