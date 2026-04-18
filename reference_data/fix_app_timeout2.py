with open('/Users/bryan/projects/markdown-to-slides/web/app.py', 'r') as f:
    text = f.read()

text = text.replace('timeout=60', 'timeout=180')

with open('/Users/bryan/projects/markdown-to-slides/web/app.py', 'w') as f:
    f.write(text)
