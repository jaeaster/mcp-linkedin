# MCP LinkedIn

A Model Context Protocol (MCP) server that provides tools to interact with LinkedIn for lead generation, sales prospecting, and networking.

This is using unofficial LinkedIn API via [Linkedin-api](https://github.com/tomquirk/linkedin-api). Use at your own risk.

<a href="https://smithery.ai/server/mcp-linkedin"><img alt="Smithery Badge" src="https://smithery.ai/badge/mcp-linkedin"></a>
<a href="https://glama.ai/mcp/servers/dvbdubl2bg"><img width="380" height="200" src="https://glama.ai/mcp/servers/dvbdubl2bg/badge" alt="mcp-linkedin MCP server" /></a>

## Overview

This MCP server provides a comprehensive set of tools for LLMs to interact with LinkedIn for various business development activities, including:

1. Finding and qualifying sales leads
2. Researching companies and industries
3. Identifying decision makers
4. Generating personalized outreach content
5. Monitoring job changes and company updates

## Installing via Smithery

To install LinkedIn Interaction Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-linkedin):

```bash
npx -y @smithery/cli install mcp-linkedin --client claude
```

## Configuration

```json
{
    "mcpServers": {
        "linkedin": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/adhikasp/mcp-linkedin", "mcp-linkedin"],
            "env": {
                "LINKEDIN_EMAIL": "your_linkedin_email",
                "LINKEDIN_PASSWORD": "your_linkedin_password"
            }
        }
    }
}
```

## Available Tools

### Feed and Job Search

1. `get_feed_posts` - Retrieve LinkedIn feed posts
2. `search_jobs` - Search for jobs on LinkedIn based on keywords and location

### Company Research

3. `search_companies` - Search for companies based on keywords, industry, and location
4. `get_company_details` - Get detailed information about a specific company
5. `get_company_updates` - Get recent updates and posts from a company
6. `find_companies_using_technologies` - Find companies that are using specific technologies

### People Research

7. `search_people` - Search for people based on various criteria (title, company, industry, etc.)
8. `get_profile_details` - Get detailed information about a specific LinkedIn profile
9. `search_company_employees` - Find employees at a specific company
10. `search_people_by_skills` - Find people who have specific skills
11. `find_common_connections` - Find common connections or similarities between two profiles
12. `find_recent_job_changes` - Find people who have recently changed jobs

### Lead Generation

13. `find_decision_makers` - Find decision makers at a specific company
14. `generate_lead_recommendations` - Generate lead recommendations for IT services sales
15. `identify_target_accounts` - Identify target accounts based on specific criteria
16. `analyze_prospect_profile` - Analyze a prospect's profile for sales opportunities
17. `generate_sales_outreach_context` - Generate personalized context for sales outreach

## Sample Usage

Using [mcp-client-cli](https://github.com/adhikasp/mcp-client-cli) or directly with Claude:

### Find Companies in a Specific Industry

```
I need to find software companies in San Francisco that might need cybersecurity services.

Tool Calls:
  search_companies
  Args:
    keywords: software
    industry: Information Technology
    location: San Francisco
    limit: 5
```

### Identify Decision Makers at a Company

```
I found a potential client company with ID "123456". Can you find the key decision makers there?

Tool Calls:
  find_decision_makers
  Args:
    company_id: 123456
    titles: ["CTO", "CISO", "Head of IT", "VP of Engineering"]
    limit: 3
```

### Generate Personalized Outreach

```
I need to send a personalized email to this prospect with profile ID "john-doe-123". We offer cloud migration services.

Tool Calls:
  generate_sales_outreach_context
  Args:
    profile_id: john-doe-123
    company_service: cloud migration services
```

### Find Companies Using Specific Technologies

```
I want to find companies that are using legacy banking systems that might need modernization.

Tool Calls:
  find_companies_using_technologies
  Args:
    technologies: ["COBOL", "mainframe", "legacy systems", "core banking"]
    industry: Banking
    limit: 5
```

### Research a Prospect's Background

```
I have a meeting with this prospect tomorrow. Can you analyze their profile to help me prepare?

Tool Calls:
  analyze_prospect_profile
  Args:
    profile_id: jane-smith-456
    service_keywords: ["digital transformation", "IT consulting", "ERP implementation"]
```

## Integration with LLM Applications

This MCP server is designed to provide LinkedIn data and insights to LLM applications to enhance their capabilities for sales, prospecting, and business development tasks. By connecting this MCP to an LLM, the AI can:

1. Research and qualify potential sales leads
2. Generate personalized outreach content
3. Prepare for sales meetings with prospect research
4. Monitor industry trends and competition
5. Find and analyze target accounts

## Development

### Prerequisites

- Python 3.7+
- LinkedIn account credentials

### Setup

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Set environment variables:
   - LINKEDIN_EMAIL
   - LINKEDIN_PASSWORD
4. Run the server: `python -m mcp_linkedin.client`

### Adding New Tools

You can extend the functionality by adding new tools to `src/mcp_linkedin/client.py`.

## Disclaimer

This project uses an unofficial LinkedIn API. Use at your own risk and ensure compliance with LinkedIn's terms of service. This tool is intended for legitimate business development activities and not for scraping or mass data collection.
