# OpenFDA API Integration Guide

This document outlines the OpenFDA APIs available for medical device information retrieval and validation, specifically for our 510(k) agent system.

## Overview

OpenFDA provides comprehensive APIs for accessing FDA medical device data, including 510(k) submissions, device classifications, recalls, and registration information. All data spans from 1976 to present with regular updates.

**Important Disclaimer**: Do not rely on openFDA to make decisions regarding medical care. Always speak to your health provider about the risks and benefits of FDA-regulated products.

## Available APIs

### 1. Device 510(k) API
**Purpose**: Access premarket notification applications for medical devices
**Documentation**: https://open.fda.gov/apis/device/510k/
**Endpoint**: `https://api.fda.gov/device/510k.json`

**Key Features**:
- Details about specific medical device products and original sponsors
- Administrative and decision information for 510(k) applications
- Receipt and decision dates
- Harmonized identifiers across different datasets
- Coverage: 1976 to present
- Update frequency: Monthly

**Input Parameters** (typical openFDA query structure):
- `search`: Query string for device name, product code, sponsor, etc.
- `limit`: Number of results to return (max 1000)
- `skip`: Number of results to skip for pagination
- `count`: Field to count results by

**Output Structure**:
- Product details and specifications
- Sponsor information
- Administrative tracking data
- Receipt and decision dates
- Cross-referenced identifiers
- **k_number**: Critical for PDF document access
- **statement_or_summary**: Indicates if "Summary" or "Statement" document available

### 2. Device Classification API
**Purpose**: Medical device classification information by regulatory category
**Documentation**: https://open.fda.gov/apis/device/classification/
**Endpoint**: `https://api.fda.gov/device/classification.json`

**Key Features**:
- Approximately 1,700 different device types
- Grouped into 16 medical specialty panels
- Classification into three regulatory classes (I, II, III) based on safety and effectiveness
- Coverage: 1976 to present
- Update frequency: Monthly

**Input Parameters**:
- `search`: Query by device name, product code, medical specialty panel
- `limit`: Number of results to return
- `skip`: Pagination offset
- `count`: Field aggregation

**Output Structure**:
- Device names and generic categories
- Product codes (FDA identifier for device category)
- Medical specialty panel assignment
- Regulatory classification level (Class I, II, or III)
- FDA regulation number

### 3. Device Recall API
**Purpose**: Medical device recall and safety information
**Documentation**: https://open.fda.gov/apis/device/recall/
**Endpoint**: `https://api.fda.gov/device/recall.json`

**Key Features**:
- Recalls are actions taken to address problems with medical devices that violate FDA law
- Covers defective devices or those posing health risks
- Coverage: 2002 to present
- Update frequency: Weekly

**Input Parameters**:
- `search`: Query by device name, manufacturer, recall classification
- `limit`: Number of results to return
- `skip`: Pagination offset
- `count`: Field aggregation

**Output Structure**:
- Recall classification and severity
- Device identification information
- Manufacturer details
- Recall initiation dates
- Description of the problem and corrective action

### 4. Device Registration and Listing API
**Purpose**: Device registration and listing information
**Documentation**: https://open.fda.gov/apis/device/registrationlisting/
**Endpoint**: `https://api.fda.gov/device/registrationlisting.json`

**Key Features**:
- Registration details for medical device establishments
- Device listing information
- Manufacturer and facility information
- Update frequency: Regular updates

**Input Parameters**:
- `search`: Query by establishment name, device name, registration number
- `limit`: Number of results to return
- `skip`: Pagination offset
- `count`: Field aggregation

**Output Structure**:
- Establishment registration information
- Device listing details
- Manufacturer contact information
- Registration numbers and dates

### 5. Device PMA (Premarket Approval) API
**Purpose**: Premarket approval applications for Class III medical devices
**Documentation**: https://open.fda.gov/apis/device/pma/
**Endpoint**: `https://api.fda.gov/device/pma.json`

**Key Features**:
- Class III medical device premarket approvals
- Administrative and decision information
- Coverage: 1976 to present
- Update frequency: Monthly

**Input Parameters**:
- `search`: Query by device name, applicant, PMA number
- `limit`: Number of results to return
- `skip`: Pagination offset
- `count`: Field aggregation

**Output Structure**:
- PMA application details
- Applicant information
- Decision dates and status
- Device specifications
- Administrative tracking

## Integration Strategy for 510(k) Agent System

### Step 0: Predicate Device Discovery
1. **Primary Search**: Use Device 510(k) API to find cleared devices by keyword
2. **Classification Filtering**: Use Device Classification API to ensure same device category
3. **Safety Validation**: Cross-reference with Device Recall API to exclude recalled devices
4. **Additional Details**: Use Registration API for supplementary device information

### Decision Point Validation
- **Legal Status**: Verify through 510(k) API that devices are cleared (not withdrawn)
- **Classification**: Confirm appropriate regulatory class through Classification API
- **Safety History**: Check Recall API for any safety issues

## API Query Examples

### Basic 510(k) Search
```bash
curl "https://api.fda.gov/device/510k.json?search=device_name:catheter&limit=10"
```

### Classification Lookup
```bash
curl "https://api.fda.gov/device/classification.json?search=device_name:catheter&limit=5"
```

### Recall Check
```bash
curl "https://api.fda.gov/device/recall.json?search=product_description:catheter&limit=5"
```

## Accessing 510(k) PDF Documents

### Direct PDF Access Pattern
Once you have a k_number from the API response, construct the PDF URL:
```
https://www.accessdata.fda.gov/cdrh_docs/pdf[YY]/[K_NUMBER].pdf
```

Where:
- `[YY]` = Last 2 digits of year from k_number (e.g., "07" from "K072240")
- `[K_NUMBER]` = Full k_number from API response

### Example:
```bash
# From API response: "k_number": "K072240"
# PDF URL: https://www.accessdata.fda.gov/cdrh_docs/pdf7/K072240.pdf

curl -o K072240.pdf "https://www.accessdata.fda.gov/cdrh_docs/pdf7/K072240.pdf"
```

### Automated PDF Retrieval Function
```bash
# Function to get PDF URL from k_number
get_510k_pdf_url() {
    local k_number="$1"
    # Extract year digits (positions 2-3 from k_number like K072240)
    local year_digits="${k_number:1:2}"
    echo "https://www.accessdata.fda.gov/cdrh_docs/pdf${year_digits}/${k_number}.pdf"
}

# Usage:
# pdf_url=$(get_510k_pdf_url "K072240")
# curl -o document.pdf "$pdf_url"
```

### Important Notes:
- Check `statement_or_summary` field - only devices with "Summary" or "Statement" will have PDFs
- **PDF URL Year Pattern**: FDA uses specific year digit pattern in URLs
  - **2000-2009**: Single digit (pdf2/, pdf3/, ..., pdf9/)
  - **2010+**: Two digits (pdf10/, pdf11/, ..., pdf23/, pdf24/)
  - Examples: K022317 (2002) → pdf2/, K181690 (2018) → pdf18/
- **PDF Access Requirements**: 
  - Use realistic User-Agent header to avoid abuse detection
  - Standard requests library works with proper headers
  - Without User-Agent: triggers Akamai anti-bot protection
  - Rate limiting recommended for bulk downloads

## Rate Limits and Best Practices
- OpenFDA has rate limiting - check current limits in documentation
- Use appropriate pagination for large result sets
- Cache results to minimize API calls
- Handle API errors gracefully with retry logic
- Consider batch processing for multiple device queries

## Additional Resources
- **Main OpenFDA Documentation**: https://open.fda.gov/apis/
- **Query Syntax Guide**: https://open.fda.gov/apis/query-syntax/
- **Rate Limiting Information**: Check current openFDA documentation for latest limits