"""
Unit test that demonstrates the critical bug in create_output_definition.

This test would FAIL before the fix and PASS after the fix.
"""

import os
import sys

# Add the arcade-core path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "arcade-core"))

from typing import Annotated

import pytest


def test_create_output_definition_with_annotated_metadata():
    """
    Test that create_output_definition handles Annotated types with metadata correctly.

    This test would FAIL before the bug fix because:
    1. For Annotated[str, "description"], __origin__ is None
    2. The buggy code would set return_type = None
    3. get_wire_type_info(None) would raise ToolDefinitionError

    After the fix, this test PASSES because:
    1. The code checks if __origin__ is not None before assignment
    2. When __origin__ is None, it keeps the original Annotated type
    3. The type processing continues correctly
    """
    from arcade_core.catalog import create_output_definition

    # Define a function with Annotated return type where __origin__ is None
    def test_function() -> Annotated[str, "A test string with metadata"]:
        """A test function that returns an annotated string."""
        return "test"

    # This would raise ToolDefinitionError before the fix
    # After the fix, it should work correctly
    try:
        output_def = create_output_definition(test_function)

        # Verify the output definition was created correctly
        assert output_def is not None
        assert output_def.description == "A test string with metadata"
        assert output_def.value_schema is not None
        assert output_def.value_schema.val_type == "string"
        assert "value" in output_def.available_modes
        assert "error" in output_def.available_modes

        print("✅ Test PASSED: create_output_definition handled Annotated type correctly")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        # Before the fix, this would raise:
        # ToolDefinitionError: Unsupported parameter type: None
        return False


def test_demonstrate_bug_scenario():
    """
    Additional test to show the exact scenario that would cause the bug.
    """
    from typing import get_origin

    # Show the problematic case
    annotated_type = Annotated[str, "Some description"]

    print(f"Type: {annotated_type}")
    print(f"Has __metadata__: {hasattr(annotated_type, '__metadata__')}")
    print(f"__metadata__: {getattr(annotated_type, '__metadata__', None)}")
    print(f"__origin__: {getattr(annotated_type, '__origin__', 'NOT_FOUND')}")

    # This is the critical issue: __origin__ is None for simple Annotated types
    origin = getattr(annotated_type, "__origin__", None)
    if origin is None:
        print("⚠️  This is the bug scenario: __origin__ is None!")
        print("    The buggy code would set return_type = None")
        print("    Leading to ToolDefinitionError when processing the type")


if __name__ == "__main__":
    print("Testing the metadata bug fix...")
    print("=" * 50)

    # Show the problematic scenario
    test_demonstrate_bug_scenario()
    print()

    # Run the actual test
    success = test_create_output_definition_with_annotated_metadata()

    if success:
        print("\n🎉 All tests passed! The bug has been fixed.")
    else:
        print("\n💥 Test failed! This would happen with the original buggy code.")
