import pytest
from keystone.core import validator

@pytest.fixture
def valid_data():
    return {
        "tool": "test-tool",
        "categories": [
            {
                "name": "Test Category",
                "keybinds": [
                    {
                        "action": "Test Action",
                        "keys": "Ctrl+T"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def invalid_data():
    return {
        "tool": "test-tool",
        "categories": [
            {
                "name": "Test Category",
                "keybinds": [
                    {
                        "action": "Test Action",
                        "keys": 123 # Invalid type
                    }
                ]
            }
        ]
    }

@pytest.fixture
def data_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Keystone Keybind Data Schema",
        "description": "Schema for tool-specific keybind data files.",
        "type": "object",
        "properties": {
            "tool": {
                "description": "The name of the tool or application.",
                "type": "string"
            },
            "version": {
                "description": "The version of the tool.",
                "type": "string"
            },
            "categories": {
                "description": "A list of keybind categories.",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "The name of the category.",
                            "type": "string"
                        },
                        "keybinds": {
                            "description": "A list of keybinds in this category.",
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "description": "The action the keybind performs.",
                                        "type": "string"
                                    },
                                    "keys": {
                                        "description": "The key or keys for the action.",
                                        "oneOf": [
                                            {
                                                "type": "string"
                                            },
                                            {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                }
                                            }
                                        ]
                                    },
                                    "description": {
                                        "description": "A description of the action.",
                                        "type": "string"
                                    }
                                },
                                "required": ["action", "keys"]
                            }
                        }
                    },
                    "required": ["name", "keybinds"]
                }
            }
        },
        "required": ["tool", "categories"]
    }

def test_validate_schema_valid(valid_data, data_schema):
    is_valid, error = validator.validate_schema(valid_data, data_schema)
    assert is_valid
    assert error is None

def test_validate_schema_invalid(invalid_data, data_schema):
    is_valid, error = validator.validate_schema(invalid_data, data_schema)
    assert not is_valid
    assert error is not None
