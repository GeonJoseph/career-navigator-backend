import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

def _call_jsearch(query: str, location: str = "", page: int = 1):
    """
    Fetch data from JSearch API via RapidAPI.
    Docs: https://rapidapi.com/letscrape-6bR7noP7u/api/jsearch
    """
    if not RAPIDAPI_KEY:
        return {"error": "RAPIDAPI_KEY not configured in .env", "results": []}

    url = "https://jsearch.p.rapidapi.com/search"
    
    # Combined search query for better precision
    full_query = query
    if location:
        full_query += f" in {location}"

    querystring = {
        "query": full_query,
        "page": str(page),
        "num_pages": "1",
        "date_posted": "all"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        raw_results = data.get("data", [])
        results = []
        
        for job in raw_results:
            # JSearch provides multiple apply options, we'll take the first one or job_apply_link
            apply_link = job.get("job_apply_link")
            if not apply_link and job.get("apply_options"):
                apply_link = job.get("apply_options")[0].get("apply_link")

            results.append({
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "Unknown"),
                "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(", "),
                "url": apply_link or job.get("job_google_link", "#"),
                "description": job.get("job_description", "")[:200],
                "posted_date": job.get("job_posted_at_datetime_utc", ""),
                "category": job.get("job_employment_type", "General"),
                "salary_min": job.get("job_min_salary"),
                "salary_max": job.get("job_max_salary")
            })
            
        return {
            "results": results,
            "total": 100, # JSearch doesn't always give a simple total count in the search endpoint
            "page": page
        }
    except Exception as e:
        print(f"JSearch API error: {e}")
        return {"results": [], "total": 0, "page": page, "error": str(e)}

def search_jobs(query: str, location: str = "", page: int = 1):
    return _call_jsearch(query, location, page)

def search_internships(query: str, location: str = "", page: int = 1):
    # Search for internships specifically
    return _call_jsearch(f"{query} internship", location, page)
