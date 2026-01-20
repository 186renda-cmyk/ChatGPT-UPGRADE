import os
import re
import posixpath

def fix_paths():
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files to process.")

    # Regex to find relative hrefs
    # Capture group 1: quote (' or ")
    # Capture group 2: the link
    # Negative lookahead to exclude absolute paths, protocols, anchors, etc.
    # Note: We match the opening quote, then the content, then the closing quote is handled by backreference \1
    pattern = re.compile(r'href=(["\'])(?!(?:/|http:|https:|#|mailto:|tel:|javascript:|data:))(.+?)\1')

    for file_path in html_files:
        # Get directory of current file relative to script root
        # file_path is like ./blog/index.html
        # rel_dir would be blog
        rel_path = os.path.relpath(file_path, '.')
        rel_dir = os.path.dirname(rel_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        def replacement(match):
            quote = match.group(1)
            original_link = match.group(2)
            
            # Handle query params and fragments
            if '#' in original_link:
                path_part, fragment = original_link.split('#', 1)
                fragment = '#' + fragment
            elif '?' in original_link:
                path_part, query = original_link.split('?', 1)
                fragment = '?' + query
            else:
                path_part = original_link
                fragment = ''

            # Normalize path
            # Combine current directory with linked path
            # posixpath.join handles '/' correctly as separator
            full_path = posixpath.join('/', rel_dir, path_part)
            # Normalize to resolve .. and .
            full_path = posixpath.normpath(full_path)
            
            # Ensure it starts with / (normpath might strip it if it resolves to relative?)
            # posixpath.normpath('/foo') -> '/foo'
            # posixpath.normpath('/../foo') -> '/foo'
            if not full_path.startswith('/'):
                full_path = '/' + full_path

            # Apply Clean URL rules
            if full_path.endswith('/index.html'):
                full_path = full_path[:-10] # remove index.html
                # Now it ends with /, which is good for index
                if not full_path.endswith('/'): 
                     # If it was just /index.html, it becomes /, fine.
                     # If /blog/index.html, it becomes /blog/, fine.
                     pass
            elif full_path.endswith('.html'):
                full_path = full_path[:-5] # remove .html
            
            # Reattach fragment/query
            new_link = full_path + fragment
            
            if new_link != original_link:
                # print(f"Fixing in {rel_path}: {original_link} -> {new_link}")
                pass
                
            return f'href={quote}{new_link}{quote}'

        new_content = pattern.sub(replacement, content)
        
        if new_content != content:
            print(f"Updating {file_path}...")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

    print("All files processed.")

if __name__ == "__main__":
    fix_paths()
