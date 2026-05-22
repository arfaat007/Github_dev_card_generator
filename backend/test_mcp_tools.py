import asyncio
import os
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card
from dotenv import load_dotenv

async def test_workflow():
    load_dotenv()
    username = "torvalds"
    print(f"--- Testing workflow for: {username} ---")

    try:
        # 1. Scrape GitHub
        print("Step 1: Scraping GitHub...")
        github_data = await scrape_github(username)
        if "error" in github_data:
            print(f"FAILED: scrape_github error: {github_data['error']}")
            return
        print("Success: Scraped data for", github_data['name'])

        # 2. Analyze Profile
        print("Step 2: Analyzing profile with Gemini...")
        analysis = await analyze_profile(github_data)
        print("Success: Analysis complete")

        # 3. Generate HTML Card
        print("Step 3: Generating HTML card...")
        html = await generate_card_html(username, github_data, analysis)
        print("Success: HTML card generated (Length:", len(html), ")")

        # 4. Save Card
        print("Step 4: Saving card...")
        path = await save_card(username, html)
        print(f"Success: Card saved to {path}")

        # Final Output
        print("\n--- TEST RESULTS ---")
        print(f"Developer Vibe: {analysis.get('developer_vibe')}")
        print(f"Card Theme: {analysis.get('card_theme')}")

    except Exception as e:
        print(f"\nCRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow())
