with open('/Users/bryan/projects/markdown-to-slides/web/app.py', 'r') as f:
    text = f.read()

text = text.replace('timeout=120', 'timeout=300')

with open('/Users/bryan/projects/markdown-to-slides/web/app.py', 'w') as f:
    f.write(text)
