import os

views_path = 'clubs/views.py'
print_bracket_path = 'print_bracket_view.py'

with open(views_path, 'rb') as f:
    content = f.read()

# We need to find the end of the original file
# The original file ended with:
#         'total_matches': len(scheduled_matches),
#     })

search_str = b"'total_matches': len(scheduled_matches),\r\n    })\r\n"
idx = content.find(search_str)

if idx == -1:
    search_str = b"'total_matches': len(scheduled_matches),\n    })\n"
    idx = content.find(search_str)

if idx == -1:
    search_str = b"'total_matches': len(scheduled_matches),\n    })"
    idx = content.find(search_str)

if idx != -1:
    end_idx = idx + len(search_str)
    original_content = content[:end_idx].decode('utf-8')
    
    with open(print_bracket_path, 'r', encoding='utf-8') as f:
        append_content = f.read()
        
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(original_content + "\n\n" + append_content)
    print("Fixed views.py successfully.")
else:
    print("Could not find the end of the original file.")
