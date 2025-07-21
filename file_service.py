import os
import shutil
import mimetypes
from typing import List, Dict, Any
import logging

class FileService:
    """Service for file system operations"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'plaintext',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bash': 'shell',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'objective-c',
            '.pl': 'perl',
            '.lua': 'lua',
            '.dart': 'dart'
        }
    
    def _get_full_path(self, relative_path: str) -> str:
        """Get full path from relative path"""
        if not relative_path:
            return self.workspace_dir
        
        # Normalize path and ensure it's within workspace
        full_path = os.path.normpath(os.path.join(self.workspace_dir, relative_path))
        
        # Security check: ensure path is within workspace
        if not full_path.startswith(self.workspace_dir):
            raise ValueError("Path outside workspace not allowed")
        
        return full_path
    
    def list_files(self, path: str = '') -> List[Dict[str, Any]]:
        """List files and directories"""
        try:
            full_path = self._get_full_path(path)
            
            if not os.path.exists(full_path):
                return []
            
            items = []
            for item in sorted(os.listdir(full_path)):
                # Skip hidden files and directories
                if item.startswith('.') and item not in ['.git', '.gitignore']:
                    continue
                
                item_path = os.path.join(full_path, item)
                relative_path = os.path.relpath(item_path, self.workspace_dir)
                
                is_dir = os.path.isdir(item_path)
                size = None if is_dir else os.path.getsize(item_path)
                modified_time = os.path.getmtime(item_path)
                
                items.append({
                    'name': item,
                    'path': relative_path,
                    'is_directory': is_dir,
                    'size': size,
                    'modified_time': modified_time
                })
            
            return items
        except Exception as e:
            logging.error(f"Error listing files: {e}")
            raise
    
    def read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            full_path = self._get_full_path(file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if os.path.isdir(full_path):
                raise ValueError(f"Path is a directory: {file_path}")
            
            # Check if file is binary
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type and mime_type.startswith('image/'):
                raise ValueError(f"Cannot read binary file: {file_path}")
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            raise
    
    def write_file(self, file_path: str, content: str) -> None:
        """Write file content"""
        try:
            full_path = self._get_full_path(file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Error writing file {file_path}: {e}")
            raise
    
    def create_file(self, file_path: str) -> None:
        """Create new file"""
        try:
            full_path = self._get_full_path(file_path)
            
            if os.path.exists(full_path):
                raise ValueError(f"File already exists: {file_path}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Create empty file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write('')
        except Exception as e:
            logging.error(f"Error creating file {file_path}: {e}")
            raise
    
    def create_directory(self, dir_path: str) -> None:
        """Create new directory"""
        try:
            full_path = self._get_full_path(dir_path)
            
            if os.path.exists(full_path):
                raise ValueError(f"Directory already exists: {dir_path}")
            
            os.makedirs(full_path)
        except Exception as e:
            logging.error(f"Error creating directory {dir_path}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> None:
        """Delete file or directory"""
        try:
            full_path = self._get_full_path(file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")
            raise
    
    def rename_file(self, old_path: str, new_path: str) -> None:
        """Rename file or directory"""
        try:
            old_full_path = self._get_full_path(old_path)
            new_full_path = self._get_full_path(new_path)
            
            if not os.path.exists(old_full_path):
                raise FileNotFoundError(f"File not found: {old_path}")
            
            if os.path.exists(new_full_path):
                raise ValueError(f"Destination already exists: {new_path}")
            
            # Create directory for new path if needed
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
            
            os.rename(old_full_path, new_full_path)
        except Exception as e:
            logging.error(f"Error renaming file {old_path} to {new_path}: {e}")
            raise
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        _, ext = os.path.splitext(file_path.lower())
        return self.language_map.get(ext, 'plaintext')
    
    def get_project_files(self, max_files: int = 100) -> List[str]:
        """Get list of project files for AI context"""
        try:
            files = []
            for root, dirs, filenames in os.walk(self.workspace_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']
                
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, self.workspace_dir)
                    files.append(relative_path)
                    
                    if len(files) >= max_files:
                        break
                
                if len(files) >= max_files:
                    break
            
            return files
        except Exception as e:
            logging.error(f"Error getting project files: {e}")
            return []
