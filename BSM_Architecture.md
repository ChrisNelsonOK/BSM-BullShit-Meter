# BSM (BullShit Meter) - System Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Overview](#component-overview)
4. [Data Flow](#data-flow)
5. [Module Responsibilities](#module-responsibilities)
6. [Technical Decisions](#technical-decisions)
7. [Security Architecture](#security-architecture)
8. [Performance Considerations](#performance-considerations)

## Overview

BSM is a desktop application built with PyQt6 that provides AI-powered fact-checking and counter-argument generation. The application runs as a system tray application and can be triggered via global hotkeys to analyze text from various sources.

### Key Technologies
- **Frontend**: PyQt6 (cross-platform desktop UI)
- **Backend**: Python 3.8+
- **AI Integration**: OpenAI, Claude (Anthropic), Ollama
- **Database**: SQLite
- **OCR**: Tesseract
- **Security**: Cryptography (Fernet encryption)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐│
│  │System Tray  │  │Result Window│  │Settings     │  │Context     ││
│  │(QSystemTray)│  │(Markdown)   │  │Window       │  │Window      ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                         Application Core Layer                       │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐│
│  │BSMApplication│  │Analysis     │  │Hotkey       │  │Text        ││
│  │(Main App)   │  │Worker       │  │Manager      │  │Capture     ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                          Service Layer                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐│
│  │AI Provider  │  │Settings     │  │Database     │  │OCR         ││
│  │Manager      │  │Manager      │  │Manager      │  │Service     ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                          External Services                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐│
│  │OpenAI API   │  │Claude API   │  │Ollama       │  │Tesseract   ││
│  │             │  │             │  │(Local)      │  │OCR         ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Component Overview

### Core Components

1. **BSMApplication** (`bsm/main.py`)
   - Central application controller
   - Manages application lifecycle
   - Coordinates between UI and backend services
   - Handles system tray integration

2. **AI Provider System** (`bsm/core/ai_providers.py`)
   - Abstract base class for AI providers
   - Concrete implementations for OpenAI, Claude, and Ollama
   - Fallback mechanism for provider failures
   - Attitude mode support (argumentative, balanced, helpful)

3. **Settings Management** (`bsm/core/settings.py`)
   - YAML-based configuration
   - Encrypted API key storage using Fernet
   - User preferences management
   - Window position persistence

4. **Database Layer** (`bsm/core/database.py`)
   - SQLite database for analysis history
   - Content deduplication using SHA-256 hashing
   - Tag support for organization
   - Full-text search capabilities

### UI Components

1. **Result Window** (`bsm/ui/result_window.py`)
   - Markdown rendering using QWebEngineView
   - Dark theme with custom CSS
   - Copy functionality
   - Window position memory

2. **Settings Window** (`bsm/ui/settings_window.py`)
   - API key configuration
   - Provider selection
   - Hotkey customization
   - Theme preferences

3. **Context Window** (`bsm/ui/context_window.py`)
   - Additional context input
   - Analysis refinement
   - Re-analysis triggers

### Utility Components

1. **Hotkey Manager** (`bsm/utils/hotkey_manager.py`)
   - Cross-platform hotkey registration
   - Platform-specific implementations
   - Fallback mechanisms

2. **Text Capture** (`bsm/utils/text_capture.py`)
   - Clipboard monitoring
   - Selection capture
   - Screenshot OCR integration

## Data Flow

### Analysis Workflow

```
User Action (Hotkey/Menu)
         │
         ▼
Text Capture/Selection
         │
         ▼
Context Window (Optional)
         │
         ▼
Analysis Worker Thread
         │
         ├─────► AI Provider Manager
         │              │
         │              ├──► Primary Provider
         │              │
         │              └──► Fallback Providers
         │
         ▼
Result Processing
         │
         ├──► Database Storage
         │
         └──► Result Window Display
```

### Configuration Flow

```
Settings Window
      │
      ▼
Settings Manager
      │
      ├──► Encrypt Sensitive Data (API Keys)
      │
      └──► Save to YAML File
             │
             └──► Update Application State
```

## Module Responsibilities

### bsm/main.py
- **Primary Responsibility**: Application lifecycle management
- **Key Classes**: 
  - `BSMApplication`: Main application controller
  - `AnalysisWorker`: Background analysis thread
- **Dependencies**: All core modules
- **Threading**: Uses QThread for background operations

### bsm/core/ai_providers.py
- **Primary Responsibility**: AI service abstraction and integration
- **Key Classes**:
  - `AIProvider`: Abstract base class
  - `OpenAIProvider`: OpenAI GPT integration
  - `ClaudeProvider`: Anthropic Claude integration
  - `OllamaProvider`: Local LLM integration
  - `AIProviderManager`: Provider orchestration
- **Features**: Fallback support, attitude modes, JSON response parsing

### bsm/core/settings.py
- **Primary Responsibility**: Configuration management
- **Key Features**:
  - YAML-based storage
  - Fernet encryption for sensitive data
  - Default settings management
  - Type-safe getter/setter methods

### bsm/core/database.py
- **Primary Responsibility**: Data persistence
- **Key Features**:
  - SQLite database management
  - Content deduplication
  - Tag support
  - Search functionality
  - Migration support

### bsm/ui/result_window.py
- **Primary Responsibility**: Analysis result display
- **Key Features**:
  - Markdown rendering
  - Custom CSS theming
  - Copy functionality
  - Window state persistence

### bsm/ui/settings_window.py
- **Primary Responsibility**: User configuration interface
- **Key Features**:
  - Tabbed interface
  - API key management
  - Provider selection
  - Hotkey configuration

### bsm/utils/hotkey_manager.py
- **Primary Responsibility**: Global hotkey management
- **Key Features**:
  - Cross-platform support
  - Multiple backend support
  - Graceful fallback

### bsm/utils/text_capture.py
- **Primary Responsibility**: Text extraction from various sources
- **Key Features**:
  - Clipboard access
  - Selection capture
  - Screenshot OCR
  - Platform-specific implementations

## Technical Decisions

### Architecture Patterns
1. **MVC Pattern**: Separation of UI, business logic, and data
2. **Provider Pattern**: Abstraction for AI services
3. **Worker Thread Pattern**: Non-blocking UI operations
4. **Singleton Pattern**: Settings and database managers

### Technology Choices
1. **PyQt6**: Modern, cross-platform UI framework
2. **SQLite**: Lightweight, embedded database
3. **Cryptography**: Industry-standard encryption
4. **Markdown**: Rich text formatting with wide support

### Design Principles
1. **Privacy First**: Local data storage, encrypted secrets
2. **Extensibility**: Plugin-ready architecture
3. **Cross-Platform**: Consistent behavior across OS
4. **User Control**: Customizable settings and behavior

## Security Architecture

### Data Protection
1. **API Keys**: Encrypted using Fernet symmetric encryption
2. **Local Storage**: All data stored locally, no cloud sync
3. **Key Management**: Unique encryption key per installation

### Network Security
1. **HTTPS Only**: All API calls use TLS
2. **No Telemetry**: No usage data collection
3. **API Key Isolation**: Keys never logged or exposed

## Performance Considerations

### Threading Model
1. **Main Thread**: UI operations only
2. **Worker Threads**: AI analysis, OCR processing
3. **Async Operations**: Network calls use asyncio

### Resource Management
1. **Lazy Loading**: Components loaded on demand
2. **Connection Pooling**: Reuse database connections
3. **Memory Management**: Explicit cleanup of large objects

### Optimization Opportunities
1. **Response Caching**: Currently not implemented
2. **Batch Processing**: Single analysis at a time
3. **Database Indexing**: Basic indexes only

## Areas for Improvement

### Code Quality
- No formal error handling strategy
- Limited logging infrastructure
- Missing comprehensive unit tests
- No continuous integration

### Architecture
- Tight coupling between UI and business logic
- Manual thread management instead of async/await
- No dependency injection framework
- Limited extensibility for new providers

### Performance
- Synchronous database operations
- No response caching mechanism
- Full UI blocking during some operations
- Memory usage not optimized

### User Experience
- Limited keyboard navigation
- No undo/redo functionality
- Basic error messages
- No progress indicators for long operations
