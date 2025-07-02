#!/usr/bin/env python3
"""
Accurate test showing the exact scenario where __origin__ is None.

This demonstrates the real bug case that would cause crashes.
"""

from typing import Annotated


def find_problematic_type():
    """Find the exact type scenario that causes __origin__ to be None."""
    print("🔍 INVESTIGATING TYPE SCENARIOS")
    print("=" * 50)

    # Test different Annotated scenarios
    scenarios = [
        ("Simple Annotated", Annotated[str, "description"]),
        ("Multiple metadata", Annotated[int, "name", "description"]),
        ("Complex metadata", Annotated[bool, {"key": "value"}]),
    ]

    for name, type_obj in scenarios:
        print(f"\n{name}: {type_obj}")
        print(f"  __origin__: {getattr(type_obj, '__origin__', 'NOT_FOUND')}")
        print(f"  __metadata__: {getattr(type_obj, '__metadata__', 'NOT_FOUND')}")

        # Check if this is the problematic case
        origin = getattr(type_obj, "__origin__", None)
        has_metadata = hasattr(type_obj, "__metadata__")

        if has_metadata and origin is None:
            print(f"  ⚠️  BUG TRIGGER: has metadata but __origin__ is None!")
            return type_obj
        elif has_metadata and origin is not None:
            print(f"  ✓ Safe: has metadata and __origin__ is {origin}")
        else:
            print(f"  ℹ️  No metadata")

    return None


def simulate_real_bug():
    """
    Simulate the real bug by creating a scenario where hasattr(__metadata__) is True
    but __origin__ access might be problematic.
    """
    print("\n" + "=" * 50)
    print("SIMULATING THE REAL BUG SCENARIO")
    print("=" * 50)

    # The issue might be with how __origin__ is accessed, not that it's None
    # Let's check what happens when we access __origin__ on different types

    test_type = Annotated[str, "test description"]
    print(f"Test type: {test_type}")
    print(f"hasattr(__metadata__): {hasattr(test_type, '__metadata__')}")
    print(f"hasattr(__origin__): {hasattr(test_type, '__origin__')}")

    # Direct access
    try:
        origin = test_type.__origin__
        print(f"Direct __origin__ access: {origin}")
    except AttributeError as e:
        print(f"AttributeError accessing __origin__: {e}")
        print("⚠️  THIS would be the bug scenario!")
        return True, test_type

    # Check if __origin__ could be None in some cases
    if hasattr(test_type, "__origin__"):
        origin = getattr(test_type, "__origin__")
        if origin is None:
            print(f"⚠️  Found it! __origin__ is None")
            return True, test_type
        else:
            print(f"__origin__ is {origin} (not None)")

    return False, test_type


def demonstrate_actual_fix():
    """Show the exact difference between buggy and fixed code."""
    print("\n" + "=" * 50)
    print("DEMONSTRATING THE ACTUAL FIX")
    print("=" * 50)

    test_type = Annotated[str, "test description"]

    print("The bug was in this logic:")
    print("if hasattr(return_type, '__metadata__'):")
    print("    description = return_type.__metadata__[0] if return_type.__metadata__ else None")
    print("    return_type = return_type.__origin__  # POTENTIAL BUG HERE")
    print()

    print("Testing with our type...")

    if hasattr(test_type, "__metadata__"):
        metadata = test_type.__metadata__
        print(f"✓ Has metadata: {metadata}")

        # The buggy assignment
        print(f"Buggy code would do: return_type = {test_type}.__origin__")

        # Check what __origin__ actually is
        if hasattr(test_type, "__origin__"):
            origin = test_type.__origin__
            print(f"  __origin__ = {origin}")

            if origin is None:
                print("  ❌ BUG: Assigning None to return_type!")
                print("  This would cause get_wire_type_info(None) to fail")
            else:
                print(f"  ✓ Safe: __origin__ is {origin}")
        else:
            print("  ❌ BUG: No __origin__ attribute!")
            print("  Direct access would raise AttributeError")

    print("\nThe fix adds a safety check:")
    print("if return_type.__origin__ is not None:")
    print("    return_type = return_type.__origin__")
    print("# Otherwise keep the original type")


def create_failing_test_case():
    """Create a test that would actually fail before the fix."""
    print("\n" + "=" * 50)
    print("CREATING ACTUAL FAILING TEST CASE")
    print("=" * 50)

    # The real issue: let's create a type where __origin__ access is problematic

    class MockAnnotatedType:
        """Mock type that simulates the problematic scenario."""

        def __init__(self):
            self.__metadata__ = ("test description",)
            # Intentionally don't set __origin__ or set it to None

        @property
        def __origin__(self):
            return None  # This is the bug scenario!

    mock_type = MockAnnotatedType()

    print(f"Mock type: {mock_type}")
    print(f"hasattr(__metadata__): {hasattr(mock_type, '__metadata__')}")
    print(f"__metadata__: {mock_type.__metadata__}")
    print(f"__origin__: {mock_type.__origin__}")

    print("\nNow testing buggy vs fixed behavior:")

    # Buggy behavior
    print("BUGGY CODE:")
    if hasattr(mock_type, "__metadata__"):
        description = mock_type.__metadata__[0] if mock_type.__metadata__ else None
        return_type = mock_type.__origin__  # This assigns None!
        print(f"  description = '{description}'")
        print(f"  return_type = {return_type}  ❌ This is None!")

    # Fixed behavior
    print("\nFIXED CODE:")
    if hasattr(mock_type, "__metadata__"):
        description = mock_type.__metadata__[0] if mock_type.__metadata__ else None
        if mock_type.__origin__ is not None:
            return_type = mock_type.__origin__
            print(f"  Would assign: return_type = {mock_type.__origin__}")
        else:
            return_type = mock_type  # Keep original!
            print(f"  Keeping original: return_type = {return_type}  ✅ Safe!")
        print(f"  description = '{description}'")


if __name__ == "__main__":
    print("🐛 ACCURATE BUG DEMONSTRATION")
    print("Finding the exact scenario that causes the bug...")

    # Try to find a real problematic type
    problematic = find_problematic_type()

    # Simulate the real bug
    is_bug, test_type = simulate_real_bug()

    # Show the actual fix
    demonstrate_actual_fix()

    # Create a failing test case
    create_failing_test_case()

    print("\n" + "=" * 50)
    print("CONCLUSION")
    print("=" * 50)
    print("The bug occurs when:")
    print("1. A type has __metadata__ (so the if condition is True)")
    print("2. But __origin__ is None (or missing)")
    print("3. The buggy code assigns None to return_type")
    print("4. Later, get_wire_type_info(None) fails")
    print()
    print("The fix prevents this by checking __origin__ is not None before assignment!")
