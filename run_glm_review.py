import os
import requests
import json
import subprocess

def run_glm_review():
    print("Reading project files...")
    
    with open('/Users/bryan/projects/markdown-to-slides/specs/01_system_architecture_and_design.md', 'r') as f:
        spec_content = f.read()
        
    with open('/Users/bryan/projects/markdown-to-slides/web/app.py', 'r') as f:
        app_content = f.read()

    with open('/Users/bryan/projects/markdown-to-slides/web/templates/index.html', 'r') as f:
        index_content = f.read()

    system_prompt = "You are a senior full-stack developer and architect. Review the provided specification and the actual code implementation. Identify bugs, potential security issues, misalignments with the specification, and areas for improvement. Provide actionable recommendations."
    
    user_prompt = f"""
    ### 1. SPECIFICATION (01_system_architecture_and_design.md)
    {spec_content}
    
    ### 2. BACKEND IMPLEMENTATION (app.py)
    ```python
    {app_content}
    ```
    
    ### 3. FRONTEND IMPLEMENTATION (index.html)
    ```html
    {index_content}
    ```
    
    Please provide:
    1. An assessment of how well the code aligns with the spec.
    2. Any bugs or issues found in the code (especially around error handling, pathing, or UI edge cases).
    3. Suggestions for what tests should be written in a `test_app.py` script to verify core functionality.
    """

    print("Calling GLM-5.1 via DashScope API...")
    url = "https://dashscope.aliyuncs.com/apps/anthropic/v1/messages"
    headers = {
        "x-api-key": os.environ.get("DASHSCOPE_API_KEY", ""),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "glm-5.1",
        "max_tokens": 4000,
        "messages": [
            {"role": "user", "content": system_prompt + "\n\n" + user_prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=240)
        response.raise_for_status()
        result = response.json()
        
        output_text = ""
        for item in result.get('content', []):
            if item.get('type') == 'text':
                output_text += item.get('text', '')
                
        print("\n--- GLM-5.1 REVIEW RESULTS ---\n")
        print(output_text)
        
        with open('glm_review.md', 'w') as f:
            f.write(output_text)
            
    except Exception as e:
        print(f"Error calling GLM-5.1: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == '__main__':
    run_glm_review()
