import requests
data = {
    "repo_url": "https://github.com/aayushbhat4/CodeReviewTool.git",  # Replace with the repo URL to test
    "new_code": """
def get_github_trending(language="python"):
    url = f"https://github.com/trending/{language}?since=daily"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None
"""  # Replace with the code you want to review
}

response = requests.post("http://127.0.0.1:5000/review", json=data)

# Print the response
print(response.json())