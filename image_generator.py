#!/usr/bin/env python3
"""Image Generator - Generate beautiful report images"""

import os
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Modern color palette
COLORS = {
    'bg_dark': '#0f0f1a',
    'bg_gradient_top': '#1a1a2e',
    'bg_gradient_bottom': '#0f0f1a',
    'card_bg': '#1e1e32',
    'card_border': '#2d2d4a',
    'accent_red': '#ff4757',
    'accent_blue': '#3742fa',
    'accent_purple': '#8b5cf6',
    'accent_cyan': '#00d4ff',
    'accent_green': '#00d26a',
    'accent_orange': '#ff9f43',
    'accent_yellow': '#feca57',
    'text_white': '#ffffff',
    'text_light': '#e0e0e0',
    'text_muted': '#8888aa',
    'threat_high': '#ff4757',
    'threat_medium': '#feca57',
    'threat_low': '#00d26a',
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size):
    font_paths = [
        # Linux (GitHub Actions)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, coords, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)

def draw_gradient_rect(img, coords, color_top, color_bottom):
    x1, y1, x2, y2 = coords
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = hex_to_rgb(color_top)
    r2, g2, b2 = hex_to_rgb(color_bottom)
    height = y2 - y1
    for y in range(int(y1), int(y2)):
        ratio = (y - y1) / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(x1, y), (x2, y)], fill=(r, g, b))

def create_glow(img, x, y, radius, color, intensity=0.5):
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    r, g, b = hex_to_rgb(color)
    for i in range(radius, 0, -2):
        alpha = int(255 * intensity * (1 - i/radius))
        draw.ellipse([x-i, y-i, x+i, y+i], fill=(r, g, b, alpha))
    return Image.alpha_composite(img.convert('RGBA'), glow)

def parse_analysis_sections(analysis):
    """Parse analysis text into structured sections - supports both Chinese and English"""
    sections = {
        'summary': [],
        'trends': [],
        'competitive': [],
        'hardware': [],
        'threats': [],
        'opportunities': [],
        'actions': []
    }

    current_section = None
    lines = analysis.split('\n')

    for line in lines:
        line_lower = line.lower()
        line_stripped = line.strip()

        # Skip table headers and separators
        if line_stripped.startswith('|') and ('---' in line_stripped or '威胁' in line_stripped or '机遇' in line_stripped or '趋势' in line_stripped or '竞争' in line_stripped):
            continue
        if line_stripped == '|' or line_stripped.replace('-', '').replace('|', '').strip() == '':
            continue

        # Detect section headers (Chinese and English)
        if '执行摘要' in line or 'executive summary' in line_lower or ('summary' in line_lower and '#' in line):
            current_section = 'summary'
            continue
        elif '技术趋势' in line or 'technology trend' in line_lower or ('trend' in line_lower and '#' in line):
            current_section = 'trends'
            continue
        elif '竞争' in line or 'competitive' in line_lower or 'competitor' in line_lower:
            current_section = 'competitive'
            continue
        elif '硬件' in line or 'hardware' in line_lower:
            current_section = 'hardware'
            continue
        elif '威胁' in line or 'threat' in line_lower:
            current_section = 'threats'
            continue
        elif '机遇' in line or '机会' in line or 'opportunit' in line_lower:
            current_section = 'opportunities'
            continue
        elif '建议' in line or '行动' in line or 'action' in line_lower or 'recommend' in line_lower:
            current_section = 'actions'
            continue

        # Parse content
        if current_section and line_stripped:
            # Handle table rows
            if line_stripped.startswith('|'):
                parts = [p.strip() for p in line_stripped.split('|') if p.strip()]
                if len(parts) >= 2:
                    clean_line = ' - '.join(parts[:2])
                    clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_line)
                    if clean_line and len(clean_line) > 3:
                        sections[current_section].append(clean_line)
            # Handle bullet points
            elif line_stripped.startswith('-') or line_stripped.startswith('*') or line_stripped.startswith('•'):
                clean_line = line_stripped.lstrip('-*• ').strip()
                clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_line)
                if clean_line and len(clean_line) > 3:
                    sections[current_section].append(clean_line)
            # Handle numbered items
            elif re.match(r'^\d+\.', line_stripped):
                clean_line = re.sub(r'^\d+\.\s*', '', line_stripped)
                clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_line)
                if clean_line and len(clean_line) > 3:
                    sections[current_section].append(clean_line)

    return sections

def generate_report_image(analysis, news_items, output_path):
    """Generate a beautiful report image"""
    width = 1400
    height = 2000
    margin = 50

    # Create base image with gradient background
    img = Image.new('RGB', (width, height), hex_to_rgb(COLORS['bg_dark']))
    draw_gradient_rect(img, (0, 0, width, height), COLORS['bg_gradient_top'], COLORS['bg_gradient_bottom'])
    draw = ImageDraw.Draw(img)

    # Add subtle glow effects
    img = create_glow(img, 200, 300, 400, COLORS['accent_purple'], 0.15)
    img = create_glow(img, width - 200, 600, 350, COLORS['accent_cyan'], 0.1)
    img = create_glow(img, 300, height - 400, 300, COLORS['accent_red'], 0.1)
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font(52)
    font_subtitle = get_font(22)
    font_section = get_font(28)
    font_body = get_font(18)
    font_small = get_font(14)

    y = margin

    # === HEADER SECTION ===
    header_height = 200
    header_img = Image.new('RGBA', (width, header_height), (0, 0, 0, 0))
    draw_gradient_rect(header_img, (0, 0, width, header_height), '#2d1f4e', '#1a1a2e')
    img.paste(header_img, (0, 0))
    draw = ImageDraw.Draw(img)

    # Decorative line
    draw.rectangle([(0, header_height - 3), (width, header_height)], fill=hex_to_rgb(COLORS['accent_purple']))

    # Title
    title = "AI Intelligence Report"
    draw.text((margin, y + 35), "🤖", font=font_title, fill=hex_to_rgb(COLORS['text_white']))
    draw.text((margin + 70, y + 35), title, font=font_title, fill=hex_to_rgb(COLORS['text_white']))

    # Subtitle
    date_str = datetime.now().strftime("%Y-%m-%d")
    subtitle = f"Daily Strategic Analysis  •  {date_str}  •  Lenovo Group"
    draw.text((margin, y + 105), subtitle, font=font_subtitle, fill=hex_to_rgb(COLORS['text_muted']))

    # Stats cards
    stats_y = y + 145
    news_count = len([n for n in news_items if n.get('type') == 'news'])
    github_count = len([n for n in news_items if n.get('type') == 'github'])
    paper_count = len([n for n in news_items if n.get('type') == 'paper'])

    stats = [
        (str(news_count), "News", COLORS['accent_red']),
        (str(github_count), "GitHub", COLORS['accent_green']),
        (str(paper_count), "Papers", COLORS['accent_blue']),
        (str(len(news_items)), "Total", COLORS['accent_purple']),
    ]

    stat_width = 130
    stat_x = width - margin - (stat_width * len(stats)) - (10 * (len(stats) - 1))
    for num, label, color in stats:
        draw_rounded_rect(draw, (stat_x, stats_y, stat_x + stat_width, stats_y + 42), radius=8,
                         fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(color), width=2)
        draw.text((stat_x + 12, stats_y + 8), num, font=font_section, fill=hex_to_rgb(color))
        bbox = draw.textbbox((0, 0), num, font=font_section)
        num_width = bbox[2] - bbox[0]
        draw.text((stat_x + 18 + num_width, stats_y + 14), label, font=font_small, fill=hex_to_rgb(COLORS['text_muted']))
        stat_x += stat_width + 10

    y = header_height + 25

    # Parse analysis
    sections = parse_analysis_sections(analysis)

    # === EXECUTIVE SUMMARY ===
    summary_items = sections['summary'][:5]
    summary_height = max(80 + len(summary_items) * 32, 120)
    draw_rounded_rect(draw, (margin, y, width - margin, y + summary_height), radius=15,
                     fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(COLORS['card_border']), width=1)

    draw.text((margin + 20, y + 15), "📊", font=font_section, fill=hex_to_rgb(COLORS['accent_cyan']))
    draw.text((margin + 55, y + 15), "Executive Summary / 执行摘要", font=font_section, fill=hex_to_rgb(COLORS['text_white']))
    draw.rectangle([(margin + 20, y + 55), (width - margin - 20, y + 56)], fill=hex_to_rgb(COLORS['card_border']))

    summary_y = y + 70
    for item in summary_items:
        item_text = item[:85] + ('...' if len(item) > 85 else '')
        draw.ellipse([(margin + 25, summary_y + 6), (margin + 33, summary_y + 14)], fill=hex_to_rgb(COLORS['accent_cyan']))
        draw.text((margin + 45, summary_y), item_text, font=font_body, fill=hex_to_rgb(COLORS['text_light']))
        summary_y += 32

    y += summary_height + 20

    # === THREATS & OPPORTUNITIES ===
    card_width = (width - margin * 3) // 2
    card_height = 320

    # Threats Card
    draw_rounded_rect(draw, (margin, y, margin + card_width, y + card_height), radius=15,
                     fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(COLORS['threat_high']), width=2)

    draw.text((margin + 20, y + 15), "⚠️", font=font_section, fill=hex_to_rgb(COLORS['threat_high']))
    draw.text((margin + 55, y + 15), "Threats / 威胁", font=font_section, fill=hex_to_rgb(COLORS['threat_high']))
    draw.rectangle([(margin + 20, y + 55), (margin + card_width - 20, y + 56)], fill=hex_to_rgb(COLORS['card_border']))

    threat_y = y + 70
    for item in sections['threats'][:6]:
        if '🔴' in item or '高' in item or 'high' in item.lower():
            color = COLORS['threat_high']
            level = "HIGH"
        elif '🟡' in item or '中' in item or 'medium' in item.lower():
            color = COLORS['threat_medium']
            level = "MED"
        else:
            color = COLORS['threat_low']
            level = "LOW"

        clean_item = re.sub(r'[🔴🟡🟢]', '', item).strip()
        clean_item = re.sub(r'(高|中|低)\s*[-|]?\s*', '', clean_item)[:55]

        draw_rounded_rect(draw, (margin + 25, threat_y, margin + 68, threat_y + 20), radius=4, fill=hex_to_rgb(color))
        draw.text((margin + 30, threat_y + 2), level, font=font_small, fill=hex_to_rgb(COLORS['bg_dark']))
        draw.text((margin + 78, threat_y), clean_item, font=font_small, fill=hex_to_rgb(COLORS['text_light']))
        threat_y += 38

    # Opportunities Card
    opp_x = margin * 2 + card_width
    draw_rounded_rect(draw, (opp_x, y, opp_x + card_width, y + card_height), radius=15,
                     fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(COLORS['accent_green']), width=2)

    draw.text((opp_x + 20, y + 15), "🚀", font=font_section, fill=hex_to_rgb(COLORS['accent_green']))
    draw.text((opp_x + 55, y + 15), "Opportunities / 机遇", font=font_section, fill=hex_to_rgb(COLORS['accent_green']))
    draw.rectangle([(opp_x + 20, y + 55), (opp_x + card_width - 20, y + 56)], fill=hex_to_rgb(COLORS['card_border']))

    opp_y = y + 70
    for item in sections['opportunities'][:6]:
        star_count = item.count('⭐')
        if star_count >= 3 or '高' in item or 'high' in item.lower():
            stars = "★★★"
            color = COLORS['accent_green']
        elif star_count >= 2 or '中' in item or 'medium' in item.lower():
            stars = "★★☆"
            color = COLORS['accent_yellow']
        else:
            stars = "★☆☆"
            color = COLORS['text_muted']

        clean_item = re.sub(r'[⭐]', '', item).strip()
        clean_item = re.sub(r'(高|中|低)\s*[-|]?\s*', '', clean_item)[:55]

        draw.text((opp_x + 25, opp_y), stars, font=font_small, fill=hex_to_rgb(color))
        draw.text((opp_x + 78, opp_y), clean_item, font=font_small, fill=hex_to_rgb(COLORS['text_light']))
        opp_y += 38

    y += card_height + 20

    # === TECHNOLOGY TRENDS ===
    trend_items = sections['trends'][:5]
    trend_height = max(80 + len(trend_items) * 32, 120)
    draw_rounded_rect(draw, (margin, y, width - margin, y + trend_height), radius=15,
                     fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(COLORS['card_border']), width=1)

    draw.text((margin + 20, y + 15), "💡", font=font_section, fill=hex_to_rgb(COLORS['accent_yellow']))
    draw.text((margin + 55, y + 15), "Technology Trends / 技术趋势", font=font_section, fill=hex_to_rgb(COLORS['text_white']))
    draw.rectangle([(margin + 20, y + 55), (width - margin - 20, y + 56)], fill=hex_to_rgb(COLORS['card_border']))

    trend_y = y + 70
    for item in trend_items:
        item_text = item[:95] + ('...' if len(item) > 95 else '')
        draw.text((margin + 25, trend_y), "→", font=font_body, fill=hex_to_rgb(COLORS['accent_yellow']))
        draw.text((margin + 50, trend_y), item_text, font=font_body, fill=hex_to_rgb(COLORS['text_light']))
        trend_y += 32

    y += trend_height + 20

    # === RECOMMENDED ACTIONS ===
    action_items = sections['actions'][:5]
    action_height = max(80 + len(action_items) * 35, 120)
    draw_rounded_rect(draw, (margin, y, width - margin, y + action_height), radius=15,
                     fill=hex_to_rgb(COLORS['card_bg']), outline=hex_to_rgb(COLORS['accent_purple']), width=2)

    draw.text((margin + 20, y + 15), "🎯", font=font_section, fill=hex_to_rgb(COLORS['accent_purple']))
    draw.text((margin + 55, y + 15), "Recommended Actions / 建议行动", font=font_section, fill=hex_to_rgb(COLORS['text_white']))
    draw.rectangle([(margin + 20, y + 55), (width - margin - 20, y + 56)], fill=hex_to_rgb(COLORS['card_border']))

    action_y = y + 70
    for i, item in enumerate(action_items):
        item_text = item[:90] + ('...' if len(item) > 90 else '')
        draw_rounded_rect(draw, (margin + 25, action_y, margin + 48, action_y + 22), radius=5, fill=hex_to_rgb(COLORS['accent_purple']))
        draw.text((margin + 32, action_y + 3), str(i + 1), font=font_small, fill=hex_to_rgb(COLORS['text_white']))
        draw.text((margin + 60, action_y + 2), item_text, font=font_body, fill=hex_to_rgb(COLORS['text_light']))
        action_y += 35

    y += action_height + 20

    # === FOOTER ===
    footer_y = min(y + 20, height - 55)
    draw.rectangle([(0, footer_y), (width, height)], fill=hex_to_rgb(COLORS['card_bg']))
    draw.rectangle([(0, footer_y), (width, footer_y + 3)], fill=hex_to_rgb(COLORS['accent_purple']))

    footer_text = "Auto-generated by AI News Bot  •  Lenovo Strategic Intelligence  •  Confidential"
    bbox = draw.textbbox((0, 0), footer_text, font=font_small)
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width) // 2, footer_y + 20), footer_text, font=font_small, fill=hex_to_rgb(COLORS['text_muted']))

    # Crop to actual content height
    final_height = min(footer_y + 55, height)
    img = img.crop((0, 0, width, final_height))

    img.save(output_path, 'PNG', quality=95)
    return output_path

if __name__ == "__main__":
    print("Image generator module loaded")
