import os
import subprocess
import logging
import shlex
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TerminalResult:
    """Result from terminal command execution"""
    output: str
    error: str
    exit_code: int

class TerminalService:
    """Service for terminal operations"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def execute_command(self, command: str, session_id: str = 'default') -> TerminalResult:
        """Execute command in terminal"""
        try:
            # Initialize session if it doesn't exist
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'cwd': self.workspace_dir,
                    'env': os.environ.copy()
                }
            
            session = self.sessions[session_id]
            
            # Handle built-in commands
            if command.strip().startswith('cd '):
                return self._handle_cd_command(command, session)
            elif command.strip() == 'pwd':
                return TerminalResult(
                    output=session['cwd'] + '\n',
                    error='',
                    exit_code=0
                )
            elif command.strip() == 'clear':
                return TerminalResult(
                    output='\033[2J\033[H',  # ANSI clear screen
                    error='',
                    exit_code=0
                )
            
            # Execute command
            args = []
            try:
                # Split command safely
                args = shlex.split(command)
                
                # Security: prevent dangerous commands
                dangerous_commands = ['rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs']
                if args and args[0] in dangerous_commands:
                    return TerminalResult(
                        output='',
                        error=f'Command "{args[0]}" is not allowed for security reasons\n',
                        exit_code=1
                    )
                
                result = subprocess.run(
                    args,
                    cwd=session['cwd'],
                    env=session['env'],
                    capture_output=True,
                    text=True,
                    timeout=30  # 30 second timeout
                )
                
                return TerminalResult(
                    output=result.stdout,
                    error=result.stderr,
                    exit_code=result.returncode
                )
                
            except subprocess.TimeoutExpired:
                return TerminalResult(
                    output='',
                    error='Command timed out after 30 seconds\n',
                    exit_code=124
                )
            except FileNotFoundError:
                return TerminalResult(
                    output='',
                    error=f'Command not found: {args[0] if args else command}\n',
                    exit_code=127
                )
            except Exception as e:
                return TerminalResult(
                    output='',
                    error=f'Error executing command: {str(e)}\n',
                    exit_code=1
                )
                
        except Exception as e:
            logging.error(f"Terminal execution error: {e}")
            return TerminalResult(
                output='',
                error=f'Terminal error: {str(e)}\n',
                exit_code=1
            )
    
    def _handle_cd_command(self, command: str, session: Dict[str, Any]) -> TerminalResult:
        """Handle cd command"""
        try:
            parts = command.strip().split(None, 1)
            if len(parts) == 1:
                # cd with no arguments - go to workspace root
                new_path = self.workspace_dir
                path_name = "~"
            else:
                path = parts[1]
                path_name = path
                if os.path.isabs(path):
                    # Absolute path - ensure it's within workspace
                    new_path = os.path.normpath(path)
                    if not new_path.startswith(self.workspace_dir):
                        return TerminalResult(
                            output='',
                            error='Access denied: path outside workspace\n',
                            exit_code=1
                        )
                else:
                    # Relative path
                    new_path = os.path.normpath(os.path.join(session['cwd'], path))
                    if not new_path.startswith(self.workspace_dir):
                        return TerminalResult(
                            output='',
                            error='Access denied: path outside workspace\n',
                            exit_code=1
                        )
            
            if not os.path.exists(new_path):
                return TerminalResult(
                    output='',
                    error=f'No such file or directory: {path_name}\n',
                    exit_code=1
                )
            
            if not os.path.isdir(new_path):
                return TerminalResult(
                    output='',
                    error=f'Not a directory: {path_name}\n',
                    exit_code=1
                )
            
            session['cwd'] = new_path
            return TerminalResult(
                output='',
                error='',
                exit_code=0
            )
            
        except Exception as e:
            return TerminalResult(
                output='',
                error=f'cd error: {str(e)}\n',
                exit_code=1
            )
    
    def resize_terminal(self, session_id: str, rows: int, cols: int) -> None:
        """Resize terminal (placeholder for future implementation)"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'cwd': self.workspace_dir,
                'env': os.environ.copy()
            }
        
        # Store terminal dimensions for future use
        self.sessions[session_id]['rows'] = rows
        self.sessions[session_id]['cols'] = cols
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'cwd': self.workspace_dir,
                'env': os.environ.copy()
            }
        
        return self.sessions[session_id].copy()
