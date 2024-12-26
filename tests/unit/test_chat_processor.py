import pytest
from src.features.chat_processor import ChatProcessor

def test_chat_processor_initialization():
    """Test that ChatProcessor can be initialized"""
    processor = ChatProcessor()
    assert processor is not None

def test_chat_processor_process_input():
    """Test that ChatProcessor can process user input"""
    processor = ChatProcessor()
    response = processor.process_user_input("Bonjour")
    assert isinstance(response, str)
    assert len(response) > 0
