"""import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")
T1 = torch.randn(4,4)
T2= T1.to(device)
print(T1)
print(T2)"""
import pickle
from mainCode import search_similar, format_prompt, get_llm_review

new_code_snippet = """
def calculate_area(radius):
    return 3.14 * radius * radius
"""

with open("cached_index.pkl", "rb") as f:
    index, embeddings, snippets = pickle.load(f)

local_matches, global_matches = search_similar(index, embeddings, snippets, new_code_snippet)

prompt = format_prompt(new_code_snippet, local_matches, global_matches)
review = get_llm_review(prompt)

print("🔍 Code Review:\n")
print(review)