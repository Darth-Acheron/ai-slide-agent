import os
import re

app_file = os.path.expanduser("~/projects/markdown-to-slides/web/app.py")
with open(app_file, "r") as f:
    content = f.read()

# Change filepath = os.path.join("static", "images", filename)
# To filepath = os.path.join(app.static_folder, "images", filename)
content = content.replace(
    'filepath = os.path.join("static", "images", filename)',
    'os.makedirs(os.path.join(app.static_folder, "images"), exist_ok=True)\n        filepath = os.path.join(app.static_folder, "images", filename)'
)

with open(app_file, "w") as f:
    f.write(content)

print("Path fixed in app.py")
