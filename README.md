#  Code Review AI Tool

An intelligent, context-aware code review system that uses Large Language Models (LLMs) to generate human-like feedback for newly added code. It leverages both the **current project context** and **global coding patterns** from public GitHub repositories.
You can use this as a tool to consult and gain quality feedback before committing changes to your codebase.



##  Features

-  **Context-Aware Review**: Uses FAISS to embed and search similar code within both the local and global codebases to implement best practices while also maintaining code styles and context from current codebase.
-  **LLM Feedback**: Integrates with OpenAI's GPT models for high-quality, human-like suggestions.
-  **GitHub Repo Input**: Accepts a repo link instead of file uploads.
-  **React Frontend**: Clean UI for input, progress, and animated feedback.


## Installation and Set Up

Clone this project:

```
git clone https://github.com/aayushbhat4/CodeReviewToolv1.git
cd CodeReviewTool
```

Set up Python dependencies:

```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Start the Flask server:
```
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Start the Frontend:
```
cd frontend
npm install
npm run dev
```

## Usage
![Screenshot 2025-04-19 005833](https://github.com/user-attachments/assets/7662b9d8-f07a-4c3a-9c66-34d7a4d539d8)

Make sure your Github repository is set to public.


