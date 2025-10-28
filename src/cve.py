import requests
from typing import TypedDict

class CVEPackage(TypedDict):
    name: str
    ecosystem: str
    purl: str

class CVEAffectedPackage(TypedDict):
    package: CVEPackage
    ranges: list[dict[str, list[dict[str, str]]]]
    ecosystem_specific: dict[str, list[str]]
    database_specific: dict[str, str]

class CVEData(TypedDict):
    id: str
    summary: str
    details: str
    modified: str
    published: str
    # List of CVE references
    upstream: list[str]
    # severity score (High...)
    database_specific: dict[str, str]
    references: list[dict[str, str]]
    affected: list[dict[str, str]]


def fetch_cve_data(cve_id: str) -> CVEData:
    """
    Fetch CVE data from a hypothetical CVE database.

    Args:
        cve_id (str): The CVE identifier to fetch data for.

    Returns:
        dict: A dictionary containing CVE data, or an error message.
    """
    # Simulated database query
    url = f"https://api.osv.dev/v1/vulns/{cve_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {cve_id}: {response.status_code}")
    
    data = response.json()
    return data