import os
import subprocess
import shlex

CHUNK_SIZE = 4.5 * 1024 * 1024 * 1024  # 4.5 GB in bytes

def run_git_command(command):
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        return False
    return result.stdout

def get_staged_file_sizes():
    result = run_git_command("git diff --cached --name-only --diff-filter=A")
    files = {}
    if result:
        for filepath in result.splitlines():
            if os.path.isfile(filepath):
                files[filepath] = os.path.getsize(filepath)
    return files

def add_files_in_chunks(files, chunk_size):
    current_chunk = []
    current_size = 0

    for filepath, size in files.items():
        if current_size + size > chunk_size:
            yield current_chunk
            current_chunk = []
            current_size = 0
        current_chunk.append(filepath)
        current_size += size
    
    if current_chunk:
        yield current_chunk

def push_in_chunks(commit_message):
    files = get_staged_file_sizes()
    for chunk in add_files_in_chunks(files, CHUNK_SIZE):
        for filepath in chunk:
            run_git_command(f"git add \"{filepath}\"")
        run_git_command(f"git commit -m \"{commit_message}\" --allow-empty")
        run_git_command("git push origin HEAD")
    
    print("All chunks pushed successfully.")

def main():
    while True:
        command = input("Enter Git command (or 'exit' to quit): ").strip()
        
        if command.lower() == 'exit':
            break
        
        if command.startswith("git add "):
            run_git_command(command)
        
        elif command.startswith("git commit "):
            run_git_command(command)
        
        elif command == "git push":
            commit_message = input("Enter commit message for chunks: ")
            push_in_chunks(commit_message)
        
        else:
            print("Unsupported command. Please use 'git add', 'git commit', or 'git push'.")

if __name__ == "__main__":
    main()
