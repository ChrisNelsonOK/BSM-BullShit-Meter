"""
Plugin Framework for AI Providers.

This module provides a plugin system for dynamically loading AI providers
through Python entry points or direct module loading.
"""

import importlib
import importlib.metadata
import logging
import inspect
from typing import Dict, List, Optional, Type, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import sys

from bsm.core.ai_providers import AIProvider

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""
    name: str
    display_name: str
    description: str
    version: str
    author: str
    provider_class: Type[AIProvider]
    config_schema: Optional[Dict[str, Any]] = None
    enabled: bool = True
    source: str = "builtin"  # builtin, entrypoint, or file


class PluginManager:
    """Manages AI provider plugins."""
    
    ENTRY_POINT_GROUP = "bsm.ai_providers"
    
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.plugins: Dict[str, PluginInfo] = {}
        self._loaded_modules: Dict[str, Any] = {}
        
        # Load built-in providers first
        self._load_builtin_providers()
        
        # Load plugins from entry points
        self._load_entry_point_plugins()
        
        # Load plugins from user directory
        if settings_manager:
            self._load_user_plugins()
    
    def _load_builtin_providers(self):
        """Load built-in AI providers."""
        from bsm.core.ai_providers import OpenAIProvider, ClaudeProvider, OllamaProvider
        
        builtin_providers = [
            PluginInfo(
                name="openai",
                display_name="OpenAI",
                description="OpenAI GPT models for analysis",
                version="1.0.0",
                author="BSM Team",
                provider_class=OpenAIProvider,
                config_schema={
                    "api_key": {
                        "type": "string",
                        "description": "OpenAI API key",
                        "required": True,
                        "secret": True
                    }
                },
                source="builtin"
            ),
            PluginInfo(
                name="claude",
                display_name="Claude",
                description="Anthropic Claude for analysis",
                version="1.0.0",
                author="BSM Team",
                provider_class=ClaudeProvider,
                config_schema={
                    "api_key": {
                        "type": "string",
                        "description": "Anthropic API key",
                        "required": True,
                        "secret": True
                    }
                },
                source="builtin"
            ),
            PluginInfo(
                name="ollama",
                display_name="Ollama",
                description="Local Ollama models",
                version="1.0.0",
                author="BSM Team",
                provider_class=OllamaProvider,
                config_schema={
                    "endpoint": {
                        "type": "string",
                        "description": "Ollama API endpoint",
                        "default": "http://localhost:11434",
                        "required": False
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name to use",
                        "default": "llama2",
                        "required": False
                    }
                },
                source="builtin"
            )
        ]
        
        for provider_info in builtin_providers:
            self.plugins[provider_info.name] = provider_info
            logger.info(f"Loaded builtin provider: {provider_info.display_name}")
    
    def _load_entry_point_plugins(self):
        """Load plugins from Python entry points."""
        try:
            # For Python 3.10+
            if sys.version_info >= (3, 10):
                entry_points = importlib.metadata.entry_points(group=self.ENTRY_POINT_GROUP)
            else:
                # For Python 3.8-3.9
                entry_points = importlib.metadata.entry_points().get(self.ENTRY_POINT_GROUP, [])
            
            for entry_point in entry_points:
                try:
                    plugin_info = self._load_entry_point(entry_point)
                    if plugin_info:
                        self.plugins[plugin_info.name] = plugin_info
                        logger.info(f"Loaded entry point plugin: {plugin_info.display_name}")
                except Exception as e:
                    logger.error(f"Failed to load entry point {entry_point.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load entry point plugins: {e}")
    
    def _load_entry_point(self, entry_point) -> Optional[PluginInfo]:
        """Load a single entry point plugin."""
        try:
            # Load the plugin module/class
            plugin_obj = entry_point.load()
            
            # Check if it's a class that inherits from AIProvider
            if inspect.isclass(plugin_obj) and issubclass(plugin_obj, AIProvider):
                # Get plugin metadata
                metadata = getattr(plugin_obj, 'PLUGIN_METADATA', {})
                
                return PluginInfo(
                    name=entry_point.name,
                    display_name=metadata.get('display_name', entry_point.name),
                    description=metadata.get('description', ''),
                    version=metadata.get('version', '1.0.0'),
                    author=metadata.get('author', 'Unknown'),
                    provider_class=plugin_obj,
                    config_schema=metadata.get('config_schema'),
                    source="entrypoint"
                )
            else:
                logger.warning(f"Entry point {entry_point.name} is not a valid AIProvider")
                return None
                
        except Exception as e:
            logger.error(f"Error loading entry point {entry_point.name}: {e}")
            return None
    
    def _load_user_plugins(self):
        """Load plugins from user plugin directory."""
        if not self.settings_manager:
            return
        
        plugin_dir = self.settings_manager.get_plugin_directory()
        if not plugin_dir or not Path(plugin_dir).exists():
            return
        
        plugin_path = Path(plugin_dir)
        
        # Add plugin directory to Python path
        if str(plugin_path) not in sys.path:
            sys.path.insert(0, str(plugin_path))
        
        # Look for plugin manifests
        for manifest_file in plugin_path.glob("*/plugin.json"):
            try:
                self._load_plugin_from_manifest(manifest_file)
            except Exception as e:
                logger.error(f"Failed to load plugin from {manifest_file}: {e}")
    
    def _load_plugin_from_manifest(self, manifest_path: Path):
        """Load a plugin from a manifest file."""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Validate manifest
        required_fields = ['name', 'module', 'class']
        if not all(field in manifest for field in required_fields):
            raise ValueError(f"Invalid manifest: missing required fields")
        
        # Load the module
        plugin_dir = manifest_path.parent
        module_name = manifest['module']
        
        # Import the module
        spec = importlib.util.spec_from_file_location(
            module_name,
            plugin_dir / f"{module_name}.py"
        )
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load module {module_name}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get the provider class
        provider_class = getattr(module, manifest['class'])
        
        if not issubclass(provider_class, AIProvider):
            raise TypeError(f"{manifest['class']} is not a valid AIProvider")
        
        # Create plugin info
        plugin_info = PluginInfo(
            name=manifest['name'],
            display_name=manifest.get('display_name', manifest['name']),
            description=manifest.get('description', ''),
            version=manifest.get('version', '1.0.0'),
            author=manifest.get('author', 'Unknown'),
            provider_class=provider_class,
            config_schema=manifest.get('config_schema'),
            source="file"
        )
        
        # Check if enabled
        if self.settings_manager:
            enabled_plugins = self.settings_manager.get('enabled_plugins', {})
            plugin_info.enabled = enabled_plugins.get(manifest['name'], True)
        
        self.plugins[plugin_info.name] = plugin_info
        logger.info(f"Loaded user plugin: {plugin_info.display_name}")
    
    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all loaded plugins."""
        return list(self.plugins.values())
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Get all enabled plugins."""
        return [p for p in self.plugins.values() if p.enabled]
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = True
            self._save_plugin_state()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = False
            self._save_plugin_state()
            return True
        return False
    
    def create_provider_instance(
        self, 
        plugin_name: str, 
        config: Dict[str, Any]
    ) -> Optional[AIProvider]:
        """Create an instance of a provider from a plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin or not plugin.enabled:
            return None
        
        try:
            # Validate config against schema
            if plugin.config_schema:
                self._validate_config(config, plugin.config_schema)
            
            # Create instance
            provider = plugin.provider_class(**config)
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create provider instance for {plugin_name}: {e}")
            return None
    
    def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]):
        """Validate configuration against schema."""
        for field, field_schema in schema.items():
            if field_schema.get('required', False) and field not in config:
                raise ValueError(f"Required field '{field}' missing")
            
            if field in config:
                field_type = field_schema.get('type', 'string')
                value = config[field]
                
                # Basic type validation
                if field_type == 'string' and not isinstance(value, str):
                    raise TypeError(f"Field '{field}' must be a string")
                elif field_type == 'number' and not isinstance(value, (int, float)):
                    raise TypeError(f"Field '{field}' must be a number")
                elif field_type == 'boolean' and not isinstance(value, bool):
                    raise TypeError(f"Field '{field}' must be a boolean")
    
    def _save_plugin_state(self):
        """Save plugin enabled/disabled state."""
        if not self.settings_manager:
            return
        
        enabled_plugins = {
            name: plugin.enabled 
            for name, plugin in self.plugins.items()
            if plugin.source != "builtin"  # Don't save builtin state
        }
        
        self.settings_manager.set('enabled_plugins', enabled_plugins)
        self.settings_manager.save_settings()
    
    def reload_plugins(self):
        """Reload all plugins."""
        # Keep enabled state
        enabled_state = {
            name: plugin.enabled 
            for name, plugin in self.plugins.items()
        }
        
        # Clear and reload
        self.plugins.clear()
        self._loaded_modules.clear()
        
        self._load_builtin_providers()
        self._load_entry_point_plugins()
        self._load_user_plugins()
        
        # Restore enabled state
        for name, enabled in enabled_state.items():
            if name in self.plugins:
                self.plugins[name].enabled = enabled
    
    def get_plugin_documentation(self, plugin_name: str) -> str:
        """Get documentation for a plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return "Plugin not found"
        
        doc_parts = [
            f"# {plugin.display_name}",
            f"**Version:** {plugin.version}",
            f"**Author:** {plugin.author}",
            f"**Source:** {plugin.source}",
            "",
            plugin.description,
            ""
        ]
        
        # Add configuration schema documentation
        if plugin.config_schema:
            doc_parts.append("## Configuration")
            doc_parts.append("")
            
            for field, schema in plugin.config_schema.items():
                required = " *(required)*" if schema.get('required', False) else ""
                secret = " *(secret)*" if schema.get('secret', False) else ""
                doc_parts.append(f"- **{field}**{required}{secret}: {schema.get('description', '')}")
                
                if 'default' in schema:
                    doc_parts.append(f"  - Default: `{schema['default']}`")
                if 'type' in schema:
                    doc_parts.append(f"  - Type: {schema['type']}")
        
        # Add provider class documentation
        if plugin.provider_class.__doc__:
            doc_parts.extend(["", "## Provider Documentation", "", plugin.provider_class.__doc__])
        
        return "\n".join(doc_parts)


# Example custom provider plugin template
PLUGIN_TEMPLATE = '''"""
Example BSM AI Provider Plugin.

To create a custom provider:
1. Inherit from AIProvider
2. Implement required methods
3. Add PLUGIN_METADATA
4. Install via entry point or place in plugins directory
"""

from typing import Dict, Any
from bsm.core.ai_providers import AIProvider


class CustomProvider(AIProvider):
    """Custom AI provider implementation."""
    
    # Plugin metadata
    PLUGIN_METADATA = {
        'display_name': 'Custom Provider',
        'description': 'A custom AI provider for BSM',
        'version': '1.0.0',
        'author': 'Your Name',
        'config_schema': {
            'api_key': {
                'type': 'string',
                'description': 'API key for the service',
                'required': True,
                'secret': True
            },
            'endpoint': {
                'type': 'string',
                'description': 'API endpoint URL',
                'default': 'https://api.example.com',
                'required': False
            }
        }
    }
    
    def __init__(self, api_key: str, endpoint: str = 'https://api.example.com'):
        super().__init__()
        self.api_key = api_key
        self.endpoint = endpoint
    
    def get_name(self) -> str:
        return "Custom Provider"
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text and return results."""
        # Implement your analysis logic here
        self._report_progress(10)
        
        # Make API calls, process text, etc.
        
        self._report_progress(100)
        
        return {
            "summary": "Analysis complete",
            "analysis": "Your analysis here",
            "confidence_score": 0.85,
            "provider_used": self.get_name()
        }
'''
