# BSM Core Module

The core module contains the essential business logic and service layer components of the BSM application.

## Components

### ai_providers.py
**Purpose**: Provides abstraction layer for AI service integration

**Key Classes**:
- `AIProvider`: Abstract base class defining the interface for all AI providers
- `OpenAIProvider`: Integration with OpenAI's GPT models
- `ClaudeProvider`: Integration with Anthropic's Claude
- `OllamaProvider`: Integration with local Ollama models
- `AIProviderManager`: Orchestrates multiple providers with fallback support

**Usage Example**:
```python
from bsm.core.ai_providers import AIProviderManager, OpenAIProvider

manager = AIProviderManager()
manager.add_provider('openai', OpenAIProvider(api_key))

result = await manager.analyze_with_fallback(
    text="Sample text to analyze",
    attitude_mode="balanced",
    primary_provider="openai"
)
```

**Key Features**:
- Automatic fallback to alternative providers
- Three attitude modes: argumentative, balanced, helpful
- Structured JSON response format
- Async/await support

### database.py
**Purpose**: Manages persistent storage of analysis history

**Key Classes**:
- `DatabaseManager`: SQLite database interface

**Database Schema**:
```sql
analyses:
  - id: INTEGER PRIMARY KEY
  - content_hash: TEXT UNIQUE (SHA-256 of text+attitude)
  - original_text: TEXT
  - source_type: TEXT ('selection', 'screenshot')
  - analysis_result: TEXT (JSON)
  - attitude_mode: TEXT
  - llm_provider: TEXT
  - confidence_score: REAL
  - created_at: TIMESTAMP
  - updated_at: TIMESTAMP

tags:
  - id: INTEGER PRIMARY KEY
  - analysis_id: INTEGER FOREIGN KEY
  - tag: TEXT
```

**Key Features**:
- Content deduplication via hashing
- Full-text search capability
- Tag support for organization
- Automatic timestamp management

### settings.py
**Purpose**: Centralized configuration management

**Key Classes**:
- `SettingsManager`: Handles all application settings

**Configuration Structure**:
```yaml
api_keys:
  openai: <encrypted>
  claude: <encrypted>
llm_provider: openai
ollama_endpoint: http://localhost:11434
ollama_model: llama2
attitude_mode: balanced
global_hotkey: ctrl+shift+b
database_path: ~/.bsm/analyses.db
window_position: {x, y, width, height}
auto_save_results: true
show_confidence_score: true
enable_screenshot_ocr: true
```

**Security Features**:
- Fernet encryption for API keys
- Unique encryption key per installation
- Secure key storage in separate file

## Design Patterns

1. **Abstract Factory**: AI provider creation
2. **Strategy Pattern**: Different analysis attitudes
3. **Singleton**: Settings and database managers
4. **Repository Pattern**: Database access layer

## Dependencies

- `openai`: OpenAI API client
- `anthropic`: Claude API client
- `aiohttp`: Async HTTP requests for Ollama
- `cryptography`: Fernet encryption
- `pyyaml`: Configuration file handling
- `sqlite3`: Database operations

## Error Handling

- All methods include try-catch blocks
- Graceful degradation for provider failures
- User-friendly error messages
- Detailed logging for debugging

## Future Improvements

1. **Caching Layer**: Add response caching to reduce API calls
2. **Connection Pooling**: Implement database connection pooling
3. **Retry Logic**: Add exponential backoff for transient failures
4. **Metrics**: Add performance monitoring
5. **Validation**: Stronger input validation and sanitization
