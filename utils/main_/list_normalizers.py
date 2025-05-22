def list_normalizers() -> None:
    """List all available text normalizers."""
    from core.processing_pipeline import processing_pipeline
    print("Omni-Converter Text Normalizers\n===============================\n\n")

    normalizers = processing_pipeline.normalizer.applied_normalizers

    for normalizer in sorted(normalizers):
        print(f"- {normalizer}")

    print("\nUse --normalizers option to specify which normalizers to apply.")
    print("Example: --normalizers whitespace,line_endings")