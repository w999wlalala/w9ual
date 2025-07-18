import subprocess
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import os

REPO_URL = "https://github.com/w999wlalala/w9ual"

# Add current directory as a safe git directory (for CI/CD like GitHub Actions)
try:
    subprocess.run([
        'git', 'config', '--global', '--add', 'safe.directory', os.getcwd()
    ], check=True)
except Exception as e:
    print(f"Warning: Could not add safe.directory: {e}")

def github_cli_login(token):
    """
    Authenticate GitHub CLI using the provided token
    """
    try:
        # Method 1: Set environment variable (preferred for GitHub Actions)
        import os
        os.environ['GITHUB_TOKEN'] = token
        print("GitHub token set in environment")
        
        # Method 2: Use gh auth login with token
        auth_cmd = ['gh', 'auth', 'login', '--with-token']
        auth_result = subprocess.run(auth_cmd, input=token, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if auth_result.returncode == 0:
            print("GitHub CLI authenticated successfully with token")
        else:
            print(f"GitHub CLI auth warning: {auth_result.stderr}")
            print("Continuing with environment token...")
        
        # Verify authentication
        status_cmd = ['gh', 'auth', 'status']
        status_result = subprocess.run(status_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if status_result.returncode == 0:
            print("GitHub CLI authentication verified")
            return True
        else:
            print("GitHub CLI authentication status unclear, but token is set")
            return True
            
    except Exception as e:
        print(f"Error during GitHub CLI authentication: {e}")
        return False

def get_commit_url(commit_hash):
    # Return GitHub commit URL
    return f"{REPO_URL}/commit/{commit_hash}"

def get_pr_url_for_commit(commit_hash):
    try:
        # First, try to get the branch name for this commit
        branch_cmd = ['git', 'branch', '-r', '--contains', commit_hash]
        branch_result = subprocess.run(branch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if branch_result.returncode == 0:
            branches = []
            for line in branch_result.stdout.strip().split('\n'):
                if line.strip() and 'origin/' in line:
                    # Extract branch name after 'origin/'
                    branch = line.strip().replace('origin/', '').strip()
                    if branch and branch != 'HEAD':
                        branches.append(branch)
            
            # Try to find PRs for each branch using gh pr list
            for branch in branches:
                if branch == 'main' or branch == 'master':
                    continue  # Skip main branches
                    
                # Use gh pr list to find PRs for this branch
                gh_cmd = ['gh', 'pr', 'list', '--head', branch, '--state', 'all', '--json', 'number,headRefName']
                gh_result = subprocess.run(gh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if gh_result.returncode == 0 and gh_result.stdout.strip():
                    import json
                    try:
                        prs = json.loads(gh_result.stdout)
                        if prs and len(prs) > 0:
                            pr_number = prs[0]['number']
                            return f"{REPO_URL}/pull/{pr_number}"
                    except json.JSONDecodeError:
                        continue
        
        # Fallback: Search for merge commits that include this commit and extract PR number
        log_cmd = [
            'git', 'log', '--merges', '--pretty=format:%H|%s', '--ancestry-path', f'{commit_hash}..HEAD'
        ]
        result = subprocess.run(log_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return ""
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                # Typical merge commit message: Merge pull request #20 from ...
                match = re.search(r'Merge pull request #(\d+)', parts[1])
                if match:
                    pr_number = match.group(1)
                    return f"{REPO_URL}/pull/{pr_number}"
        return ""
        
    except Exception as e:
        print(f"Warning: Could not get PR URL for commit {commit_hash}: {e}")
        return ""

def get_yesterday_git_log(TOKEN):
    # Use Hong Kong timezone (UTC+8)
    hk_now = datetime.utcnow() + timedelta(hours=8)
    yesterday = (hk_now - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Authenticate GitHub CLI first
    print("Authenticating GitHub CLI...")
    github_cli_login(TOKEN)
    
    # Configure git to use the token for authentication
    try:
        # Set up credential helper to use the token
        subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'], check=True)
        
        # Configure the remote URL with token for authentication
        remote_url_with_token = REPO_URL.replace('https://', f'https://{TOKEN}@')
        subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url_with_token], check=True)
        
    except Exception as e:
        print(f"Warning: Could not configure git authentication: {e}")
    
    # Fetch from remote to get the latest remote commits
    print("Fetching from remote repository with authentication...")
    fetch_cmd = ['git', 'fetch', '--all']
    fetch_result = subprocess.run(fetch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if fetch_result.returncode != 0:
        print(f"Warning: Could not fetch from remote: {fetch_result.stderr}")
    else:
        print("Successfully fetched from remote")
    
    # Get commits for yesterday from 08:00am to 23:59pm in Hong Kong timezone from ALL branches (including remote branches)
    # Use --since and --until with timezone offset
    start_time = f"{yesterday}T08:00:00+08:00"
    end_time = f"{yesterday}T23:59:59+08:00"
    
    cmd = [
        'git', 'log', '--all', '--remotes', '--since', start_time, '--until', end_time,
        '--pretty=format:%h|%an|%ae|%s'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return f'Error running git log: {result.stderr}'
    lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
    output = []
    output.append(f"Git usage for {yesterday} (Hong Kong timezone UTC+8, including remote commits, 08:00-23:59):")
    output.append(f"Total commits: {len(lines)}")
    committers = []
    commit_branch_map = {}
    commits_by_committer = defaultdict(list)
    for line in lines:
        parts = line.split('|')
        if len(parts) >= 1 and parts[0]:
            # Get the original branch where this commit was first made
            # Try multiple methods to find the most accurate branch name (including remote branches)
            original_branch = None
            
            # Method 1: Try git name-rev to find the original branch (including remotes)
            name_rev_cmd = ['git', 'name-rev', '--name-only', '--refs=refs/heads/*', '--refs=refs/remotes/*', parts[0]]
            name_rev_result = subprocess.run(name_rev_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if name_rev_result.returncode == 0 and name_rev_result.stdout.strip():
                branch_name = name_rev_result.stdout.strip()
                # Clean up the branch name (remove ~N and ^N suffixes)
                if '~' not in branch_name and '^' not in branch_name and branch_name != 'undefined':
                    original_branch = branch_name
            
            # Method 2: If method 1 failed, try to find which branch contains this commit (including remote branches)
            if not original_branch:
                branch_cmd = ['git', 'branch', '-a', '--contains', parts[0]]
                branch_result = subprocess.run(branch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if branch_result.returncode == 0:
                    branches = branch_result.stdout.strip().replace('* ', '').replace('  ', '').split('\n')
                    branches = [b.strip() for b in branches if b.strip()]
                    # Prefer remote branches or non-current branch if available
                    current_branch_cmd = ['git', 'branch', '--show-current']
                    current_result = subprocess.run(current_branch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    current_branch = current_result.stdout.strip() if current_result.returncode == 0 else ''
                    
                    # Find a remote branch first, then non-current local branch
                    for branch in branches:
                        if branch.startswith('remotes/') and branch:
                            original_branch = branch
                            break
                    
                    # If no remote branch found, find a local branch that's not the current branch
                    if not original_branch:
                        for branch in branches:
                            if branch != current_branch and branch and not branch.startswith('remotes/'):
                                original_branch = branch
                                break
                    
                    # If no other branch found, use the first available branch
                    if not original_branch and branches:
                        original_branch = branches[0]
            
            # Store the result
            commit_branch_map[parts[0]] = [original_branch] if original_branch else ['unknown']
        if len(parts) >= 3:
            committer = f"{parts[1]} <{parts[2]}>"
            committers.append(committer)
            if len(parts) >= 4:
                # Get files changed for this commit - try multiple methods
                files = []
                
                # Method 1: Try git diff-tree
                files_cmd = ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', parts[0]]
                files_result = subprocess.run(files_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if files_result.returncode == 0 and files_result.stdout.strip():
                    files = [f for f in files_result.stdout.strip().split('\n') if f.strip()]
                
                # Method 2: If method 1 failed, try git show
                if not files:
                    files_cmd = ['git', 'show', '--name-only', '--pretty=format:', parts[0]]
                    files_result = subprocess.run(files_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if files_result.returncode == 0 and files_result.stdout.strip():
                        files = [f for f in files_result.stdout.strip().split('\n') if f.strip()]
                
                # Get PR URL if available, otherwise use commit URL
                pr_url = get_pr_url_for_commit(parts[0])
                commit_url = get_commit_url(parts[0])
                commits_by_committer[committer].append({
                    'hash': parts[0],
                    'branches': commit_branch_map.get(parts[0], []),
                    'message': parts[3],
                    'files': files,
                    'pr_url': pr_url,
                    'commit_url': commit_url
                })
    committer_counts = Counter(committers)
    output.append(f"Unique committers: {len(committer_counts)}")
    output.append("Committer summary:")
    for committer, count in committer_counts.items():
        output.append(f"    {committer}: {count} commit(s)")
        for commit in commits_by_committer[committer]:
            branch_str = ', '.join(commit['branches']) if commit['branches'] else 'N/A'
            output.append(f"        Commits {commit['hash']}: on branch(es): {branch_str}: {commit['message']}")
            if commit['pr_url']:
                output.append(f"            PR: {commit['pr_url']}")
            output.append(f"            Files changed:")
            if commit['files']:
                for f in commit['files']:
                    output.append(f"                {f}")
            else:
                output.append(f"                (No files detected)")
    return '\n'.join(output)

# if __name__ == "__main__":
#     TOKEN = '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'
#     print(get_yesterday_git_log(TOKEN))
