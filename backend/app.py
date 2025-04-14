from flask import Flask, request, jsonify
import os
import pickle
import shutil
import traceback

# Fix OpenMP duplicate library issue
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from backend.githubScraper import download_repo_zip
from backend.mainCode import (
    extract_code_snippets,
    build_faiss_index,
    search_similar_dual,
    format_dual_context_prompt,
    get_llm_review
)

app = Flask(__name__)

@app.route("/review", methods=["POST"])
def review():
    repo_url = request.json.get("repo_url")
    new_code = request.json.get("new_code")
    temp_dir = "temp_repo"

    try:
        print("[INFO] Received review request.")
        
        # Step 1: Download and extract repo
        if os.path.exists(temp_dir):
            print("[INFO] Cleaning existing temp_repo directory.")
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        clean_repo_url = repo_url.rstrip(".git")
        api_url = clean_repo_url.replace("https://github.com/", "https://api.github.com/repos/")
        print(f"[INFO] Downloading repo from: {clean_repo_url}")
        result = download_repo_zip(api_url, clean_repo_url, temp_dir)
        if not result:
            return jsonify({"error": "Failed to download repo"}), 400

        # Step 2: Extract snippets and build FAISS
        print("[INFO] Extracting code snippets...")
        local_snippets = extract_code_snippets(temp_dir)
        print("[INFO] Building FAISS index...")
        local_index, local_embeddings = build_faiss_index(local_snippets)

        # Step 3: Load global FAISS index
        print("[INFO] Loading global FAISS index...")
        with open("cached_index.pkl", "rb") as f:
            global_index, global_embeddings, global_snippets = pickle.load(f)

        # Step 4: Search similar snippets
        print("[INFO] Searching for similar code...")
        local_matches, global_matches = search_similar_dual(
            local_index, local_embeddings, local_snippets,
            global_index, global_embeddings, global_snippets,
            new_code, current_file=None
        )

        # Step 5: Format prompt and get review
        print("[INFO] Formatting prompt and generating feedback...")
        prompt = format_dual_context_prompt(new_code, local_matches, global_matches)
        feedback = get_llm_review(prompt)

        print("[INFO] Review complete.")
        print(feedback)

        # Cleanup
        shutil.rmtree(temp_dir)
        return jsonify({"feedback": feedback})

    except Exception as e:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("[INFO] Starting Flask server...")
    app.run(debug=True, use_reloader=False)
