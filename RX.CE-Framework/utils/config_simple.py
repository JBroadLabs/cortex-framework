#!/usr/bin/env python3
"""
Simple configuration loader with auto-generation and lazy loading.

Features:
- Auto-creates config on first use
- Lazy loading (loads once, cached)
- No validation (simple and fast)
- Minimal overhead (~50ms first time, 0ms after)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


# Default configuration
DEFAULTS = {
    'skip_code_review': False,
    'skip_testing': False,
    'skip_qa': False,
    'coding_standards': True,
    'strict_version_checking': True,
    'min_coverage_percent': 80,
    'sharding_threshold': 500,
}


# Config template with inline help
CONFIG_TEMPLATE = """# Framework Configuration
# Auto-generated. Edit values to customize workflow.
# Delete this file anytime to restore defaults.

#===================================================================
# WORKFLOW - Skip stages for faster iteration
#===================================================================

skip_code_review: false      # true = skip [CR] stage
skip_testing: false          # true = skip [T] stage
skip_qa: false               # true = skip [Q] stage

# Examples:
#   Fast prototyping: Set all to true -> [I] -> [Done]
#   Trust tests only: skip_code_review=true, skip_qa=true -> [I] -> [T] -> [Done]


#===================================================================
# FEATURES - Toggle major capabilities
#===================================================================

coding_standards: true           # Enforce code quality via linters
strict_version_checking: true    # Block if doc versions incompatible


#===================================================================
# TESTING - Quality requirements
#===================================================================

min_coverage_percent: 80         # Test coverage threshold (0-100)


#===================================================================
# ADVANCED - Rarely changed
#===================================================================

sharding_threshold: 500          # Lines before doc sharding triggers


#===================================================================
# QUICK REFERENCE
#===================================================================
#
# Common scenarios:
#   1. Default (as above) - Full workflow, all quality gates
#   2. Fast (skip_qa: true) - Skip final QA for speed
#   3. Minimal (all skips: true) - Implementation only, no validation
#   4. Strict (min_coverage: 90) - Production-grade quality
#
# Commands:
#   claude code: /ask "how does [setting] work?"
#
#===================================================================
"""


# Global cache (lazy loading)
_cached_config: Optional[Dict[str, Any]] = None


def get_config() -> Dict[str, Any]:
    """
    Get configuration (lazy loaded and cached).

    First call: Reads file (~50ms)
    Subsequent calls: Returns cached copy (~0ms)
    """
    global _cached_config

    if _cached_config is None:
        _cached_config = _load_config()

    return _cached_config


def _load_config() -> Dict[str, Any]:
    """Load config from file or create default."""
    config_path = Path('.claude/config.yml')

    # Auto-create if doesn't exist
    if not config_path.exists():
        _create_default_config(config_path)
        return {'_just_created': True, **DEFAULTS}

    # Load existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[!] Error reading config: {e}")
        print("    Using defaults")
        user_config = {}

    # Merge with defaults (user values override)
    config = {**DEFAULTS, **user_config}
    return config


def _create_default_config(config_path: Path):
    """Create default config file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(CONFIG_TEMPLATE, encoding='utf-8')
    print(f"[+] Created {config_path}")


def get_workflow_path(config: Dict[str, Any]) -> list:
    """Calculate workflow path based on config."""
    path = ['[Pending]', '[I]']

    if not config.get('skip_code_review', False):
        path.append('[CR]')

    if not config.get('skip_testing', False):
        path.append('[T]')

    if not config.get('skip_qa', False):
        path.append('[Q]')

    path.append('[Done]')
    return path


if __name__ == '__main__':
    # Test the loader
    config = get_config()
    workflow = ' -> '.join(get_workflow_path(config))
    print(f"[+] Config loaded")
    print(f"Workflow: {workflow}")
