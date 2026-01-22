import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ERP_BASE_URL")
API_KEY = os.getenv("ERP_API_KEY")
API_SECRET = os.getenv("ERP_API_SECRET")

HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def erp_get(doctype: str, name: str):
    """Fetch a specific document."""
    url = f"{BASE_URL}/api/v2/document/{doctype}/{name}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": response.text if 'response' in locals() else "No response"}

def erp_count(doctype: str):
    """Count number of docs for a Doctype."""
    url = f"{BASE_URL}/api/v2/doctype/{doctype}/count"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def erp_list(doctype: str, *args,**kwargs):
    """
    Enhanced list function:
    - limit=0 fetches ALL records.
    - fields=["name", "status"] reduces data load.
    - filters=[["status", "=", "Open"]] allows searching.
    """
    
    url = f"{BASE_URL}/api/v2/document/{doctype}"
    limit = kwargs.get("limit", 0)
    params = {
        "limit_page_length": limit # 0 = All records
    }

    fields = kwargs.get("fields")
    filters = kwargs.get("filters")

    if fields:
        url = url + "?fields=" + json.dumps(fields)
    elif filters:
        url += "?filters=" + json.dumps(filters)
    print(f"   >>> [INTERNAL] Calling API: GET {url}")
    print(f"   >>> [INTERNAL] Filters: {filters} | Fields: {fields} | Limit: {limit}")
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "details": response.text if 'response' in locals() else "No response"}

# Registry maps tool names to actual functions for the Agent to use
TOOL_REGISTRY = {
    "erp_get": erp_get,
    "erp_count": erp_count,
    "erp_list": erp_list
}