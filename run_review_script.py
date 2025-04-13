from mainCode import (
    extract_code_snippets,
    build_faiss_index,
    search_similar,
    format_prompt,
    get_llm_review,
   
)
import os
import pickle
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



"""snippets = extract_code_snippets("global_codebase")
index, embeddings = build_faiss_index(snippets)




with open("cached_index.pkl", "wb") as f:
    pickle.dump((index, embeddings, snippets), f)"""

# Load later
with open("cached_index.pkl", "rb") as f:
    index, embeddings, snippets = pickle.load(f)

new_code = """
def get_github_trending(language="python"):
    url = f"https://github.com/trending/{language}?since=daily"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None
"""


# Step 3: Search for relevant local/global examples
local_matches, global_matches = search_similar(index, embeddings, snippets, new_code, current_file=None)

# Step 4: Build a prompt and get a review
#prompt = format_prompt(new_code, local_matches, global_matches)
prompt = format_prompt(new_code, local_matches, global_matches)
review = get_llm_review(prompt)

# Step 5: Output the review
print("🔍 Code Review:\n")
print(review)