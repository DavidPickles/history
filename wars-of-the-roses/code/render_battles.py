#!/usr/bin/env python3
"""
Render Wars of the Roses battles from JSON to an HTML timeline visualization.
Reads JSON from stdin and outputs HTML to stdout.
"""

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

def get_faction_bg(allegiance: str) -> str:
    """Return background color for each faction."""
    colors = {
        'york': '#1a1a2e',
        'lancaster': '#2d1f1f',
        'tudor': '#1f2d1f',
        'uncertain': '#2a2a2a'
    }
    return colors.get(allegiance, '#1a1a1a')

def generate_html(data: dict) -> str:
    """Generate HTML visualization of the battles."""
    
    battles_html = ""
    
    for battle in data['events']:
        date = battle['date']
        name = battle['name']
        victor = battle['victor']
        notes = battle.get('notes', '')
        
        # Group commanders by allegiance
        commanders_by_side = {}
        for cmd in battle['commanders']:
            allegiance = cmd['allegiance']
            if allegiance not in commanders_by_side:
                commanders_by_side[allegiance] = []
            
            cmd_text = cmd['name']
            if 'notes' in cmd:
                cmd_text += f" <span class='cmd-note'>({cmd['notes']})</span>"
            commanders_by_side[allegiance].append(cmd_text)
        
        # Build commanders HTML
        commanders_html = ""
        for allegiance, cmds in commanders_by_side.items():
            faction_name = data['factions'].get(allegiance, allegiance.title())
            color = get_faction_color(allegiance)
            commanders_html += f"""
                <div class="faction-group">
                    <span class="faction-badge" style="background-color: {color}; color: {'#000' if allegiance == 'york' else '#fff'}">
                        {faction_name}
                    </span>
                    <ul class="commander-list">
                        {''.join(f'<li>{cmd}</li>' for cmd in cmds)}
                    </ul>
                </div>
            """
        
        victor_name = data['factions'].get(victor, victor.title())
        victor_color = get_faction_color(victor)
        
        battles_html += f"""
        <div class="battle-card" style="border-left-color: {victor_color}">
            <div class="battle-header" onclick="toggleBattle(this)">
                <div class="battle-summary">
                    <span class="battle-date">{date}</span>
                    <span class="battle-name">{name}</span>
                    <span class="victor-badge" style="background-color: {victor_color}; color: {'#000' if victor == 'york' else '#fff'}">
                        {victor_name}
                    </span>
                </div>
                <div class="expand-icon">▼</div>
            </div>
            <div class="battle-details">
                <div class="commanders-section">
                    <h3>Commanders</h3>
                    {commanders_html}
                </div>
                <p class="battle-notes">{notes}</p>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wars of the Roses - Battle Timeline</title>
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
            gap: 30px;
            margin: 30px 0;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid #444;
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
        
        .battle-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 4px solid;
            position: relative;
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
        }}

        .battle-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .battle-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 15px;
            cursor: pointer;
            user-select: none;
        }}

        .battle-summary {{
            flex: 1;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}

        @media (max-width: 768px) {{
            .battle-summary {{
                gap: 8px;
            }}
        }}

        .expand-icon {{
            font-size: 1rem;
            color: #888;
            transition: transform 0.3s ease;
            margin-left: 15px;
        }}

        .battle-card.expanded .expand-icon {{
            transform: rotate(180deg);
        }}

        .battle-details {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding: 0 15px;
        }}

        .battle-card.expanded .battle-details {{
            max-height: 1000px;
            padding: 0 15px 15px 15px;
        }}

        .battle-card::before {{
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
            .battle-card::before {{
                left: -28px;
                width: 8px;
                height: 8px;
            }}
        }}

        .battle-date {{
            font-size: 0.85rem;
            color: #888;
            font-family: monospace;
            min-width: 80px;
        }}

        @media (max-width: 768px) {{
            .battle-date {{
                font-size: 0.75rem;
                min-width: 70px;
            }}
        }}

        .battle-name {{
            font-size: 1rem;
            color: #fff;
            font-weight: 500;
            flex: 1;
            min-width: 150px;
        }}

        @media (max-width: 768px) {{
            .battle-name {{
                font-size: 0.9rem;
                min-width: 120px;
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
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-bottom: 5px;
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
        
        .outcome {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .victor-label {{
            font-weight: bold;
            color: #888;
        }}

        .victor-badge {{
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.8rem;
            white-space: nowrap;
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
            <h1>⚔️ Wars of the Roses</h1>
            <p class="subtitle">{data['period']} • Battle Timeline</p>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #FFFFFF;"></div>
                    <span>York</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #DC143C;"></div>
                    <span>Lancaster</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: #228B22;"></div>
                    <span>Tudor</span>
                </div>
            </div>
        </header>

        <div class="timeline">
            {battles_html}
        </div>
        
        <footer>
            <p>Wars of the Roses Battle Timeline • Data Visualization</p>
        </footer>
    </div>

    <script>
        function toggleBattle(headerElement) {{
            const card = headerElement.closest('.battle-card');
            card.classList.toggle('expanded');
        }}
    </script>
</body>
</html>
"""
    return html

def main():
    # Read JSON data from stdin
    data = json.load(sys.stdin)

    # Generate HTML
    html_content = generate_html(data)

    # Write HTML to stdout
    sys.stdout.write(html_content)

if __name__ == '__main__':
    main()
