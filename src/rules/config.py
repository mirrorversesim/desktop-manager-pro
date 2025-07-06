import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manager class for configuration operations"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.rules_file = self.config_dir / "default_rules.json"
        self.logger = logger
    
    def load_rules(self) -> List[Dict[str, Any]]:
        """Load rules from the configuration file"""
        try:
            if self.rules_file.exists():
                return load_rules(str(self.rules_file))
            else:
                # Return default rules if no config file exists
                return get_default_rules()
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            return get_default_rules()
    
    def save_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Save rules to the configuration file"""
        try:
            return save_rules(rules, str(self.rules_file))
        except Exception as e:
            self.logger.error(f"Error saving rules: {e}")
            return False
    
    def get_config_path(self) -> str:
        """Get the configuration directory path"""
        return str(self.config_dir)


def load_rules(filepath: str) -> List[Dict[str, Any]]:
    """
    Load rules from a JSON file.
    
    Args:
        filepath: Path to the JSON file containing rules
        
    Returns:
        List[Dict[str, Any]]: List of rule dictionaries
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        if not os.path.exists(filepath):
            logger.error(f"Rules file not found: {filepath}")
            raise FileNotFoundError(f"Rules file not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
            
        if not isinstance(rules, list):
            logger.error(f"Invalid rules file format: expected list, got {type(rules)}")
            raise ValueError("Rules file must contain a list of rules")
            
        # Validate rules structure
        validated_rules = []
        for i, rule in enumerate(rules):
            if _validate_rule(rule, i):
                validated_rules.append(rule)
                
        logger.info(f"Loaded {len(validated_rules)} rules from {filepath}")
        return validated_rules
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rules file {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading rules from {filepath}: {e}")
        raise


def save_rules(rules: List[Dict[str, Any]], filepath: str) -> bool:
    """
    Save rules to a JSON file.
    
    Args:
        rules: List of rule dictionaries to save
        filepath: Path to save the rules file
        
    Returns:
        bool: True if saved successfully
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Saved {len(rules)} rules to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving rules to {filepath}: {e}")
        return False


def get_default_rules() -> List[Dict[str, Any]]:
    """
    Load the default rules configuration.
    
    Returns:
        List[Dict[str, Any]]: List of default rules
    """
    try:
        # Get the path to the default rules file
        current_dir = Path(__file__).parent.parent.parent
        default_rules_path = current_dir / "config" / "default_rules.json"
        
        return load_rules(str(default_rules_path))
        
    except Exception as e:
        logger.error(f"Error loading default rules: {e}")
        return []


def _validate_rule(rule: Dict[str, Any], index: int) -> bool:
    """
    Validate a single rule structure.
    
    Args:
        rule: Rule dictionary to validate
        index: Index of the rule in the list (for error reporting)
        
    Returns:
        bool: True if rule is valid
    """
    try:
        # Check required fields
        required_fields = ['name', 'enabled', 'trigger', 'action']
        for field in required_fields:
            if field not in rule:
                logger.warning(f"Rule {index}: Missing required field '{field}'")
                return False
                
        # Validate trigger structure
        trigger = rule.get('trigger', {})
        if not isinstance(trigger, dict):
            logger.warning(f"Rule {index}: Invalid trigger structure")
            return False
            
        # Validate action structure
        action = rule.get('action', {})
        if not isinstance(action, dict):
            logger.warning(f"Rule {index}: Invalid action structure")
            return False
            
        # Check for required trigger fields
        if 'event_type' not in trigger:
            logger.warning(f"Rule {index}: Missing event_type in trigger")
            return False
            
        # Check for required action fields
        if 'type' not in action:
            logger.warning(f"Rule {index}: Missing type in action")
            return False
            
        # Validate event_type
        valid_event_types = ['CREATE', 'DESTROY', 'SHOW', 'HIDE', 'FOREGROUND', 'NAMECHANGE']
        if trigger['event_type'] not in valid_event_types:
            logger.warning(f"Rule {index}: Invalid event_type '{trigger['event_type']}'")
            return False
            
        # Validate action type
        valid_action_types = [
            'MINIMIZE_OTHERS_OF_SAME_APP',
            'CLOSE_DUPLICATE_PATH',
            'BRING_TO_FOREGROUND',
            'CLOSE_WINDOW',
            'HIDE_WINDOW'
        ]
        if action['type'] not in valid_action_types:
            logger.warning(f"Rule {index}: Invalid action type '{action['type']}'")
            return False
            
        return True
        
    except Exception as e:
        logger.warning(f"Rule {index}: Validation error: {e}")
        return False


def create_rule(name: str, enabled: bool, trigger: Dict[str, Any], 
                action: Dict[str, Any], priority: int = 50, 
                description: str = "") -> Dict[str, Any]:
    """
    Create a new rule with proper structure.
    
    Args:
        name: Rule name
        enabled: Whether the rule is enabled
        trigger: Trigger conditions
        action: Action to perform
        priority: Rule priority (higher = more important)
        description: Rule description
        
    Returns:
        Dict[str, Any]: Rule dictionary
    """
    return {
        'name': name,
        'enabled': enabled,
        'trigger': trigger,
        'action': action,
        'priority': priority,
        'description': description
    }


def enable_rule(rules: List[Dict[str, Any]], rule_name: str) -> bool:
    """
    Enable a rule by name.
    
    Args:
        rules: List of rules
        rule_name: Name of the rule to enable
        
    Returns:
        bool: True if rule was found and enabled
    """
    for rule in rules:
        if rule.get('name') == rule_name:
            rule['enabled'] = True
            logger.info(f"Enabled rule: {rule_name}")
            return True
            
    logger.warning(f"Rule not found: {rule_name}")
    return False


def disable_rule(rules: List[Dict[str, Any]], rule_name: str) -> bool:
    """
    Disable a rule by name.
    
    Args:
        rules: List of rules
        rule_name: Name of the rule to disable
        
    Returns:
        bool: True if rule was found and disabled
    """
    for rule in rules:
        if rule.get('name') == rule_name:
            rule['enabled'] = False
            logger.info(f"Disabled rule: {rule_name}")
            return True
            
    logger.warning(f"Rule not found: {rule_name}")
    return False


def get_enabled_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get only the enabled rules from a list.
    
    Args:
        rules: List of all rules
        
    Returns:
        List[Dict[str, Any]]: List of enabled rules
    """
    return [rule for rule in rules if rule.get('enabled', False)]


def sort_rules_by_priority(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort rules by priority (highest first).
    
    Args:
        rules: List of rules to sort
        
    Returns:
        List[Dict[str, Any]]: Sorted list of rules
    """
    return sorted(rules, key=lambda x: x.get('priority', 0), reverse=True) 