from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import sys
from dotenv import load_dotenv

load_dotenv()

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"],
        )
    )
)

github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a GitHub profile analyst and dev card generator.
When a user gives you a GitHub username, you ALWAYS follow this exact sequence:
1. First call 'scrape_github'.
2. Then call 'analyze_profile' with the result from step 1.
3. Then call 'generate_card_html' with the username, the result from step 1, and the result from step 2.
4. Then call 'save_card' with the username and the result from step 3.

Never skip steps. Be enthusiastic about developers' work.
If the profile is private or doesn't exist, say so clearly.
""",
    tools=[mcp_toolset],
)