
import re

file_path = r'c:\Users\jeffe\Documents\Sites\CSHub\templates\base.html'

def analyze_tags():
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Simple regex for tags we care about
    tag_re = re.compile(r'{%\s*(if|elif|else|endif|for|endfor|block|endblock|with|endwith)\s+.*?%}')

    print(f"Analyzing {file_path}...")
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check specifically around line 214
        if line_num >= 210 and line_num <= 220:
            print(f"{line_num}: {line.strip()}")

        matches = tag_re.finditer(line)
        for match in matches:
            tag_full = match.group(0)
            tag_name = match.group(1)
            
            # Print recent stack actions
            # print(f"L{line_num}: Found {tag_name} | Stack before: {stack}")

            if tag_name in ['if', 'for', 'block', 'with']:
                stack.append((tag_name, line_num))
            elif tag_name in ['endif', 'endfor', 'endblock', 'endwith']:
                if not stack:
                    print(f"ERROR: Found {tag_name} at line {line_num} but stack is empty!")
                    return
                last_tag, last_line = stack[-1]
                expected_close = 'end' + last_tag
                if tag_name == expected_close:
                    stack.pop()
                else:
                    print(f"ERROR: Found {tag_name} at line {line_num}, expected {expected_close} closing {last_tag} from line {last_line}")
                    # Don't return, keep going to see more info? No, structure is broken.
                    # return 
            elif tag_name in ['elif', 'else']:
                if not stack:
                    print(f"ERROR: Found {tag_name} at line {line_num} but stack is empty (orphaned)!")
                    return
                last_tag, last_line = stack[-1]
                if last_tag != 'if':
                    print(f"ERROR: Found {tag_name} at line {line_num} inside {last_tag} block start at line {last_line}. {tag_name} is valid only inside 'if'.")
                    return
        
        # Stop a bit after 214
        if line_num == 220:
            break

    print("\nFinal Stack (if verification incomplete):")
    for item in stack:
        print(item)

if __name__ == "__main__":
    analyze_tags()
