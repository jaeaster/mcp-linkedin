from linkedin_api import Linkedin
from fastmcp import FastMCP
import os
import logging
import json
from typing import List, Optional, Dict, Any, Union

mcp = FastMCP("mcp-linkedin")
logger = logging.getLogger(__name__)

def get_client():
    return Linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD"), debug=True)

@mcp.tool()
def get_feed_posts(limit: int = 10, offset: int = 0) -> str:
    """
    Retrieve LinkedIn feed posts.

    :return: List of feed post details
    """
    client = get_client()
    try:
        post_urns = client.get_feed_posts(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error: {e}"

    posts = ""
    for urn in post_urns:
        posts += f"Post by {urn['author_name']}: {urn['content']}\n"

    return posts

@mcp.tool()
def search_jobs(keywords: str, limit: int = 3, offset: int = 0, location: str = '') -> str:
    """
    Search for jobs on LinkedIn.

    :param keywords: Job search keywords
    :param limit: Maximum number of job results
    :param location: Optional location filter
    :return: List of job details
    """
    client = get_client()
    jobs = client.search_jobs(
        keywords=keywords,
        location_name=location,
        limit=limit,
        offset=offset,
    )
    job_results = ""
    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        job_data = client.get_job(job_id=job_id)

        job_title = job_data["title"]
        company_name = job_data["companyDetails"]["com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"]["companyResolutionResult"]["name"]
        job_description = job_data["description"]["text"]
        job_location = job_data["formattedLocation"]

        job_results += f"Job by {job_title} at {company_name} in {job_location}: {job_description}\n\n"

    return job_results


@mcp.tool()
def search_companies(keywords: str, industry: str = None, location: str = None, limit: int = 10) -> str:
    """
    Search for companies on LinkedIn based on keywords, industry, and location.

    :param keywords: Company name or keywords
    :param industry: Industry filter (e.g., "Information Technology", "Financial Services")
    :param location: Location filter (e.g., "United States", "London")
    :param limit: Maximum number of company results
    :return: List of company details
    """
    client = get_client()
    try:
        # Build search filters
        search_params = {
            "keywords": keywords,
        }

        # Add optional filters
        if industry:
            search_params["industry"] = industry

        if location:
            search_params["location"] = location

        # Execute search
        companies = client.search_companies(
            **search_params,
            limit=limit
        )

        # Format results
        results = []
        for company in companies:
            company_id = company.get("entityUrn", "").split(":")[-1]
            company_name = company.get("name", "Unknown")
            company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"
            company_location = company.get("headquarter", {}).get("country", "Unknown") if company.get("headquarter") else "Unknown"
            company_description = company.get("description", "No description available")
            company_size = company.get("staffCount", "Unknown")
            company_url = f"https://www.linkedin.com/company/{company_id}"

            results.append({
                "id": company_id,
                "name": company_name,
                "industry": company_industry,
                "location": company_location,
                "description": company_description,
                "size": company_size,
                "url": company_url
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        return f"Error searching companies: {e}"

@mcp.tool()
def get_company_details(company_id: str) -> str:
    """
    Get detailed information about a specific company.

    :param company_id: LinkedIn company ID
    :return: Detailed company information
    """
    client = get_client()
    try:
        company = client.get_company(company_id)

        # Extract key information
        company_name = company.get("name", "Unknown")
        company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"
        company_description = company.get("description", "No description available")
        company_website = company.get("websiteUrl", "Unknown")
        company_headquarter = company.get("headquarter", {})
        company_location = f"{company_headquarter.get('city', '')}, {company_headquarter.get('country', '')}" if company_headquarter else "Unknown"
        company_size = company.get("staffCount", "Unknown")
        company_specialties = company.get("specialities", [])
        company_founded = company.get("founded", "Unknown")

        company_details = {
            "id": company_id,
            "name": company_name,
            "industry": company_industry,
            "description": company_description,
            "website": company_website,
            "location": company_location,
            "size": company_size,
            "specialties": company_specialties,
            "founded": company_founded,
        }

        return json.dumps(company_details, indent=2)

    except Exception as e:
        logger.error(f"Error getting company details: {e}")
        return f"Error getting company details: {e}"


@mcp.tool()
def search_people(keywords: str = None, title: str = None, company: str = None,
                 industry: str = None, location: str = None,
                 school: str = None, skill: str = None, limit: int = 10) -> str:
    """
    Search for people on LinkedIn based on various criteria.

    :param keywords: General search keywords
    :param title: Job title filter (e.g., "CTO", "Software Engineer")
    :param company: Company name filter
    :param industry: Industry filter
    :param location: Location filter
    :param school: Education institution filter
    :param skill: Specific skill to search for
    :param limit: Maximum number of results
    :return: List of profile details
    """
    client = get_client()
    try:
        # Build search parameters
        search_params = {}

        # Add parameters that are provided
        if keywords:
            search_params["keywords"] = keywords
        if title:
            search_params["title"] = title
        if company:
            search_params["company_name"] = company
        if school:
            search_params["school_name"] = school
        if industry:
            search_params["industry"] = industry
        if location:
            search_params["location_name"] = location

        # Execute search
        people = client.search_people(
            **search_params,
            limit=limit
        )

        # Filter by skill if provided
        if skill and people:
            filtered_people = []
            for person in people:
                profile_id = person.get("public_id", "")
                profile_skills = client.get_profile_skills(profile_id)

                if any(skill.lower() in s.get("name", "").lower() for s in profile_skills):
                    filtered_people.append(person)

            people = filtered_people[:limit]

        # Format results
        results = []
        for person in people:
            profile_id = person.get("public_id", "")
            profile_urn = person.get("urn_id", "")
            profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
            profile_title = person.get("occupation", "")
            profile_location = person.get("locationName", "")
            profile_url = f"https://www.linkedin.com/in/{profile_id}"

            # Get current company
            current_company = ""
            if person.get("experience") and len(person.get("experience")) > 0:
                current_company = person.get("experience")[0].get("companyName", "")

            results.append({
                "id": profile_id,
                "name": profile_name,
                "title": profile_title,
                "company": current_company,
                "location": profile_location,
                "url": profile_url
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error searching people: {e}")
        return f"Error searching people: {e}"

@mcp.tool()
def get_profile_details(profile_id: str) -> str:
    """
    Get detailed information about a specific LinkedIn profile.

    :param profile_id: LinkedIn profile ID/public_id
    :return: Detailed profile information
    """
    client = get_client()
    try:
        profile = client.get_profile(profile_id)
        skills = client.get_profile_skills(profile_id)

        # Extract key information
        full_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        headline = profile.get("headline", "")
        location = profile.get("locationName", "")
        industry = profile.get("industryName", "")

        # Experience
        experience = []
        for exp in profile.get("experience", []):
            experience.append({
                "company": exp.get("companyName", ""),
                "title": exp.get("title", ""),
                "description": exp.get("description", ""),
                "date_range": f"{exp.get('timePeriod', {}).get('startDate', {}).get('year', '')} - {exp.get('timePeriod', {}).get('endDate', {}).get('year', 'Present')}"
            })

        # Education
        education = []
        for edu in profile.get("education", []):
            education.append({
                "school": edu.get("schoolName", ""),
                "degree": edu.get("degreeName", ""),
                "field": edu.get("fieldOfStudy", ""),
                "date_range": f"{edu.get('timePeriod', {}).get('startDate', {}).get('year', '')} - {edu.get('timePeriod', {}).get('endDate', {}).get('year', '')}"
            })

        # Skills
        skill_list = [skill.get("name", "") for skill in skills]

        # Format results
        profile_details = {
            "id": profile_id,
            "name": full_name,
            "headline": headline,
            "location": location,
            "industry": industry,
            "experience": experience,
            "education": education,
            "skills": skill_list,
            "url": f"https://www.linkedin.com/in/{profile_id}"
        }

        return json.dumps(profile_details, indent=2)

    except Exception as e:
        logger.error(f"Error getting profile details: {e}")
        return f"Error getting profile details: {e}"


@mcp.tool()
def search_company_employees(company_id: str, title: str = None, limit: int = 10) -> str:
    """
    Search for employees at a specific company, optionally filtered by job title.

    :param company_id: LinkedIn company ID
    :param title: Job title filter (e.g., "CTO", "Software Engineer")
    :param limit: Maximum number of results
    :return: List of employee profiles
    """
    client = get_client()
    try:
        # Get company name first
        company = client.get_company(company_id)
        company_name = company.get("name", "")

        if not company_name:
            return "Error: Could not find company name"

        # Search for people at the company
        search_params = {
            "company_name": company_name
        }

        # Add title filter if provided
        if title:
            search_params["title"] = title

        # Execute search
        employees = client.search_people(
            **search_params,
            limit=limit
        )

        # Format results
        results = []
        for person in employees:
            profile_id = person.get("public_id", "")
            profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
            profile_title = person.get("occupation", "")
            profile_location = person.get("locationName", "")
            profile_url = f"https://www.linkedin.com/in/{profile_id}"

            results.append({
                "id": profile_id,
                "name": profile_name,
                "title": profile_title,
                "company": company_name,
                "location": profile_location,
                "url": profile_url
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error searching company employees: {e}")
        return f"Error searching company employees: {e}"

@mcp.tool()
def search_people_by_skills(skills: List[str], title: str = None, industry: str = None,
                           location: str = None, limit: int = 10) -> str:
    """
    Search for people on LinkedIn who have specific skills.

    :param skills: List of skills to search for
    :param title: Optional job title filter
    :param industry: Optional industry filter
    :param location: Optional location filter
    :param limit: Maximum number of results
    :return: List of profiles with the specified skills
    """
    client = get_client()
    try:
        # Build search parameters
        search_params = {}

        # Add parameters that are provided
        if title:
            search_params["title"] = title
        if industry:
            search_params["industry"] = industry
        if location:
            search_params["location_name"] = location

        # Use the first skill as a keyword
        if skills and len(skills) > 0:
            search_params["keywords"] = skills[0]

        # Execute search
        people = client.search_people(
            **search_params,
            limit=limit * 2  # Search for more to filter later
        )

        # Filter by all skills
        filtered_people = []
        for person in people:
            profile_id = person.get("public_id", "")
            profile_skills = client.get_profile_skills(profile_id)
            profile_skill_names = [s.get("name", "").lower() for s in profile_skills]

            # Check if the person has all the required skills
            has_all_skills = all(any(skill.lower() in skill_name for skill_name in profile_skill_names) for skill in skills)

            if has_all_skills:
                filtered_people.append(person)

                # Break if we have enough results
                if len(filtered_people) >= limit:
                    break

        # Format results
        results = []
        for person in filtered_people[:limit]:
            profile_id = person.get("public_id", "")
            profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
            profile_title = person.get("occupation", "")
            profile_location = person.get("locationName", "")
            profile_url = f"https://www.linkedin.com/in/{profile_id}"

            # Get current company
            current_company = ""
            if person.get("experience") and len(person.get("experience")) > 0:
                current_company = person.get("experience")[0].get("companyName", "")

            # Get matched skills
            person_skills = client.get_profile_skills(profile_id)
            matched_skills = []
            for person_skill in person_skills:
                skill_name = person_skill.get("name", "")
                if any(s.lower() in skill_name.lower() for s in skills):
                    matched_skills.append(skill_name)

            results.append({
                "id": profile_id,
                "name": profile_name,
                "title": profile_title,
                "company": current_company,
                "location": profile_location,
                "matched_skills": matched_skills,
                "url": profile_url
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error searching people by skills: {e}")
        return f"Error searching people by skills: {e}"


@mcp.tool()
def get_company_updates(company_id: str, limit: int = 5) -> str:
    """
    Get recent updates and posts from a company.

    :param company_id: LinkedIn company ID
    :param limit: Maximum number of updates to retrieve
    :return: List of company updates
    """
    client = get_client()
    try:
        # Get company updates
        updates = client.get_company_updates(company_id, limit=limit)

        # Format results
        results = []
        for update in updates:
            update_text = update.get("value", {}).get("com.linkedin.voyager.feed.render.UpdateV2", {}).get("commentary", {}).get("text", "No content")

            # Get timestamp if available
            timestamp = None
            actor = update.get("value", {}).get("com.linkedin.voyager.feed.render.UpdateV2", {}).get("actor", {})
            if actor:
                timestamp = actor.get("subDescription", {}).get("text", "")

            results.append({
                "content": update_text,
                "timestamp": timestamp
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error getting company updates: {e}")
        return f"Error getting company updates: {e}"

@mcp.tool()
def find_decision_makers(company_id: str, titles: List[str] = None, limit: int = 5) -> str:
    """
    Find decision makers at a specific company based on their job titles.

    :param company_id: LinkedIn company ID
    :param titles: List of job titles to search for (e.g., ["CTO", "Director", "VP"])
    :param limit: Maximum number of results
    :return: List of decision maker profiles
    """
    client = get_client()
    try:
        # Default titles if none provided
        if not titles:
            titles = ["CEO", "CTO", "CIO", "Director", "VP", "Head", "Manager"]

        # Get company name first
        company = client.get_company(company_id)
        company_name = company.get("name", "")

        if not company_name:
            return "Error: Could not find company name"

        # Search for decision makers
        decision_makers = []

        for title in titles:
            # Search for people with this title at the company
            search_params = {
                "company_name": company_name,
                "title": title
            }

            # Execute search
            people = client.search_people(
                **search_params,
                limit=limit // len(titles) + 1  # Distribute limit across titles
            )

            # Add to results
            decision_makers.extend(people)

            # Break if we have enough results
            if len(decision_makers) >= limit:
                break

        # Format results
        results = []
        for person in decision_makers[:limit]:
            profile_id = person.get("public_id", "")
            profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
            profile_title = person.get("occupation", "")
            profile_location = person.get("locationName", "")
            profile_url = f"https://www.linkedin.com/in/{profile_id}"

            results.append({
                "id": profile_id,
                "name": profile_name,
                "title": profile_title,
                "company": company_name,
                "location": profile_location,
                "url": profile_url
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error finding decision makers: {e}")
        return f"Error finding decision makers: {e}"


@mcp.tool()
def generate_lead_recommendations(industry: str = None, company_size: str = None,
                                technologies: List[str] = None, location: str = None,
                                limit: int = 5) -> str:
    """
    Generate lead recommendations for IT services sales based on various criteria.

    :param industry: Target industry
    :param company_size: Target company size
    :param technologies: List of technologies the company might be using
    :param location: Target location
    :param limit: Maximum number of recommendations
    :return: List of recommended leads with decision makers
    """
    client = get_client()
    try:
        # Default values
        if not industry:
            industry = "Information Technology"

        # Search for companies first
        search_params = {}

        if industry:
            search_params["keywords"] = industry

        if location:
            search_params["location"] = location

        # Execute search
        companies = client.search_companies(
            **search_params,
            limit=limit * 2  # Search for more to filter later
        )

        # Filter companies by size if needed
        filtered_companies = companies
        if company_size:
            size_ranges = {
                "small": (1, 50),
                "medium": (51, 500),
                "large": (501, float('inf'))
            }

            range_min, range_max = size_ranges.get(company_size.lower(), (0, float('inf')))

            filtered_companies = []
            for company in companies:
                staff_count = company.get("staffCount", 0)
                if range_min <= staff_count <= range_max:
                    filtered_companies.append(company)

        # Generate recommendations
        recommendations = []
        for company in filtered_companies[:limit]:
            company_id = company.get("entityUrn", "").split(":")[-1]
            company_name = company.get("name", "Unknown")
            company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"
            company_location = company.get("headquarter", {}).get("country", "Unknown") if company.get("headquarter") else "Unknown"
            company_size = company.get("staffCount", "Unknown")

            # Find decision makers
            decision_makers = []
            try:
                # Default titles for IT services sales
                titles = ["CTO", "CIO", "IT Director", "VP of Technology", "Head of IT"]

                # Get decision makers
                for title in titles[:2]:  # Limit to two titles to avoid too many API calls
                    search_params = {
                        "company_name": company_name,
                        "title": title
                    }

                    # Execute search
                    people = client.search_people(
                        **search_params,
                        limit=2  # Just get a couple per title
                    )

                    # Add to results
                    for person in people:
                        profile_id = person.get("public_id", "")
                        profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
                        profile_title = person.get("occupation", "")
                        profile_url = f"https://www.linkedin.com/in/{profile_id}"

                        decision_makers.append({
                            "name": profile_name,
                            "title": profile_title,
                            "url": profile_url
                        })

                        # Break if we have enough decision makers
                        if len(decision_makers) >= 2:
                            break

            except Exception as e:
                logger.warning(f"Error finding decision makers for {company_name}: {e}")

            # Generate technology fit if technologies are provided
            technology_fit = "Unknown"
            if technologies:
                # Search for company updates or job postings mentioning the technologies
                try:
                    # Get company updates
                    updates = client.get_company_updates(company_id, limit=5)

                    # Check if any updates mention the technologies
                    mentions = []
                    for update in updates:
                        update_text = update.get("value", {}).get("com.linkedin.voyager.feed.render.UpdateV2", {}).get("commentary", {}).get("text", "")

                        for tech in technologies:
                            if tech.lower() in update_text.lower():
                                mentions.append(tech)

                    if mentions:
                        technology_fit = "High - Mentioned in company updates: " + ", ".join(mentions)
                    else:
                        # Check job postings
                        jobs = client.search_jobs(
                            keywords=" ".join(technologies),
                            company_name=company_name,
                            limit=5
                        )

                        if jobs:
                            technology_fit = "Medium - Company has job postings with relevant technologies"
                        else:
                            technology_fit = "Low - No direct mentions found"

                except Exception as e:
                    logger.warning(f"Error checking technology fit for {company_name}: {e}")

            recommendations.append({
                "company_id": company_id,
                "company_name": company_name,
                "industry": company_industry,
                "location": company_location,
                "size": company_size,
                "technology_fit": technology_fit,
                "decision_makers": decision_makers,
                "company_url": f"https://www.linkedin.com/company/{company_id}"
            })

        return json.dumps(recommendations, indent=2)

    except Exception as e:
        logger.error(f"Error generating lead recommendations: {e}")
        return f"Error generating lead recommendations: {e}"


@mcp.tool()
def identify_target_accounts(industry: str, keywords: List[str] = None, location: str = None,
                           min_size: int = None, max_size: int = None,
                           technology_interests: List[str] = None,
                           limit: int = 10) -> str:
    """
    Identify target accounts for IT service sales based on specific criteria.

    :param industry: Target industry
    :param keywords: Additional keywords to refine search
    :param location: Target company location
    :param min_size: Minimum company size (number of employees)
    :param max_size: Maximum company size (number of employees)
    :param technology_interests: List of technologies the target may be interested in
    :param limit: Maximum number of accounts to return
    :return: List of potential target accounts with details
    """
    client = get_client()
    try:
        # Build search parameters
        search_params = {
            "keywords": industry,
        }

        if location:
            search_params["location"] = location

        # Execute search
        companies = client.search_companies(
            **search_params,
            limit=limit * 3  # Get more results for filtering
        )

        # Apply filters
        filtered_companies = []
        for company in companies:
            # Check company size
            staff_count = company.get("staffCount", 0)

            if min_size is not None and staff_count < min_size:
                continue

            if max_size is not None and staff_count > max_size:
                continue

            # Check for keywords in description
            description = company.get("description", "").lower()

            if keywords:
                keyword_match = False
                for keyword in keywords:
                    if keyword.lower() in description:
                        keyword_match = True
                        break

                if not keyword_match:
                    continue

            # Add to filtered results
            filtered_companies.append(company)

            # Break if we have enough
            if len(filtered_companies) >= limit:
                break

        # Format results
        results = []
        for company in filtered_companies[:limit]:
            company_id = company.get("entityUrn", "").split(":")[-1]
            company_name = company.get("name", "Unknown")
            company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"
            company_location = company.get("headquarter", {}).get("country", "Unknown") if company.get("headquarter") else "Unknown"
            company_size = company.get("staffCount", "Unknown")
            company_description = company.get("description", "No description available")[:200] + "..." if company.get("description") and len(company.get("description")) > 200 else company.get("description", "No description available")

            # Technology interest score
            tech_score = 0
            tech_mentions = []

            if technology_interests and company_description:
                for tech in technology_interests:
                    if tech.lower() in company_description.lower():
                        tech_score += 1
                        tech_mentions.append(tech)

            # Find key decision makers
            decision_makers = []
            try:
                # Default titles for IT services sales
                titles = ["CTO", "CIO", "IT Director", "VP of Technology"]

                # Get decision makers
                for title in titles[:2]:  # Limit to two titles
                    search_params = {
                        "company_name": company_name,
                        "title": title
                    }

                    # Execute search
                    people = client.search_people(
                        **search_params,
                        limit=1  # Just get one per title
                    )

                    # Add to results
                    for person in people:
                        profile_id = person.get("public_id", "")
                        profile_name = f"{person.get('firstName', '')} {person.get('lastName', '')}"
                        profile_title = person.get("occupation", "")
                        profile_url = f"https://www.linkedin.com/in/{profile_id}"

                        decision_makers.append({
                            "name": profile_name,
                            "title": profile_title,
                            "url": profile_url
                        })

            except Exception as e:
                logger.warning(f"Error finding decision makers for {company_name}: {e}")

            results.append({
                "company_id": company_id,
                "company_name": company_name,
                "industry": company_industry,
                "location": company_location,
                "size": company_size,
                "description": company_description,
                "tech_score": tech_score,
                "tech_mentions": tech_mentions,
                "decision_makers": decision_makers,
                "company_url": f"https://www.linkedin.com/company/{company_id}"
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error identifying target accounts: {e}")
        return f"Error identifying target accounts: {e}"


@mcp.tool()
def analyze_prospect_profile(profile_id: str, service_keywords: List[str] = None) -> str:
    """
    Analyze a prospect's profile for IT service sales.

    :param profile_id: LinkedIn profile ID
    :param service_keywords: List of IT service keywords to match against the profile
    :return: Analysis of the prospect's profile for IT service sales opportunities
    """
    client = get_client()
    try:
        # Get profile details
        profile = client.get_profile(profile_id)
        skills = client.get_profile_skills(profile_id)

        # Extract key information
        full_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        headline = profile.get("headline", "")
        location = profile.get("locationName", "")
        industry = profile.get("industryName", "")

        # Default service keywords if not provided
        if not service_keywords:
            service_keywords = [
                "cloud", "migration", "digital transformation", "infrastructure", "security",
                "automation", "devops", "ai", "machine learning", "data analytics", "integration",
                "erp", "crm", "software development", "consulting", "it services"
            ]

        # Experience
        experience = []
        current_company = ""
        current_title = ""

        for exp in profile.get("experience", []):
            company_name = exp.get("companyName", "")
            title = exp.get("title", "")
            description = exp.get("description", "")

            # Capture current job
            if exp.get("timePeriod", {}).get("endDate") is None:
                current_company = company_name
                current_title = title

            experience.append({
                "company": company_name,
                "title": title,
                "description": description
            })

        # Skills
        skill_list = [skill.get("name", "") for skill in skills]

        # Decision maker analysis
        decision_maker_score = 0
        decision_maker_titles = ["cto", "cio", "vp", "director", "chief", "head", "lead", "senior", "manager"]

        for title in decision_maker_titles:
            if title in current_title.lower():
                decision_maker_score += 1

        is_decision_maker = decision_maker_score > 0

        # Service interest analysis
        service_mentions = []
        service_score = 0

        # Check headline
        for keyword in service_keywords:
            if headline and keyword.lower() in headline.lower():
                service_mentions.append(keyword)
                service_score += 2  # Higher weight for headline

        # Check experience descriptions
        for exp in experience:
            description = exp.get("description", "").lower()
            for keyword in service_keywords:
                if keyword.lower() in description and keyword not in service_mentions:
                    service_mentions.append(keyword)
                    service_score += 1

        # Check skills
        for skill in skill_list:
            for keyword in service_keywords:
                if keyword.lower() in skill.lower() and keyword not in service_mentions:
                    service_mentions.append(keyword)
                    service_score += 1

        # Calculate opportunity score
        opportunity_score = 0

        # Decision maker adds points
        if is_decision_maker:
            opportunity_score += 30

        # Service interest adds points
        opportunity_score += min(service_score * 5, 50)  # Cap at 50 points

        # Current company size/industry adds points
        # This would require an additional API call to get company details
        # Omitting for simplicity

        # Opportunity level
        opportunity_level = "Low"
        if opportunity_score >= 70:
            opportunity_level = "High"
        elif opportunity_score >= 40:
            opportunity_level = "Medium"

        # Format results
        analysis = {
            "name": full_name,
            "headline": headline,
            "current_title": current_title,
            "current_company": current_company,
            "location": location,
            "industry": industry,
            "is_decision_maker": is_decision_maker,
            "service_interests": service_mentions,
            "service_score": service_score,
            "opportunity_score": opportunity_score,
            "opportunity_level": opportunity_level,
            "profile_url": f"https://www.linkedin.com/in/{profile_id}",
            "skills": skill_list[:10]  # Include top 10 skills
        }

        return json.dumps(analysis, indent=2)

    except Exception as e:
        logger.error(f"Error analyzing prospect profile: {e}")
        return f"Error analyzing prospect profile: {e}"


@mcp.tool()
def find_companies_using_technologies(technologies: List[str], industry: str = None,
                                    location: str = None, limit: int = 10) -> str:
    """
    Find companies that are using specific technologies.

    :param technologies: List of technologies to search for
    :param industry: Optional industry filter
    :param location: Optional location filter
    :param limit: Maximum number of companies to return
    :return: List of companies using the specified technologies
    """
    client = get_client()
    try:
        # Build search parameters
        search_params = {}

        # Add parameters that are provided
        if technologies and len(technologies) > 0:
            search_params["keywords"] = " ".join(technologies[:2])  # Use first two technologies as keywords

        if industry:
            search_params["industry"] = industry

        if location:
            search_params["location"] = location

        # Execute search
        companies = client.search_companies(
            **search_params,
            limit=limit * 3  # Get more results for filtering
        )

        # Format and filter results
        results = []
        for company in companies[:limit * 3]:
            company_id = company.get("entityUrn", "").split(":")[-1]
            company_name = company.get("name", "Unknown")
            company_description = company.get("description", "").lower()

            # Check for technology mentions in company description
            tech_mentions = []
            for tech in technologies:
                if tech.lower() in company_description:
                    tech_mentions.append(tech)

            # Only include companies that mention at least one technology
            if not tech_mentions:
                continue

            # Get company details
            company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"
            company_location = company.get("headquarter", {}).get("country", "Unknown") if company.get("headquarter") else "Unknown"
            company_size = company.get("staffCount", "Unknown")

            results.append({
                "id": company_id,
                "name": company_name,
                "industry": company_industry,
                "location": company_location,
                "size": company_size,
                "technologies_mentioned": tech_mentions,
                "url": f"https://www.linkedin.com/company/{company_id}"
            })

            # Break if we have enough results
            if len(results) >= limit:
                break

        # If we don't have enough results, try searching job postings
        if len(results) < limit:
            remaining = limit - len(results)

            # Get companies that have job postings with the technologies
            for tech in technologies:
                # Skip if we already have enough results
                if len(results) >= limit:
                    break

                # Search for jobs with this technology
                jobs = client.search_jobs(
                    keywords=tech,
                    limit=remaining * 2
                )

                # Extract companies
                for job in jobs:
                    if len(results) >= limit:
                        break

                    job_id = job.get("entityUrn", "").split(":")[-1]

                    try:
                        job_data = client.get_job(job_id=job_id)

                        company_data = job_data.get("companyDetails", {}).get("com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany", {})
                        company_info = company_data.get("companyResolutionResult", {})

                        company_id = company_info.get("entityUrn", "").split(":")[-1] if company_info.get("entityUrn") else None
                        company_name = company_info.get("name", "Unknown")

                        # Skip if this company is already in results
                        if any(r.get("id") == company_id for r in results):
                            continue

                        results.append({
                            "id": company_id,
                            "name": company_name,
                            "industry": "Unknown",  # Would need another API call
                            "location": "Unknown",  # Would need another API call
                            "size": "Unknown",      # Would need another API call
                            "technologies_mentioned": [tech],
                            "url": f"https://www.linkedin.com/company/{company_id}" if company_id else "#",
                            "source": "Job Posting"
                        })

                    except Exception as e:
                        logger.warning(f"Error processing job {job_id}: {e}")

        return json.dumps(results, indent=2)

    except Exception as e:
        logger.error(f"Error finding companies using technologies: {e}")
        return f"Error finding companies using technologies: {e}"


@mcp.tool()
def find_common_connections(profile_id1: str, profile_id2: str, limit: int = 5) -> str:
    """
    Find common connections or similarities between two LinkedIn profiles.

    :param profile_id1: First LinkedIn profile ID
    :param profile_id2: Second LinkedIn profile ID
    :param limit: Maximum number of common connections to return
    :return: Analysis of common connections and similarities
    """
    client = get_client()
    try:
        # Get profile details
        profile1 = client.get_profile(profile_id1)
        profile2 = client.get_profile(profile_id2)

        # Extract names
        name1 = f"{profile1.get('firstName', '')} {profile1.get('lastName', '')}"
        name2 = f"{profile2.get('firstName', '')} {profile2.get('lastName', '')}"

        # Find common companies
        companies1 = [exp.get("companyName", "").lower() for exp in profile1.get("experience", [])]
        companies2 = [exp.get("companyName", "").lower() for exp in profile2.get("experience", [])]

        common_companies = []
        for company in companies1:
            if company in companies2 and company not in common_companies:
                common_companies.append(company)

        # Find common education
        schools1 = [edu.get("schoolName", "").lower() for edu in profile1.get("education", [])]
        schools2 = [edu.get("schoolName", "").lower() for edu in profile2.get("education", [])]

        common_schools = []
        for school in schools1:
            if school in schools2 and school not in common_schools:
                common_schools.append(school)

        # Find common skills
        skills1 = [s.get("name", "").lower() for s in client.get_profile_skills(profile_id1)]
        skills2 = [s.get("name", "").lower() for s in client.get_profile_skills(profile_id2)]

        common_skills = []
        for skill in skills1:
            if skill in skills2 and skill not in common_skills:
                common_skills.append(skill)

        # Format results
        common_connections = {
            "profile1": {
                "id": profile_id1,
                "name": name1,
                "url": f"https://www.linkedin.com/in/{profile_id1}"
            },
            "profile2": {
                "id": profile_id2,
                "name": name2,
                "url": f"https://www.linkedin.com/in/{profile_id2}"
            },
            "common_companies": common_companies,
            "common_schools": common_schools,
            "common_skills": common_skills[:limit],
            "connection_strength": len(common_companies) + len(common_schools) + min(len(common_skills), 5)
        }

        return json.dumps(common_connections, indent=2)

    except Exception as e:
        logger.error(f"Error finding common connections: {e}")
        return f"Error finding common connections: {e}"


@mcp.tool()
def find_recent_job_changes(industry: str = None, title_keywords: List[str] = None,
                           location: str = None, limit: int = 10) -> str:
    """
    Find people who have recently changed jobs - potential sales opportunities.

    :param industry: Industry filter
    :param title_keywords: List of job title keywords to filter by
    :param location: Location filter
    :param limit: Maximum number of results
    :return: List of people who have recently changed jobs
    """
    client = get_client()
    try:
        # Build search parameters
        search_params = {}

        # Add parameters that are provided
        if industry:
            search_params["industry"] = industry

        if location:
            search_params["location_name"] = location

        if title_keywords and len(title_keywords) > 0:
            search_params["title"] = title_keywords[0]

        # Execute search
        people = client.search_people(
            **search_params,
            limit=limit * 3  # Get more results to filter for job changes
        )

        # Filter for recent job changes (looking at experience)
        recent_changes = []
        for person in people:
            profile_id = person.get("public_id", "")

            # Get full profile to analyze experience details
            try:
                profile = client.get_profile(profile_id)
                experiences = profile.get("experience", [])

                # Need at least 2 experiences to detect a change
                if len(experiences) < 2:
                    continue

                # Get the two most recent experiences
                current_exp = experiences[0]
                previous_exp = experiences[1]

                # Extract details
                current_company = current_exp.get("companyName", "")
                current_title = current_exp.get("title", "")
                previous_company = previous_exp.get("companyName", "")

                # Skip if the companies are the same (internal move)
                if current_company.lower() == previous_company.lower():
                    continue

                # Check if title matches any keywords (if provided)
                if title_keywords:
                    title_match = False
                    for keyword in title_keywords:
                        if keyword.lower() in current_title.lower():
                            title_match = True
                            break

                    if not title_match:
                        continue

                # Check how recent the change is
                current_start = current_exp.get("timePeriod", {}).get("startDate", {})
                if current_start:
                    start_year = current_start.get("year", 0)
                    start_month = current_start.get("month", 0)

                    # Get the current year and month
                    # This is simplified - in production you'd use actual date comparison
                    # Assuming changes in the last 6 months are "recent"
                    if start_year >= 2024:  # Simplified check for recent changes
                        # Format the result
                        name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
                        location = profile.get("locationName", "")

                        recent_changes.append({
                            "id": profile_id,
                            "name": name,
                            "current_title": current_title,
                            "current_company": current_company,
                            "previous_company": previous_company,
                            "location": location,
                            "url": f"https://www.linkedin.com/in/{profile_id}"
                        })

                        # Break if we have enough results
                        if len(recent_changes) >= limit:
                            break

            except Exception as e:
                logger.warning(f"Error processing profile {profile_id}: {e}")
                continue

        return json.dumps(recent_changes, indent=2)

    except Exception as e:
        logger.error(f"Error finding recent job changes: {e}")
        return f"Error finding recent job changes: {e}"


@mcp.tool()
def generate_sales_outreach_context(profile_id: str, company_service: str) -> str:
    """
    Generate personalized context for sales outreach based on a LinkedIn profile.

    :param profile_id: LinkedIn profile ID of the prospect
    :param company_service: Brief description of your company's service offering
    :return: Personalized context for sales outreach
    """
    client = get_client()
    try:
        # Get profile details
        profile = client.get_profile(profile_id)
        skills = client.get_profile_skills(profile_id)

        # Extract key information
        full_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        headline = profile.get("headline", "")
        current_title = ""
        current_company = ""

        # Experience
        experience = []
        for exp in profile.get("experience", []):
            company_name = exp.get("companyName", "")
            title = exp.get("title", "")

            # Capture current job
            if exp.get("timePeriod", {}).get("endDate") is None:
                current_company = company_name
                current_title = title

            experience.append({
                "company": company_name,
                "title": title
            })

        # Education
        education = []
        for edu in profile.get("education", []):
            education.append({
                "school": edu.get("schoolName", ""),
                "degree": edu.get("degreeName", ""),
                "field": edu.get("fieldOfStudy", "")
            })

        # Skills
        skill_list = [skill.get("name", "") for skill in skills]

        # Recent activity
        activity = []
        try:
            # This is a simplified approach - actual implementation would vary
            # based on what the LinkedIn API provides for activity
            profile_posts = client.get_profile_posts(profile_id, limit=3)

            for post in profile_posts:
                activity.append({
                    "type": "post",
                    "content": post.get("commentary", {}).get("text", "")[:100] + "..."
                })

        except Exception as e:
            logger.warning(f"Error getting profile activity: {e}")

        # Personal interests (inferred from profile details)
        interests = []

        # Check if current company has info available
        company_details = {}
        try:
            if current_company:
                # Search for the company
                companies = client.search_companies(keywords=current_company, limit=1)

                if companies:
                    company = companies[0]
                    company_id = company.get("entityUrn", "").split(":")[-1]
                    company_size = company.get("staffCount", "Unknown")
                    company_industry = company.get("industries", ["Unknown"])[0] if company.get("industries") else "Unknown"

                    company_details = {
                        "id": company_id,
                        "name": current_company,
                        "size": company_size,
                        "industry": company_industry
                    }

        except Exception as e:
            logger.warning(f"Error getting company details: {e}")

        # Generate outreach context
        outreach_context = {
            "prospect": {
                "name": full_name,
                "title": current_title,
                "company": current_company,
                "headline": headline,
                "url": f"https://www.linkedin.com/in/{profile_id}"
            },
            "company_details": company_details,
            "top_skills": skill_list[:5],
            "education_background": education,
            "experience_summary": experience[:3],
            "recent_activity": activity,
            "common_connections": [],  # Would require additional API calls
            "personalization_points": []
        }

        # Generate personalization points
        personalization_points = []

        # Current role/responsibility
        if current_title:
            personalization_points.append({
                "type": "role",
                "context": f"Current role as {current_title} at {current_company}"
            })

        # Skills related to service
        service_related_skills = []
        service_keywords = company_service.lower().split()

        for skill in skill_list:
            for keyword in service_keywords:
                if keyword.lower() in skill.lower() and skill not in service_related_skills:
                    service_related_skills.append(skill)

        if service_related_skills:
            personalization_points.append({
                "type": "skills",
                "context": f"Skills related to your services: {', '.join(service_related_skills)}"
            })

        # Educational background
        if education:
            school = education[0].get("school", "")
            degree = education[0].get("degree", "")
            field = education[0].get("field", "")

            if school:
                personalization_points.append({
                    "type": "education",
                    "context": f"Educational background: {degree} in {field} from {school}"
                })

        # Career progression
        if len(experience) >= 2:
            progression = []
            for i, exp in enumerate(experience[:3]):
                progression.append(f"{exp.get('title')} at {exp.get('company')}")

            personalization_points.append({
                "type": "career",
                "context": f"Career progression: {' → '.join(progression)}"
            })

        # Add personalization points to context
        outreach_context["personalization_points"] = personalization_points

        # Add recommended conversation starters
        conversation_starters = [
            f"I noticed you've been at {current_company} as {current_title}. How has your experience been so far?",
            f"I saw you have expertise in {', '.join(skill_list[:2])}. What projects are you currently focused on?"
        ]

        if service_related_skills:
            conversation_starters.append(f"Your experience with {service_related_skills[0]} caught my attention. Have you been working on any initiatives related to this recently?")

        if education:
            conversation_starters.append(f"I see we share an interest in {education[0].get('field', '')}. What drew you to that field?")

        outreach_context["conversation_starters"] = conversation_starters

        return json.dumps(outreach_context, indent=2)

    except Exception as e:
        logger.error(f"Error generating sales outreach context: {e}")
        return f"Error generating sales outreach context: {e}"

# Add main execution block
if __name__ == "__main__":
    print(search_jobs(keywords="data engineer", location="Jakarta", limit=2))
