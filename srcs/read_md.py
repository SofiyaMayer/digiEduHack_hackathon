import json
import requests
from pathlib import Path

def read_md_files(path_pattern):
    folder = Path(path_pattern).parent
    pattern = Path(path_pattern).name

    all_results = []

    for file in folder.glob(pattern):
        md_text = file.read_text(encoding="utf-8")

        prompt = f"""
        You are an AI writing analyst.

        Analyze the following markdown and return ONLY valid JSON.

        JSON format:
        {{
            "file": "{file.name}",
            "summary": "",
            "key_points": [],
            "main_problems": [],
            "required_changes": [],
            "suggested_improvements": [],
            "final_evaluation": "",
            "anonymized_names": true
        }}

        Real names must be anonymized.

        Markdown:
        {md_text}
        """
        response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )

    raw = response.json()["response"]

    # Try to parse JSON output from the model
    try:
        parsed = json.loads(raw)
    except:
        # If the model adds text before/after JSON → extract block
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            parsed = {"file": file.name, "error": "Could not parse JSON", "raw_output": raw}

    all_results.append(parsed)

    return all_results

def main():
    results = read_md_files("/home/sasha/Downloads/data_samples_eduzmena/Data samples/*.md")
    for res in results:
        print(f"\n=== Analysis for {res['file']} ===\n")
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()



