# PandaCode IDE

PandaCode is a modern, AI-powered IDE that provides both a native desktop application and web-based interface for seamless code development <cite/>. Built with Python and PyQt6 for the desktop client, it integrates Google Gemini AI for intelligent code assistance.

## Features

### 🖥️ Dual Interface Support
- **Desktop Application**: Native PyQt6 interface with full IDE capabilities [1](#0-0) 
- **Web Interface**: Browser-based access through Flask and SocketIO <cite/>

### 🤖 AI-Powered Development
- **Intelligent Chat**: Context-aware AI assistance using Google Gemini [2](#0-1) 
- **Code Refactoring**: AI-driven code improvements with custom instructions [3](#0-2) 
- **Test Generation**: Automated unit test creation for your code [4](#0-3) 

### 📁 File Management
- **Workspace Security**: All operations constrained to designated workspace directory [5](#0-4) 
- **Multi-Language Support**: Syntax detection for 20+ programming languages [6](#0-5) 
- **File Explorer**: Integrated file browser with double-click editing [7](#0-6) 

### 🔧 Development Tools
- **Integrated Terminal**: Execute commands directly within the IDE [8](#0-7) 
- **Git Integration**: Built-in version control with status tracking [9](#0-8) 
- **Syntax Highlighting**: Python syntax highlighting with extensible architecture [10](#0-9) 

## Installation

### Prerequisites
- Python 3.8+
- PyQt6
- Google Gemini API key

### Setup
1. Clone the repository:
```bash
git clone https://github.com/RyomenPanda/PandaCode.git
cd PandaCode
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AI service:
   - Create a `config.json` file in the root directory [11](#0-10) 
   - Add your Gemini API key:
   ```json
   {
     "gemini_api_key": "your_api_key_here"
   }
   ```

4. Run the desktop application:
```bash
python app.py
```

## Architecture

PandaCode follows a service-oriented architecture with shared business logic between desktop and web interfaces <cite/>:

- **FileService**: Workspace and file operations [12](#0-11) 
- **AIService**: Google Gemini integration for code assistance [13](#0-12) 
- **GitService**: Version control operations [14](#0-13) 
- **TerminalService**: Command execution within workspace [15](#0-14) 

## Usage

### Desktop Application
Launch the desktop app and use the integrated file explorer, editor, terminal, and AI chat panels [16](#0-15) . The AI assistant can help with code refactoring, test generation, and general programming questions.

### AI Features
- **Chat**: Ask questions about your code with automatic context inclusion [17](#0-16) 
- **Refactor**: Select code and provide refactoring instructions [18](#0-17) 
- **Generate Tests**: Automatically create unit tests for your functions [4](#0-3) 

## Configuration

Settings are managed through the Settings dialog accessible from the menu [19](#0-18) . The configuration system uses JSON files for persistent storage and environment variables for runtime settings [20](#0-19) .

## Contributing

PandaCode welcomes contributions! The modular service architecture makes it easy to extend functionality or add new client interfaces.
