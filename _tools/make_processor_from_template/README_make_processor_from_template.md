# Processor Template Generator Tool

## Usage

```bash
python make_processor_from_template.py [-h] -i INPUT -o OUTPUT [--validate-only]
```

Generate Python classes from JSON function schemas

## Options

- `-h, --help`: Show this help message and exit
- `-i INPUT, --input INPUT`: Path to the input JSON schema file
- `-o OUTPUT, --output OUTPUT`: Path to the output Python file
- `--validate-only`: Only validate the schema without generating code
- `--template_path`: Path to the Jinja2 template file (relative to current directory, default: `dependency_module_template.py.jinja`)

## Example Usage

```bash
python schema_generator.py -i sample_processor_schema.json -o generated_processor.py
python schema_generator.py --input sample_processor_schema.json --output processors/my_processor.py
```

## Sample Input - dependency_module_template.py.jinja
```json
{
    "module_name": "_pypdf2_processor",
    "module_docstring": "PDF processing using PyPDF2.\n\n.",
    "imports": ["re", "io"],
    "dependencies_import": "dependencies",
    "dependencies_class": "Dependencies",
    "functions": [
        {
            "name": "extract_metadata",
            "docstring": "Extract metadata from PDF content using PyPDF2.",
            "parameters": [
                {
                    "name": "pdf_content",
                    "type": "bytes",
                    "description": "The PDF content as bytes."
                },
                {
                    "name": "options",
                    "type": "Optional[dict[str, Any]]",
                    "description": "Optional extraction options.",
                    "default": "None"
                }
            ],
            "returns": {
                "type": "dict[str, Any]",
                "description": "Dictionary of metadata."
            },
            "body": "reader = Dependencies.PyPDF2.PdfReader(io.BytesIO(pdf_content))\n    \n    metadata = {\n        'format': 'pdf',\n        'pages': len(reader.pages)\n    }\n    \n    # Extract document info\n    if reader.metadata:\n        if reader.metadata.get('/Title'):\n            metadata['title'] = reader.metadata['/Title']\n        if reader.metadata.get('/Author'):\n            metadata['author'] = reader.metadata['/Author']\n        if reader.metadata.get('/Subject'):\n            metadata['subject'] = reader.metadata['/Subject']\n    \n    return metadata"
        },
        {
            "name": "extract_text",
            "docstring": "Extract plain text content from PDF using PyPDF2.",
            "parameters": [
                {
                    "name": "pdf_content",
                    "type": "bytes",
                    "description": "The PDF content as bytes."
                },
                {
                    "name": "options",
                    "type": "Optional[dict[str, Any]]",
                    "description": "Optional extraction options.",
                    "default": "None"
                }
            ],
            "returns": {
                "type": "str",
                "description": "Plain text extracted from PDF."
            },
            "body": "reader = Dependencies.PyPDF2.PdfReader(io.BytesIO(pdf_content))\n    text_parts = []\n    \n    for page in reader.pages:\n        text_parts.append(page.extract_text())\n    \n    # Join all text and normalize whitespace\n    full_text = ' '.join(text_parts)\n    full_text = re.sub(r'\\s+', ' ', full_text).strip()\n    \n    return full_text"
        },
        {
            "name": "process_pdf",
            "docstring": "Process PDF content using PyPDF2.",
            "parameters": [
                {
                    "name": "file_content",
                    "type": "Any",
                    "description": "The file content to process."
                },
                {
                    "name": "options",
                    "type": "dict[str, Any]",
                    "description": "Processing options."
                }
            ],
            "returns": {
                "type": "tuple[str, dict[str, Any], list[dict[str, Any]]]",
                "description": "Tuple of (text content, metadata, sections)."
            },
            "body": "# Get PDF content as bytes\n    if hasattr(file_content, 'get_as_bytes'):\n        pdf_content = file_content.get_as_bytes()\n    else:\n        pdf_content = bytes(file_content)\n    \n    # Extract metadata\n    metadata = extract_metadata(pdf_content, options)\n    \n    # Extract text content\n    text = extract_text(pdf_content, options)\n    \n    # Create basic sections\n    sections = [{\n        'type': 'body',\n        'content': text\n    }]\n    \n    return text, metadata, sections"
        }
    ]
}
```