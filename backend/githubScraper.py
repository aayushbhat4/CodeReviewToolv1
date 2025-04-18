# github_fetcher.py

import requests  # used to make HTTP requests to GitHub API and download files
import os         # for directory creation and file path handling
import zipfile    # for unzipping downloaded repo archives
from io import BytesIO  # to handle byte-streams from downloaded zip files
from tqdm import tqdm 
from dotenv import load_dotenv
load_dotenv()
github_api_key = os.getenv("GITHUB_KEY")
 # used to show progress bars while downloading


GITHUB_API = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
HEADERS["Authorization"] = github_api_key

def search_repos(query, max_repos=10):
    """
    Search GitHub repositories using query parameters.

    Args:
        query (str): GitHub API search query string.
        max_repos (int): Max number of repositories to fetch.

    Returns:
        list: List of repository metadata dictionaries.
    """
    repos = []
    page = 1
    while len(repos) < max_repos:
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 30,
            "page": page
        }
        r = requests.get(GITHUB_API, headers=HEADERS, params=params)
        data = r.json()
        if "items" not in data:
            print("Error:", data)
            break
        repos.extend(data["items"])
        if len(data["items"]) == 0:
            break
        page += 1
    return repos[:max_repos]

def download_repo_zip(repo_api_url, repo_html_url, dest_folder):
    """
    Download and extract the zip of a GitHub repo's default branch.

    Args:
        repo_api_url (str): GitHub API URL for the repo.
        repo_html_url (str): GitHub HTML URL for the repo.
        dest_folder (str): Local folder to extract repo contents into.

    Returns:
        str: Destination folder path or None if failed.
    """
    r_meta = requests.get(repo_api_url, headers=HEADERS)
    if r_meta.status_code != 200:

        print(f"Failed to fetch metadata for {repo_html_url}")
        return None

    default_branch = r_meta.json().get("default_branch", "main")
    zip_url = repo_html_url + f"/archive/refs/heads/{default_branch}.zip"
    r = requests.get(zip_url)
    if r.status_code != 200:
        print(r, r.status_code)
        print(f"Failed to download {repo_html_url} with branch {default_branch}, the error was {r.status_code}\n")
        return None

    with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
        zip_ref.extractall(dest_folder)
    return dest_folder

def fetch_top_python_repos(dest="global_codebase", query="language:Python stars:>1000", count=10):
    """
    Fetch and download top Python repositories from GitHub.

    Args:
        dest (str): Directory where repos will be saved.
        query (str): GitHub search query.
        count (int): Number of repos to download.
    """
    os.makedirs(dest, exist_ok=True)
    repos = search_repos(query, max_repos=count)
    for repo in tqdm(repos, desc="Downloading repos"):
        name = repo["full_name"].replace("/", "-")
        repo_path = os.path.join(dest, name)
        if not os.path.exists(repo_path):
            print(f"Downloading {name}")
            download_repo_zip(repo["url"], repo["html_url"], repo_path)
        else:
            print(f"Already exists: {name}")

if __name__ == "__main__":
    fetch_top_python_repos(count=0)  # Change to more if needed

