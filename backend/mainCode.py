from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import faiss
import os
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
open_ai_key = os.getenv("OPEN_API_KEY")

print("OpenAI Key: ", open_ai_key)

model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


#Embed the code snippets using CodeBERT
def embed_code(code_snippet):
    tokens = tokenizer(code_snippet, return_tensors='pt', truncation=True, padding=True).to(device)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

def embed_codes_batch(snippets, batch_size=16):
    embeddings = []
    for i in tqdm(range(0, len(snippets), batch_size), desc="Embedding code snippets"):
        batch = snippets[i:i+batch_size]
        tokenized = tokenizer([s["code"] for s in batch], return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            output = model(**tokenized)
        batch_embeddings = output.last_hidden_state.mean(dim=1).cpu().numpy()
        embeddings.extend(batch_embeddings)
    return embeddings
#
def extract_code_snippets(folder_path):
    snippets = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()
                for func in code.split("def ")[1:]:
                    func_code = "def " + func.split("\n\n")[0]
                    snippets.append({
                        "code": func_code,
                        "file": path,
                        "repo": folder_path
                    })
    return snippets


#Build the FAISS index
def build_faiss_index(snippets):
    print("Building FAISS index...")
    embeddings = embed_codes_batch(snippets)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings))
    print("Index built successfully.")
    return index, embeddings


#Searching the FAISS index for similar code snippets
def search_similar_dual(
    local_index, local_embeddings, local_snippets,
    global_index, global_embeddings, global_snippets,
    new_code, current_file=None, k_local=3, k_global=2
):
    """
    Searches both local and global codebases separately using FAISS,
    and returns a dual context (local + global matches).
    """

    # 1. Embed the new code
    new_emb = torch.tensor(embed_code(new_code)).cpu().reshape(1, -1).numpy().astype("float32")

    # 2. Search local
    D_local, I_local = local_index.search(new_emb, k_local + 5)  # extra buffer in case of file mismatch
    local_matches = []
    for i in tqdm(I_local[0], desc="Searching local context"):
        if i >= len(local_snippets): continue
        match = local_snippets[i]
        if current_file and match['file'] == current_file:
            local_matches.append(match)
        elif not current_file:
            local_matches.append(match)
        if len(local_matches) >= k_local:
            break

    # 3. Search global
    D_global, I_global = global_index.search(new_emb, k_global + 5)
    global_matches = []
    for i in tqdm(I_global[0], desc="Searching global context"):
        if i >= len(global_snippets): continue
        match = global_snippets[i]
        global_matches.append(match)
        if len(global_matches) >= k_global:
            break

    return local_matches, global_matches


def format_dual_context_prompt(new_code, local_matches, global_matches):
    """
    Create a prompt with dual context for LLM review.
    """
    prompt = f"""
You are reviewing a newly written code snippet in a software project. Use the existing patterns from the same file (local context) and from the rest of the project or similar repositories (global context) to assess it.

### New Code
{new_code}

### Local Context (Same File)
"""
    for m in local_matches:
        prompt += f"\nFile: {m['file']}\n{m['code']}\n"

    prompt += "\n### Global Context (Other Files or Repos)\n"
    for m in global_matches:
        prompt += f"\nFile: {m['file']}\n{m['code']}\n"

    prompt += "\n### Review the new code based on the context above. Highlight structure, bugs, and improvements. Keep comments minimal but insightful (max 5)."
    return prompt



client = OpenAI(api_key = open_ai_key)

def get_llm_review(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful software engineer providing feedback on code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content
