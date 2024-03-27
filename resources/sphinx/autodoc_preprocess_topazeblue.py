import re

def setup(app):
    app.connect('autodoc-process-docstring', pre_process_docstring)


# Regular expression pattern
_PATTERN = r'^\s*(:)(\w+)(:)\s+(.*)$'

# Replacement function
def _replace(match):
    #if match.group(2) == "returns" or match.group(2) == "rtype" or match.group(2) == "return" or match.group(2) == "raises" or match.group(2) == "raise" or match.group(2) == "except" or match.group(2) == "exception" or match.group(2) == "yields" or match.group(2) == "yield":
    if match.group(2) in ["returns", "rtype", "return", "raises", "raise", "except", "exception", "yields", "yield"]:
        return f"{match.group(1)}{match.group(2)}{match.group(3)} {match.group(4)}"
    return f"{match.group(1)}param {match.group(2)}{match.group(3)} {match.group(4)}"
    

def pre_process_docstring(app, what, name, obj, options, lines):
    """
    pre-processes docstrings in the format used in topaze.blue code
    
    This function is called before the docstring is parsed by autodoc. It modifies the docstring
    lines in place, then passing them back to autodoc. Changes made are the following:
    
    1. the first line of the docstring is usually a summary, and separated from the rest of the text
    by a blank line. The first line is emphasized.
    
    2. In topaze.blue code, for readability the `param` term in `:param variable: description` is implied,
    ie it only uses `:variable: description`. This function adds `param` before the variable name.
    
    3. If there is a line that ONLY has "---" plus whitespace then that line and everything after it 
    is removed 
    """
    # try:
    #     if len(lines)==1 or lines[1].strip() == "":
    #         lines[0] = f"**{lines[0].strip()}**"
    # except:
    #     pass
    new_lines = []
    for line in lines:
        if line.strip() == "---":
            break
        if re.match(_PATTERN, line):
            # If it matches, perform the replacement
            new_line = re.sub(_PATTERN, _replace, line)
            #print("Modified line:", new_line)
        else:
            new_line = line
        new_lines.append(new_line)
    lines[:] = new_lines  # Update the original list with modified lines
