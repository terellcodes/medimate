"""
Configuration for document field extraction.
Each field defines queries to search for and a prompt for LLM extraction.
"""

EXTRACTION_CONFIG = {
    "device_name": {
        "queries": [
            "device name",
            "trade name", 
            "product name",
            "device:",
            "name:",
            "product:"
        ],
        "prompt": """
Extract the device name or trade name from the following text. Look for:
- Trade Name
- Device Name  
- Product Name
- Commercial name of the device

Return only the device name, no additional text or explanation.
If multiple names are found, return the primary/trade name.
If no clear device name is found, return "Unknown".

Text:
{text}

Device Name:"""
    },
    
    "manufacturer": {
        "queries": [
            "manufacturer",
            "company", 
            "submitter",
            "corporation",
            "inc",
            "ltd",
            "llc"
        ],
        "prompt": """
Extract the manufacturer or company name from the following text. Look for:
- Manufacturer
- Company name
- Submitter  
- Corporation name
- Business entity name

Return only the company/manufacturer name, no additional text.
If no clear manufacturer is found, return "Unknown".

Text:
{text}

Manufacturer:"""
    },
    
    "indication_of_use": {
        "queries": [
            "indication for use",
            "indications for use", 
            "intended use",
            "indication:",
            "indications:",
            "use:",
            "purpose"
        ],
        "prompt": """
Extract the indication for use or intended use statement from the following text. Look for:
- Indications for Use
- Intended Use
- Purpose of the device
- What the device is used for
- Clinical indication

Return the complete indication statement exactly as written in the document.
If no clear indication is found, return "Not specified".

Text:
{text}

Indication for Use:"""
    },
    
    "description": {
        "queries": [
            "description",
            "summary",
            "overview", 
            "device description",
            "product description",
            "what is",
            "device summary"
        ],
        "prompt": """
Extract a description or summary of the device from the following text. Look for:
- Device description
- Product summary
- Overview of the device
- What the device does
- Device characteristics

Return a concise description of the device and its function.
If no clear description is found, return a brief description based on the device name and context.

Text:
{text}

Description:"""
    }
}

# Easy way to add new fields
def add_extraction_field(field_name: str, queries: list, prompt: str):
    """Add a new field to the extraction configuration."""
    EXTRACTION_CONFIG[field_name] = {
        "queries": queries,
        "prompt": prompt
    }

# Example of how to extend:
# add_extraction_field(
#     "clearance_date", 
#     ["clearance date", "FDA clearance", "510k clearance", "approval date"],
#     "Extract the FDA clearance date from this text..."
# )