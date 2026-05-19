
import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Combined regex to catch the block.
    # We use non-greedy matching .*?
    # We allow matched content to include newlines (re.DOTALL)
    # We want to keep the INCOMING part (after =======)
    
    # Pattern explanation:
    # <<<<<<< HEAD (followed by anything until newline)
    # (content 1 - ignored)
    # ======= (followed by anything until newline, usually empty)
    # (content 2 - KEPT)
    # >>>>>>> (followed by anything until newline, usually commit hash)
    
    pattern = re.compile(r'<<<<<<< HEAD.*?=======+(.*?)>>>>>>>.*?\n?', re.DOTALL)
    
    def replacer(match):
        # Return only the Incoming part (Group 1 in this new regex)
        # Note: The regex above captures only ONE group for the part we want.
        # Wait, I need to match the FIRST part to ignore it.
        return match.group(1)

    # Let's fix the regex logic to be safer:
    pattern = re.compile(r'<<<<<<< HEAD.*?=======+(.*?)>>>>>>>.*?\n', re.DOTALL)
    
    # If the file ends with the conflict without a newline, checking \n might fail?
    # Let's use specific markers
    pattern = re.compile(r'<<<<<<< HEAD.*?=======[\r\n]+(.*?)>>>>>>>[^\n]*\n?', re.DOTALL)

        
    new_content, count = pattern.subn(replacer, content)
    
    if count > 0:
        print(f"Fixed {count} conflicts in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
import sys

def main():
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()
        
    print(f"Scanning {root_dir}...")
    
    extensions = ('.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.html', '.css')
    
    for subdir, dirs, files in os.walk(root_dir):
        if 'node_modules' in subdir:
            continue
            
        for file in files:
            if file.endswith(extensions):
                fix_file(os.path.join(subdir, file))

if __name__ == '__main__':
    main()
