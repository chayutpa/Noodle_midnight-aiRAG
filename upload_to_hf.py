#!/usr/bin/env python3
"""
Script to upload all files to Hugging Face repository
"""
import os
from pathlib import Path
from huggingface_hub import HfApi, login

# Repository details
REPO_ID = "Yut15346/MilkyWay-demi"
LOCAL_DIR = "/workspaces/MilkyWay-aiRAG/MilkyWay-demi"

def upload_files():
    """Upload all files to Hugging Face repository"""
    
    # Check if .env file exists and has HF token
    env_file = "/workspaces/MilkyWay-aiRAG/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('HF_TOKEN'):
                    token = line.split('=')[1].strip()
                    if token:
                        api = HfApi(token=token)
                        break
    else:
        # Try to get token from local git credentials or environment
        api = HfApi()
    
    print(f"Uploading files to {REPO_ID}...")
    
    # Iterate through all files in the directory
    local_path = Path(LOCAL_DIR)
    
    files_uploaded = 0
    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            # Skip git-related files
            if '.git' in file_path.parts:
                continue
            
            # Get relative path for the repo
            relative_path = file_path.relative_to(local_path)
            
            try:
                print(f"Uploading: {relative_path}")
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=str(relative_path),
                    repo_id=REPO_ID,
                    repo_type="model"
                )
                files_uploaded += 1
            except Exception as e:
                print(f"Error uploading {relative_path}: {e}")
    
    print(f"\nUpload complete! {files_uploaded} files uploaded to {REPO_ID}")

if __name__ == "__main__":
    upload_files()
