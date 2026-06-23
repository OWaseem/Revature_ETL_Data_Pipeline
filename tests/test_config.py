import pytest
from config import load_sources

def test_load_sources_returns_list():
    # load_sources should return a list of source definitions
    result = load_sources("config/sources.yml")
    assert isinstance(result, list)
    assert len(result) > 0

def test_load_sources_has_required_keys():
    # each source must have name, format, and target_table
    result = load_sources("config/sources.yml")
    for source in result:
        assert "name" in source
        assert "format" in source
        assert "target_table" in source

def test_load_sources_file_not_found():
    # loading a non-existent file should raise an error
    with pytest.raises(Exception):
        load_sources("config/nonexistent.yml")
