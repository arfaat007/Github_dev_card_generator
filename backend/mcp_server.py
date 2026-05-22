import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
from collections import Counter

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

mcp = FastMCP("GitHub Dev Card Generator")

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetch GitHub profile data and top repositories for a given username."""
    headers = {}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    async with httpx.AsyncClient(headers=headers) as client:
        # Fetch user profile
        user_res = await client.get(f"https://api.github.com/users/{username}")
        if user_res.status_code != 200:
            return {"error": f"User not found or API error: {user_res.status_code}"}
        
        user_data = user_res.json()
        
        # Fetch repositories
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100")
        repos = repos_res.json() if repos_res.status_code == 200 else []
        
        # Process top 6 repos by stars
        sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
        top_6 = []
        languages = []
        
        for r in sorted_repos[:6]:
            top_6.append({
                "name": r.get("name"),
                "stars": r.get("stargazers_count"),
                "language": r.get("language"),
                "description": r.get("description")
            })
            if r.get("language"):
                languages.append(r.get("language"))
        
        # Aggregate languages
        lang_counts = Counter(languages)
        most_used_langs = [lang for lang, count in lang_counts.most_common(5)]

        return {
            "name": user_data.get("name") or username,
            "avatar_url": user_data.get("avatar_url"),
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_repos": top_6,
            "languages": most_used_langs
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Analyze GitHub data using Gemini to generate a developer persona."""
    prompt = f"""
    Analyze this GitHub profile data and return a JSON object with:
    - developer_vibe: A 1-sentence personality description.
    - top_skills: A list of the top 3 technical skills.
    - fun_fact: A clever observation inferred from their repositories.
    - card_theme: One of ["hacker", "builder", "researcher", "designer", "open-source-hero"].

    Data: {json.dumps(github_data)}
    
    Respond ONLY with the JSON object.
    """
    
    response = model.generate_content(prompt)
    try:
        # Simple extraction if Gemini wraps it in code blocks
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text)
    except Exception:
        return {
            "developer_vibe": "A dedicated coder making waves on GitHub.",
            "top_skills": github_data.get("languages", ["Coding"])[:3],
            "fun_fact": "They have a knack for building interesting projects.",
            "card_theme": "builder"
        }

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generate a self-contained beautiful HTML card."""
    theme = analysis.get("card_theme", "builder")
    
    # Simple theme mapping
    themes = {
        "hacker": {"bg": "#0a0a0a", "text": "#00ff41", "accent": "#00ff41", "card": "#1a1a1a"},
        "builder": {"bg": "#f4f7f6", "text": "#2c3e50", "accent": "#3498db", "card": "#ffffff"},
        "researcher": {"bg": "#eef2f3", "text": "#2c3e50", "accent": "#8e44ad", "card": "#ffffff"},
        "designer": {"bg": "#fff5f5", "text": "#4a4a4a", "accent": "#ff6b6b", "card": "#ffffff"},
        "open-source-hero": {"bg": "#f0fff4", "text": "#2d3748", "accent": "#48bb78", "card": "#ffffff"}
    }
    
    t = themes.get(theme, themes["builder"])
    
    skills_badges = "".join([f'<span class="badge" style="background:{t["accent"]}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px;">{s}</span>' for s in analysis.get("top_skills", [])])
    
    repos_html = "".join([f'<li><strong>{r["name"]}</strong> (⭐{r["stars"]}) - {r["language"] or "Mixed"}</li>' for r in github_data.get("top_repos", [])[:3]])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: {t["bg"]}; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: {t["card"]}; color: {t["text"]}; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 400px; padding: 25px; border: 1px solid {t["accent"]}22; }}
            .header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }}
            .avatar {{ width: 80px; height: 80px; border-radius: 50%; border: 3px solid {t["accent"]}; }}
            .vibe {{ font-style: italic; margin-bottom: 15px; color: {t["text"]}aa; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 20px; border-top: 1px solid {t["text"]}22; border-bottom: 1px solid {t["text"]}22; padding: 10px 0; }}
            .repos-list {{ list-style: none; padding: 0; font-size: 14px; }}
            .repos-list li {{ margin-bottom: 8px; }}
            .fun-fact {{ font-size: 12px; margin-top: 20px; color: {t["text"]}88; border-left: 3px solid {t["accent"]}; padding-left: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <img src="{github_data["avatar_url"]}" class="avatar">
                <div>
                    <h2 style="margin:0;">{github_data["name"]}</h2>
                    <div style="margin-top:5px;">{skills_badges}</div>
                </div>
            </div>
            <div class="vibe">"{analysis["developer_vibe"]}"</div>
            <div class="stats">
                <div><strong>{github_data["public_repos"]}</strong><br><small>Repos</small></div>
                <div><strong>{github_data["followers"]}</strong><br><small>Followers</small></div>
            </div>
            <h3>Top Projects</h3>
            <ul class="repos-list">
                {repos_html}
            </ul>
            <div class="fun-fact"><strong>Did you know?</strong> {analysis["fun_fact"]}</div>
        </div>
    </body>
    </html>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Save the generated HTML card to a static file."""
    # Resolve project root and write to the correct static/cards directory
    output_dir = Path(__file__).resolve().parents[2] / "static" / "cards"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{username}.html"
    file_path.write_text(html, encoding="utf-8")
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
