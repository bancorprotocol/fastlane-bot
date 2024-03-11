import re
import os

# Function to replace the second colon in a matching line
def replace_second_colon(line):
    # Regular expression that matches lines with the specified format:
    # Starts with optional whitespace, followed by a tag (alphanumeric and underscores)
    # between two colons. Captures the content before the second colon.
    pattern = r'^(.*?\:[a-zA-Z0-9_]+)\:'
    # Replace the second colon with a space, if the pattern matches
    return re.sub(pattern, r'\1 ', line)

# Process all .py files in the current directory
for filename in os.listdir('.'):
    if filename.endswith('.py'):
        # Read the content of the file
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Apply the replacement to each line
        modified_lines = [replace_second_colon(line) for line in lines]

        # Write the modified content back to the file
        with open(filename, 'w') as file:
            file.writelines(modified_lines)
