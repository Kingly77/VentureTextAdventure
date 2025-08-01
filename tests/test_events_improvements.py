#!/usr/bin/env python3
"""
Test script to verify the improvements made to the events system.
This script tests all the key improvements:
1. Fixed return value collection
2. Proper exception handling
3. Enhanced Handler class
4. Event debugging support
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.underlings.events import (
    Events,
    EventHandler,
    EventNotFoundError,
    HandlerNotFoundError,
)


def test_return_value_collection():
    """Test that trigger_event properly collects all handler results."""
    print("Testing return value collection...")

    # Clear any existing events
    Events.clear_all_events()

    def handler1():
        return "Result from handler 1"

    def handler2():
        return "Result from handler 2"

    def handler3():
        return None  # Should not be included in results

    # Register multiple handlers
    Events.add_event("test_multiple", handler1)
    Events.add_event("test_multiple", handler2)
    Events.add_event("test_multiple", handler3)

    # Trigger event and check results
    results = Events.trigger_event("test_multiple")

    assert results is not None, "Results should not be None"
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    assert "Result from handler 1" in results, "Missing result from handler 1"
    assert "Result from handler 2" in results, "Missing result from handler 2"

    print("✓ Return value collection test passed")


def test_exception_handling():
    """Test that proper exceptions are raised."""
    print("Testing exception handling...")

    Events.clear_all_events()

    # Test EventNotFoundError for trigger_event
    try:
        Events.trigger_event("nonexistent_event")
        assert False, "Should have raised EventNotFoundError"
    except EventNotFoundError as e:
        assert "nonexistent_event" in str(e)
        print("✓ EventNotFoundError for trigger_event works")

    # Test EventNotFoundError for remove_event
    try:
        Events.remove_event("nonexistent_event", lambda: None)
        assert False, "Should have raised EventNotFoundError"
    except EventNotFoundError as e:
        assert "nonexistent_event" in str(e)
        print("✓ EventNotFoundError for remove_event works")

    # Test HandlerNotFoundError
    def test_handler():
        return "test"

    Events.add_event("test_event", test_handler)

    try:
        Events.remove_event("test_event", lambda: "different")
        assert False, "Should have raised HandlerNotFoundError"
    except HandlerNotFoundError as e:
        assert "Handler function not found" in str(e)
        print("✓ HandlerNotFoundError works")


def test_enhanced_handler():
    """Test the enhanced EventHandler class."""
    print("Testing enhanced EventHandler...")

    Events.clear_all_events()

    def test_func():
        return "Enhanced handler result"

    # Create enhanced handler
    handler = EventHandler(
        test_func, priority=10, description="Test handler", one_time=True
    )

    # Test handler properties
    assert handler.priority == 10
    assert handler.description == "Test handler"
    assert handler.one_time == True

    # Test handler execution
    result = handler()
    assert result == "Enhanced handler result"

    print("✓ Enhanced EventHandler test passed")


def test_debugging_support():
    """Test the debugging support methods."""
    print("Testing debugging support...")

    Events.clear_all_events()

    def handler1():
        return "test1"

    def handler2():
        return "test2"

    # Add some events
    Events.add_event("debug_test1", handler1)
    Events.add_event("debug_test1", handler2)
    Events.add_event("debug_test2", handler1, one_time=True)

    # Test list_events
    event_list = Events.list_events()
    assert "debug_test1" in event_list
    assert "debug_test2" in event_list
    assert event_list["debug_test1"] == 2
    assert event_list["debug_test2"] == 1
    print("✓ list_events works")

    # Test get_event_info
    info = Events.get_event_info("debug_test1")
    assert info["name"] == "debug_test1"
    assert info["handler_count"] == 2
    assert len(info["handlers"]) == 2
    print("✓ get_event_info works")

    # Test get_event_info with nonexistent event
    try:
        Events.get_event_info("nonexistent")
        assert False, "Should have raised EventNotFoundError"
    except EventNotFoundError:
        print("✓ get_event_info exception handling works")


def test_one_time_handlers():
    """Test that one-time handlers are properly removed."""
    print("Testing one-time handlers...")

    Events.clear_all_events()

    call_count = 0

    def one_time_handler():
        nonlocal call_count
        call_count += 1
        return f"Called {call_count} times"

    # Add one-time handler
    Events.add_event("one_time_test", one_time_handler, one_time=True)

    # First trigger should work
    results = Events.trigger_event("one_time_test")
    assert results is not None
    assert len(results) == 1
    assert call_count == 1

    # Second trigger should raise EventNotFoundError (event should be gone)
    try:
        Events.trigger_event("one_time_test")
        assert False, "Event should have been removed after one-time use"
    except EventNotFoundError:
        print("✓ One-time handler removal works")


def test_error_handling_in_handlers():
    """Test that errors in handlers don't break the event system."""
    print("Testing error handling in handlers...")

    Events.clear_all_events()

    def good_handler():
        return "Good result"

    def bad_handler():
        raise Exception("Handler error")

    def another_good_handler():
        return "Another good result"

    # Add handlers including one that will fail
    Events.add_event("error_test", good_handler)
    Events.add_event("error_test", bad_handler)
    Events.add_event("error_test", another_good_handler)

    # Trigger event - should get results from good handlers despite the error
    results = Events.trigger_event("error_test")

    assert results is not None
    assert len(results) == 2  # Only the good handlers should return results
    assert "Good result" in results
    assert "Another good result" in results

    print("✓ Error handling in handlers works")


def run_all_tests():
    """Run all test functions."""
    print("Running event system improvement tests...\n")

    test_return_value_collection()
    test_exception_handling()
    test_enhanced_handler()
    test_debugging_support()
    test_one_time_handlers()
    test_error_handling_in_handlers()

    print("\n✅ All tests passed! Event system improvements are working correctly.")


if __name__ == "__main__":
    run_all_tests()
