with open('web/templates/index.html', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "const inlineRegex =" in line:
        lines[i] = "        const inlineRegex = new RegExp('!\\\\\\\\[(.*?)\\\\\\\\]\\\\\\\\(auto\\\\\\\\)', 'g');\n"
    if "const bgRegex =" in line:
        lines[i] = "        const bgRegex = new RegExp('<' + '!--\\\\\\\\s*bg:\\\\\\\\s*(.*?)\\\\\\\\s*--' + '>', 'g');\n"

with open('web/templates/index.html', 'w') as f:
    f.writelines(lines)
