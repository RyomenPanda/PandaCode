import os
import subprocess
import logging
from typing import List, Optional
from models import GitStatus

class GitService:
    """Service for Git operations"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
    
    def _run_git_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run git command in workspace directory"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            logging.error(f"Error running git command {command}: {e}")
            raise
    
    def is_git_repo(self) -> bool:
        """Check if workspace is a git repository"""
        try:
            result = self._run_git_command(['status'])
            return result.returncode == 0
        except:
            return False
    
    def init_repo(self) -> None:
        """Initialize git repository"""
        try:
            result = self._run_git_command(['init'])
            if result.returncode != 0:
                raise RuntimeError(f"Failed to initialize git repo: {result.stderr}")
        except Exception as e:
            logging.error(f"Error initializing git repo: {e}")
            raise
    
    def get_status(self) -> GitStatus:
        """Get git repository status"""
        try:
            if not self.is_git_repo():
                # Initialize repo if it doesn't exist
                self.init_repo()
            
            # Get current branch
            branch_result = self._run_git_command(['branch', '--show-current'])
            branch = branch_result.stdout.strip() or 'main'
            
            # Get status
            status_result = self._run_git_command(['status', '--porcelain'])
            
            modified_files = []
            staged_files = []
            untracked_files = []
            
            for line in status_result.stdout.splitlines():
                if len(line) < 3:
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                
                if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                    staged_files.append(file_path)
                elif status_code[1] in ['M', 'D']:
                    modified_files.append(file_path)
                elif status_code == '??':
                    untracked_files.append(file_path)
            
            return GitStatus(
                branch=branch,
                modified_files=modified_files,
                staged_files=staged_files,
                untracked_files=untracked_files
            )
        except Exception as e:
            logging.error(f"Error getting git status: {e}")
            raise
    
    def get_diff(self, file_path: Optional[str] = None) -> str:
        """Get git diff for file or all files"""
        try:
            if not self.is_git_repo():
                return "Not a git repository"
            
            command = ['diff']
            if file_path:
                command.append(file_path)
            
            result = self._run_git_command(command)
            return result.stdout
        except Exception as e:
            logging.error(f"Error getting git diff: {e}")
            raise
    
    def add_files(self, files: List[str]) -> None:
        """Add files to staging area"""
        try:
            if not self.is_git_repo():
                raise RuntimeError("Not a git repository")
            
            for file_path in files:
                result = self._run_git_command(['add', file_path])
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to add file {file_path}: {result.stderr}")
        except Exception as e:
            logging.error(f"Error adding files: {e}")
            raise
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> None:
        """Commit changes to repository"""
        try:
            if not self.is_git_repo():
                raise RuntimeError("Not a git repository")
            
            # Add files if specified
            if files:
                self.add_files(files)
            else:
                # Add all modified files
                result = self._run_git_command(['add', '-A'])
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to add files: {result.stderr}")
            
            # Commit changes
            result = self._run_git_command(['commit', '-m', message])
            if result.returncode != 0:
                if 'nothing to commit' in result.stdout:
                    raise RuntimeError("Nothing to commit")
                else:
                    raise RuntimeError(f"Failed to commit: {result.stderr}")
        except Exception as e:
            logging.error(f"Error committing changes: {e}")
            raise
    
    def push_changes(self, remote: str = 'origin', branch: Optional[str] = None) -> None:
        """Push changes to remote repository"""
        try:
            if not self.is_git_repo():
                raise RuntimeError("Not a git repository")
            
            # Get current branch if not specified
            if not branch:
                branch_result = self._run_git_command(['branch', '--show-current'])
                branch = branch_result.stdout.strip() or 'main'
            
            # Push changes
            result = self._run_git_command(['push', remote, branch])
            if result.returncode != 0:
                # Try to set upstream if it fails
                result = self._run_git_command(['push', '-u', remote, branch])
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to push: {result.stderr}")
        except Exception as e:
            logging.error(f"Error pushing changes: {e}")
            raise
    
    def pull_changes(self, remote: str = 'origin', branch: Optional[str] = None) -> None:
        """Pull changes from remote repository"""
        try:
            if not self.is_git_repo():
                raise RuntimeError("Not a git repository")
            
            # Get current branch if not specified
            if not branch:
                branch_result = self._run_git_command(['branch', '--show-current'])
                branch = branch_result.stdout.strip() or 'main'
            
            # Pull changes
            result = self._run_git_command(['pull', remote, branch])
            if result.returncode != 0:
                raise RuntimeError(f"Failed to pull: {result.stderr}")
        except Exception as e:
            logging.error(f"Error pulling changes: {e}")
            raise
