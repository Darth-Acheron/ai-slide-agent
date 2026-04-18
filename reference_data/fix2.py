with open('web/templates/index.html', 'r') as f:
    c = f.read()

c = c.replace('<\\/script>', '<\\\\/script>')

with open('web/templates/index.html', 'w') as f:
    f.write(c)
