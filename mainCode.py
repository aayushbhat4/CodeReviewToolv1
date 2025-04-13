from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import faiss
import os
import openai
from tqdm import tqdm


model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



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

def build_faiss_index(snippets):
    print("Building FAISS index...")
    embeddings = embed_codes_batch(snippets)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings))
    print("Index built successfully.")
    return index, embeddings

def search_similar(index, embeddings, snippets, new_code, current_file=None, k_local=3, k_global=2):
    new_emb = torch.tensor(embed_code(new_code)).cpu().reshape(1, -1)  # ensure CPU for FAISS
    D, I = index.search(new_emb.numpy(), k_local + k_global)

    local_matches = []
    global_matches = []

    for i, idx in enumerate(tqdm(I[0], desc="Searching similar code")):
        match = snippets[idx]
        if current_file and match['file'] == current_file:
            local_matches.append(match)
        else:
            global_matches.append(match)

    return local_matches[:k_local], global_matches[:k_global]
def format_prompt(new_code, local_matches, global_matches):
    prompt = f"""
You are reviewing new code added to a project.

New code:
{new_code}

Similar code from the SAME file:
"""
    for m in local_matches:
        prompt += f"\nFile: {m['file']}\n{m['code']}\n"

    prompt += "\nOther relevant patterns from the project:\n"
    for m in global_matches:
        prompt += f"\nFile: {m['file']}\n{m['code']}\n"

    prompt += "\nPlease provide a code review with more emphasis on the patterns from the same file."
    return prompt

from openai import OpenAI

client = OpenAI(api_key =("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"))

def get_llm_review(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful software engineer providing feedback on code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content
