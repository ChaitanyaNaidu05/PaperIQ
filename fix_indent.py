import re

with open(r"c:\Users\chait\Projects\PaperIQ\app\main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for i, line in enumerate(lines):
    if 752 <= i < 823:
        # these lines were indented by 28 spaces, need them to be 20 basically we remove 8 spaces
        if line.startswith("        "):
            output.append(line[8:])
        else:
            output.append(line)
    elif 823 <= i < 827: # the old except block
        pass # skip it entirely
    else:
        output.append(line)

with open(r"c:\Users\chait\Projects\PaperIQ\app\main.py", "w", encoding="utf-8") as f:
    f.writelines(output)
