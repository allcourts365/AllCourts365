import os

filepath = 'clubs/views.py'
with open(filepath, 'rb') as f:
    content = f.read()

# Remove all null bytes
content = content.replace(b'\x00', b'')

with open(filepath, 'wb') as f:
    f.write(content)
    
print("Fixed views.py by removing null bytes!")
