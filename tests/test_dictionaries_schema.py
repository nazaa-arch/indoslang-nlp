"""Validation tests for dictionary files and JSON Schema compliance."""

import json
from pathlib import Path

import jsonschema
import pytest


@pytest.fixture
def schema():
    schema_path = Path("indoslang/data/schema/lexicon.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def dictionary_files():
    dict_dir = Path("indoslang/data/dictionaries")
    return list(dict_dir.glob("*.json"))


def test_schema_validity(schema):
    """Ensure the JSON schema itself is valid Draft-07."""
    jsonschema.Draft7Validator.check_schema(schema)


def test_all_dictionaries_comply_with_schema(schema, dictionary_files):
    """Ensure every dictionary file conforms to the schema."""
    validator = jsonschema.Draft7Validator(schema)
    assert len(dictionary_files) >= 4, "Expected at least 4 dictionary files"

    for dict_path in dictionary_files:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        errors = list(validator.iter_errors(data))
        assert not errors, f"Schema validation errors in {dict_path}: {errors}"


def test_no_duplicate_keys_across_dictionaries(dictionary_files):
    """Verify that no two dictionaries define the same word key."""
    all_keys = {}
    for dict_path in dictionary_files:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in data:
            assert key not in all_keys, f"Duplicate key '{key}' found in {dict_path.name} and {all_keys[key]}"
            all_keys[key] = dict_path.name


def test_anti_chaining_rule(dictionary_files):
    """Verify anti-chaining: normalized word cannot be an entry key (A -> B -> C is forbidden)."""
    all_keys = set()
    for dict_path in dictionary_files:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_keys.update(data.keys())

    for dict_path in dictionary_files:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, entry in data.items():
            for sense in entry["senses"]:
                norm = sense["normalized"]
                # If norm is a key in any dictionary, it would cause a chain unless it's identical
                if norm != key:
                    assert norm not in all_keys, (
                        f"Anti-chaining violation: '{key}' normalizes to '{norm}', "
                        f"which is also a key in dictionaries!"
                    )


def test_confidence_scores_valid(dictionary_files):
    """Verify confidence scores are 0-1 and sum of senses confidence is ~1.0."""
    for dict_path in dictionary_files:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, entry in data.items():
            total_conf = sum(s["confidence"] for s in entry["senses"])
            assert 0.9 <= total_conf <= 1.05, f"Confidence sum for '{key}' in {dict_path.name} is {total_conf}, expected ~1.0"
