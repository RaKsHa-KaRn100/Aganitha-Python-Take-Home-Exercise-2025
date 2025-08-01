import requests
import csv
import xml.etree.ElementTree as ET

def fetch_and_save_papers(query: str, filename: str = "output.csv", debug: bool = False):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"
    fetch_url = f"{base_url}efetch.fcgi"
    
    # Step 1: Search for PubMed IDs
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 20
    }
    search_res = requests.get(search_url, params=search_params)
    ids = search_res.json().get("esearchresult", {}).get("idlist", [])
    
    if not ids:
        print("No papers found.")
        return
    
    # Step 2: Fetch article details
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml"
    }
    fetch_res = requests.get(fetch_url, params=fetch_params)
    root = ET.fromstring(fetch_res.text)
    
    papers = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        pub_date = article.findtext(".//PubDate/Year") or "N/A"

        affiliations = article.findall(".//AffiliationInfo")
        non_academic_authors = []
        company_affiliations = []
        email = "N/A"
        for aff in affiliations:
            affiliation = aff.findtext("Affiliation") or ""
            if any(word in affiliation.lower() for word in ["inc", "ltd", "company", "biotech", "pharma"]):
                company_affiliations.append(affiliation)
                author_name = aff.findtext("../LastName")
                if author_name:
                    non_academic_authors.append(author_name)
            if "@" in affiliation and email == "N/A":
                email = affiliation.split()[-1]  # crude email extraction

        if company_affiliations:
            papers.append([pmid, title, pub_date, "; ".join(non_academic_authors), "; ".join(company_affiliations), email])

    if not papers:
        print("No qualifying papers with company affiliations found.")
        return

    # Save to CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
        writer.writerows(papers)
    
    if debug:
        print(f"Saved {len(papers)} paper(s) to {filename}")
