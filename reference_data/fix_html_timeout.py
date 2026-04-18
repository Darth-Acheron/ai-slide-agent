with open('/Users/bryan/projects/markdown-to-slides/web/templates/index.html', 'r') as f:
    text = f.read()

text = text.replace('~40s each', '~130s each')

# Fix error handling logic to alert on failure
text = text.replace('if (data.image_url) {', 'if (data.image_url) {')
# To easily replace without regex, let's just patch the two occurrences.
import re
text = re.sub(
    r'(const data = await res\.json\(\);\s*)if \(data\.image_url\)',
    r'\1if (data.error) { throw new Error(data.error); }\n          if (data.image_url)',
    text
)

with open('/Users/bryan/projects/markdown-to-slides/web/templates/index.html', 'w') as f:
    f.write(text)

with open('/Users/bryan/projects/markdown-to-slides/fix_html.py', 'r') as f:
    text2 = f.read()
text2 = text2.replace('~40s each', '~130s each')
text2 = re.sub(
    r'(const data = await res\.json\(\);\s*)if \(data\.image_url\)',
    r'\1if (data.error) { throw new Error(data.error); }\n          if (data.image_url)',
    text2
)
with open('/Users/bryan/projects/markdown-to-slides/fix_html.py', 'w') as f:
    f.write(text2)
