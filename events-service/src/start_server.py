#!/usr/bin/env python3
"""
Events Service Startup Script
"""
import os
import sys
import subprocess

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Regenerate proto files with correct imports
proto_dir = os.path.join(os.path.dirname(current_dir), 'proto')
proto_file = os.path.join(proto_dir, 'events.proto')

print("Regenerating proto files...")
try:
    subprocess.run([
        'python', '-m', 'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={current_dir}',
        f'--grpc_python_out={current_dir}',
        proto_file
    ], check=True)
    print("Proto files generated successfully")
except subprocess.CalledProcessError as e:
    print(f"Error generating proto files: {e}")

# Fix imports in generated files
events_pb2_grpc_file = os.path.join(current_dir, 'events_pb2_grpc.py')
if os.path.exists(events_pb2_grpc_file):
    with open(events_pb2_grpc_file, 'r') as f:
        content = f.read()
    
    # Fix the import
    content = content.replace('import events_pb2 as events__pb2', 'import events_pb2 as events__pb2')
    
    with open(events_pb2_grpc_file, 'w') as f:
        f.write(content)
    print("Fixed imports in events_pb2_grpc.py")

# Now start the server
print("Starting Events Service...")
from events_service import serve

if __name__ == '__main__':
    serve()