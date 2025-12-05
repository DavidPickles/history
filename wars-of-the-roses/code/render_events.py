#!/usr/bin/env python3
"""
Render Wars of the Roses events from JSON to an HTML timeline visualization.
Reads JSON from stdin and outputs HTML to stdout.

Usage:
    cat wars_of_the_roses.json | python render_events.py [--type TYPE ...]

Options:
    --type TYPE    Filter by event type (battle, death, coronation, treaty)
                   Can be specified multiple times. If omitted, shows all events.
"""

import argparse
import json
import sys

def get_faction_color(allegiance: str) -> str:
    """Return color for each faction."""
    colors = {
        'york': '#FFFFFF',      # White rose
        'lancaster': '#DC143C', # Red rose
        'tudor': '#228B22',     # Green for Tudor
        'uncertain': '#808080'  # Gray for uncertain
    }
    return colors.get(allegiance, '#666666')

def get_rose_svg(allegiance: str, size: int = 20) -> str:
    """Return inline SVG rose for each faction."""
    if allegiance == 'york':
        # White rose of York
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="vertical-align: middle;">
            <defs>
                <radialGradient id="yorkCenter" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#FFD700"/>
                    <stop offset="100%" style="stop-color:#DAA520"/>
                </radialGradient>
            </defs>
            <g transform="translate(50,50)">
                <ellipse rx="22" ry="38" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(0)"/>
                <ellipse rx="22" ry="38" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(72)"/>
                <ellipse rx="22" ry="38" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(144)"/>
                <ellipse rx="22" ry="38" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(216)"/>
                <ellipse rx="22" ry="38" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(288)"/>
                <circle r="12" fill="url(#yorkCenter)"/>
            </g>
        </svg>'''
    elif allegiance == 'lancaster':
        # Red rose of Lancaster
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="vertical-align: middle;">
            <defs>
                <radialGradient id="lancasterCenter" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#FFD700"/>
                    <stop offset="100%" style="stop-color:#DAA520"/>
                </radialGradient>
            </defs>
            <g transform="translate(50,50)">
                <ellipse rx="22" ry="38" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(0)"/>
                <ellipse rx="22" ry="38" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(72)"/>
                <ellipse rx="22" ry="38" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(144)"/>
                <ellipse rx="22" ry="38" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(216)"/>
                <ellipse rx="22" ry="38" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(288)"/>
                <circle r="12" fill="url(#lancasterCenter)"/>
            </g>
        </svg>'''
    elif allegiance == 'tudor':
        # Tudor rose (combined red and white)
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="vertical-align: middle;">
            <defs>
                <radialGradient id="tudorCenter" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#FFD700"/>
                    <stop offset="100%" style="stop-color:#DAA520"/>
                </radialGradient>
            </defs>
            <g transform="translate(50,50)">
                <!-- Outer red petals -->
                <ellipse rx="22" ry="40" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(0)"/>
                <ellipse rx="22" ry="40" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(72)"/>
                <ellipse rx="22" ry="40" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(144)"/>
                <ellipse rx="22" ry="40" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(216)"/>
                <ellipse rx="22" ry="40" fill="#DC143C" stroke="#8B0000" stroke-width="1" transform="rotate(288)"/>
                <!-- Inner white petals -->
                <ellipse rx="14" ry="26" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(36)"/>
                <ellipse rx="14" ry="26" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(108)"/>
                <ellipse rx="14" ry="26" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(180)"/>
                <ellipse rx="14" ry="26" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(252)"/>
                <ellipse rx="14" ry="26" fill="#FFFFFF" stroke="#DDD" stroke-width="1" transform="rotate(324)"/>
                <circle r="10" fill="url(#tudorCenter)"/>
            </g>
        </svg>'''
    else:
        # Gray rose for uncertain allegiance
        return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="vertical-align: middle;">
            <defs>
                <radialGradient id="uncertainCenter" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#999"/>
                    <stop offset="100%" style="stop-color:#666"/>
                </radialGradient>
            </defs>
            <g transform="translate(50,50)">
                <ellipse rx="22" ry="38" fill="#808080" stroke="#666" stroke-width="1" transform="rotate(0)"/>
                <ellipse rx="22" ry="38" fill="#808080" stroke="#666" stroke-width="1" transform="rotate(72)"/>
                <ellipse rx="22" ry="38" fill="#808080" stroke="#666" stroke-width="1" transform="rotate(144)"/>
                <ellipse rx="22" ry="38" fill="#808080" stroke="#666" stroke-width="1" transform="rotate(216)"/>
                <ellipse rx="22" ry="38" fill="#808080" stroke="#666" stroke-width="1" transform="rotate(288)"/>
                <circle r="12" fill="url(#uncertainCenter)"/>
            </g>
        </svg>'''

def get_event_type_style(event_type: str) -> tuple[str, str]:
    """Return (background_color, text_color) for event type badges."""
    styles = {
        'battle': ('#8B0000', '#fff'),      # Dark red
        'death': ('#2c2c2c', '#fff'),        # Dark gray
        'coronation': ('#FFD700', '#000'),   # Gold
        'treaty': ('#4169E1', '#fff'),       # Royal blue
    }
    return styles.get(event_type, ('#666', '#fff'))

def generate_event_html(event: dict, factions: dict) -> str:
    """Generate HTML for a single event based on its type."""
    date = event['date']
    name = event['name']
    event_type = event['type']
    notes = event.get('notes', '')
    
    type_bg, type_fg = get_event_type_style(event_type)
    
    # Build type badge
    type_badge = f"""<span class="type-badge" style="background-color: {type_bg}; color: {type_fg}">{event_type.title()}</span>"""
    
    # Build details section based on event type
    if event_type == 'battle':
        victor = event['victor']
        victor_name = factions.get(victor, victor.title())
        victor_color = get_faction_color(victor)
        victor_rose = get_rose_svg(victor, 20)
        
        # Group commanders by allegiance
        commanders_by_side = {}
        for cmd in event['commanders']:
            allegiance = cmd['allegiance']
            if allegiance not in commanders_by_side:
                commanders_by_side[allegiance] = []
            cmd_text = cmd['name']
            if 'notes' in cmd:
                cmd_text += f" <span class='cmd-note'>({cmd['notes']})</span>"
            commanders_by_side[allegiance].append(cmd_text)
        
        commanders_html = ""
        for allegiance, cmds in commanders_by_side.items():
            faction_name = factions.get(allegiance, allegiance.title())
            rose_svg = get_rose_svg(allegiance, 24)
            commanders_html += f"""
                <div class="faction-group">
                    <span class="faction-badge">
                        {rose_svg}
                        {faction_name}
                    </span>
                    <ul class="commander-list">
                        {''.join(f'<li>{cmd}</li>' for cmd in cmds)}
                    </ul>
                </div>
            """
        
        victor_badge = f"""<span class="victor-badge">{victor_rose}<span class="victor-name"> {victor_name}</span></span>"""
        
        details_html = f"""
            <div class="commanders-section">
                <h3>Commanders</h3>
                {commanders_html}
            </div>
            <p class="battle-notes">{notes}</p>
        """
        border_color = victor_color
        
    elif event_type == 'death':
        person = event['person']
        location = event.get('location', 'Unknown')
        cause = event.get('cause', 'Unknown')
        
        victor_badge = ""
        details_html = f"""
            <div class="event-details-section">
                <p><strong>Person:</strong> {person}</p>
                <p><strong>Location:</strong> {location}</p>
                <p><strong>Cause:</strong> {cause}</p>
            </div>
            <p class="battle-notes">{notes}</p>
        """
        border_color = '#2c2c2c'
        
    elif event_type == 'coronation':
        monarch = event['monarch']
        location = event.get('location', 'Unknown')
        
        victor_badge = ""
        details_html = f"""
            <div class="event-details-section">
                <p><strong>Monarch:</strong> {monarch}</p>
                <p><strong>Location:</strong> {location}</p>
            </div>
            <p class="battle-notes">{notes}</p>
        """
        border_color = '#FFD700'
        
    elif event_type == 'treaty':
        parties = event.get('parties', [])
        
        victor_badge = ""
        details_html = f"""
            <div class="event-details-section">
                <p><strong>Parties:</strong> {', '.join(parties)}</p>
            </div>
            <p class="battle-notes">{notes}</p>
        """
        border_color = '#4169E1'
    
    else:
        victor_badge = ""
        details_html = f"<p class='battle-notes'>{notes}</p>"
        border_color = '#666'
    
    return f"""
    <div class="event-card" data-type="{event_type}" style="border-left-color: {border_color}">
        <div class="event-header" onclick="toggleEvent(this)">
            <div class="event-summary">
                <span class="event-date">{date}</span>
                <div class="type-victor-group">
                    {type_badge}
                    {victor_badge}
                </div>
                <span class="event-name">{name}</span>
            </div>
            <div class="expand-icon">&#9660;</div>
        </div>
        <div class="event-details">
            {details_html}
        </div>
    </div>
    """

def generate_html(data: dict, type_filter: list[str] = None) -> str:
    """Generate HTML visualization of the events."""
    
    events_html = ""
    
    for event in data['events']:
        # Apply type filter if specified
        if type_filter and event['type'] not in type_filter:
            continue
        events_html += generate_event_html(event, data['factions'])
    
    # Build filter description for subtitle
    if type_filter:
        filter_desc = ', '.join(t.title() + 's' for t in type_filter)
    else:
        filter_desc = 'All Events'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wars of the Roses - Timeline</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px 15px;
            }}
        }}
        
        header {{
            text-align: center;
            margin-bottom: 50px;
        }}

        @media (max-width: 768px) {{
            header {{
                margin-bottom: 30px;
            }}
        }}
        
        h1 {{
            font-size: 2.5rem;
            color: #fff;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8rem;
            }}
        }}

        .subtitle {{
            font-size: 1.2rem;
            color: #aaa;
        }}

        @media (max-width: 768px) {{
            .subtitle {{
                font-size: 1rem;
            }}
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 30px 0;
            flex-wrap: wrap;
        }}

        .legend-section {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }}

        .legend-title {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .legend-items {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
        }}

        .filter-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .filter-btn {{
            --btn-color: #555;
            --btn-text: #fff;
            background: transparent;
            border: 2px solid var(--btn-color);
            color: #aaa;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover {{
            background: var(--btn-color);
            color: var(--btn-text);
        }}

        .filter-btn.active {{
            background: var(--btn-color);
            color: var(--btn-text);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}

        @media (max-width: 768px) {{
            .timeline {{
                padding-left: 20px;
            }}
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, #DC143C, #FFFFFF, #228B22);
            border-radius: 3px;
        }}
        
        .event-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 4px solid;
            position: relative;
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
        }}

        .event-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .event-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 15px;
            cursor: pointer;
            user-select: none;
        }}

        .event-summary {{
            flex: 1;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        @media (max-width: 768px) {{
            .event-summary {{
                gap: 6px;
            }}
        }}

        .expand-icon {{
            font-size: 1rem;
            color: #888;
            transition: transform 0.3s ease;
            margin-left: 15px;
        }}

        .event-card.expanded .expand-icon {{
            transform: rotate(180deg);
        }}

        .event-details {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding: 0 15px;
        }}

        .event-card.expanded .event-details {{
            max-height: 1000px;
            padding: 0 15px 15px 15px;
        }}

        .event-card::before {{
            content: '';
            position: absolute;
            left: -38px;
            top: 15px;
            width: 10px;
            height: 10px;
            background: #fff;
            border-radius: 50%;
            border: 3px solid #1a1a2e;
        }}

        @media (max-width: 768px) {{
            .event-card::before {{
                left: -28px;
                width: 8px;
                height: 8px;
            }}
        }}

        .event-date {{
            font-size: 0.85rem;
            color: #888;
            font-family: monospace;
            min-width: 80px;
        }}

        @media (max-width: 768px) {{
            .event-date {{
                font-size: 0.75rem;
                min-width: 70px;
            }}
        }}

        .type-badge {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .event-name {{
            font-size: 1rem;
            color: #fff;
            font-weight: 500;
            flex: 1;
            min-width: 120px;
        }}

        @media (max-width: 768px) {{
            .event-name {{
                font-size: 0.9rem;
                min-width: 100px;
            }}
        }}
        
        .commanders-section {{
            margin-bottom: 15px;
        }}
        
        .commanders-section h3 {{
            font-size: 0.85rem;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        
        .faction-group {{
            margin-bottom: 10px;
        }}
        
        .faction-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px 3px 3px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-bottom: 5px;
            background: rgba(255,255,255,0.1);
        }}
        
        .commander-list {{
            list-style: none;
            padding-left: 15px;
        }}
        
        .commander-list li {{
            font-size: 0.95rem;
            padding: 2px 0;
            color: #ccc;
        }}
        
        .cmd-note {{
            font-size: 0.8rem;
            color: #f0ad4e;
            font-style: italic;
        }}

        .type-victor-group {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .victor-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px 3px 3px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.8rem;
            white-space: nowrap;
            background: rgba(255,255,255,0.1);
        }}

        @media (max-width: 768px) {{
            .victor-badge {{
                padding: 3px;
                gap: 0;
            }}

            .victor-badge .victor-name {{
                display: none;
            }}
        }}

        .event-details-section {{
            margin-bottom: 15px;
        }}

        .event-details-section p {{
            margin: 5px 0;
            color: #ccc;
        }}

        .event-details-section strong {{
            color: #aaa;
        }}
        
        .battle-notes {{
            font-style: italic;
            color: #aaa;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 15px;
            margin-top: 10px;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>&#9876;&#65039; Wars of the Roses</h1>
            <p class="subtitle">{data['period']} &bull; {filter_desc}</p>
            
            <div class="legend">
                <div class="legend-section">
                    <span class="legend-title">Factions</span>
                    <div class="legend-items">
                        <div class="legend-item">
                            {get_rose_svg('york', 28)}
                            <span>York</span>
                        </div>
                        <div class="legend-item">
                            {get_rose_svg('lancaster', 28)}
                            <span>Lancaster</span>
                        </div>
                        <div class="legend-item">
                            {get_rose_svg('tudor', 28)}
                            <span>Tudor</span>
                        </div>
                    </div>
                </div>
                <div class="legend-section">
                    <span class="legend-title">Filter by Event Type</span>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-type="all">All</button>
                        <button class="filter-btn" data-type="battle" style="--btn-color: #8B0000;">Battle</button>
                        <button class="filter-btn" data-type="coronation" style="--btn-color: #FFD700; --btn-text: #000;">Coronation</button>
                        <button class="filter-btn" data-type="death" style="--btn-color: #2c2c2c;">Death</button>
                        <button class="filter-btn" data-type="treaty" style="--btn-color: #4169E1;">Treaty</button>
                    </div>
                </div>
            </div>
        </header>

        <div class="timeline">
            {events_html}
        </div>
        
        <footer>
            <p>Wars of the Roses Timeline &bull; Data Visualization</p>
        </footer>
    </div>

    <script>
        function toggleEvent(headerElement) {{
            const card = headerElement.closest('.event-card');
            card.classList.toggle('expanded');
        }}

        // Filter functionality
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                // Update active state
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const filterType = btn.dataset.type;
                const cards = document.querySelectorAll('.event-card');

                cards.forEach(card => {{
                    if (filterType === 'all' || card.dataset.type === filterType) {{
                        card.style.display = '';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
"""
    return html

def main():
    parser = argparse.ArgumentParser(
        description='Render Wars of the Roses events to HTML timeline'
    )
    parser.add_argument(
        '--type', '-t',
        action='append',
        dest='types',
        choices=['battle', 'death', 'coronation', 'treaty'],
        help='Filter by event type (can be specified multiple times)'
    )
    args = parser.parse_args()

    # Read JSON data from stdin
    data = json.load(sys.stdin)

    # Generate HTML
    html_content = generate_html(data, args.types)

    # Write HTML to stdout
    sys.stdout.write(html_content)

if __name__ == '__main__':
    main()
