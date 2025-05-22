def list_supported_formats() -> None:
    """List all supported formats."""
    from format_handlers.format_registry import format_registry

    # Format the handler capabilities
    print("Omni-Converter Supported Formats\n===============================\n\n")

    # Get formats grouped by category from the registry
    categories = format_registry.get_formats_by_category()

    # Print formats by category
    for category, formats in sorted(categories.items()):
        print(f"{category.capitalize()} Formats ({len(formats)}):")
        for fmt in sorted(formats):
            print(f"  - {fmt}")
        print()
