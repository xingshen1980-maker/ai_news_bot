#!/usr/bin/env python3
"""PC Market Weekly Report - Competitive analysis for PC industry"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pc_collector import get_all_pc_news
from pc_analyzer import analyze_pc_market
from image_generator import generate_report_image
from email_sender import send_email

# Configuration
RECIPIENT_EMAIL = os.environ.get("PC_RECIPIENT_EMAIL", "24318868@qq.com")
LOG_FILE = os.path.join(os.path.dirname(__file__), "pc_bot.log")
REPORT_IMAGE = os.path.join(os.path.dirname(__file__), "pc_report.png")

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

def main():
    """Main function to run the PC market weekly report"""
    log("=" * 50)
    log("PC Market Weekly Report Bot Started")

    try:
        # Step 1: Collect news
        log("Collecting PC market news from multiple sources...")
        news_items = get_all_pc_news()
        log(f"Collected {len(news_items)} news items")

        if not news_items:
            log("No news items found. Exiting.")
            return

        # Step 2: Analyze market
        log("Analyzing PC market with Claude AI...")
        analysis = analyze_pc_market(news_items)
        log("Analysis complete")

        # Step 3: Generate report image
        log("Generating report image...")
        generate_report_image(analysis, news_items, REPORT_IMAGE)
        log(f"Report image saved to {REPORT_IMAGE}")

        # Step 4: Send email
        log(f"Sending email to {RECIPIENT_EMAIL}...")
        date_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"💻 PC Market Weekly Analysis - Dell/HP/Lenovo vs Apple - {date_str}"

        success = send_email(RECIPIENT_EMAIL, subject, analysis, REPORT_IMAGE)

        if success:
            log("PC market weekly report sent successfully!")
        else:
            log("Failed to send email")

    except Exception as e:
        log(f"Error: {str(e)}")
        import traceback
        log(traceback.format_exc())

    log("PC Market Weekly Report Bot Finished")
    log("=" * 50)

if __name__ == "__main__":
    main()
