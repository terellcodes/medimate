#!/usr/bin/env python3
"""
510(k) PDF Retrieval Script

This script searches the openFDA 510(k) database for medical devices matching a search term,
and downloads the corresponding 510(k) PDF documents from FDA's database.

Features:
- Searches openFDA API for device matches
- Filters for devices with available summary documents
- Correctly handles FDA's year-based URL pattern
- Downloads PDFs with proper user-agent headers
- Robust error handling and logging

Usage:
    python fetch_510k_pdf.py "search term"
    python fetch_510k_pdf.py "catheter"
    python fetch_510k_pdf.py "insulin pump"
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
OPENFDA_510K_URL = "https://api.fda.gov/device/510k.json"
FDA_PDF_BASE_URL = "https://www.accessdata.fda.gov/cdrh_docs"
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename by removing/replacing invalid characters.
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra whitespace and limit length
    filename = re.sub(r'\s+', '_', filename.strip())
    return filename[:100]  # Limit filename length

def search_510k_devices(search_term, limit=10):
    """
    Search the openFDA 510(k) database for devices matching the search term.
    
    Args:
        search_term (str): Search term for device name
        limit (int): Number of results to return
    
    Returns:
        dict: API response data
    """
    try:
        # Construct search query
        search_query = f'device_name:"{search_term}"'
        params = {
            'search': search_query,
            'limit': limit
        }
        
        logger.info(f'Searching for devices matching: "{search_term}"')
        response = requests.get(OPENFDA_510K_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'results' not in data or len(data['results']) == 0:
            logger.warning(f"No devices found matching: {search_term}")
            return None
        
        logger.info(f"Found {len(data['results'])} device(s)")
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {e}")
        return None

def extract_device_info(device_data):
    """
    Extract relevant information from a device record.
    
    Args:
        device_data (dict): Device record from API response
    
    Returns:
        dict: Extracted device information
    """
    try:
        k_number = device_data.get('k_number')
        if not k_number:
            logger.error("No k_number found in device data")
            return None
        
        # Extract year digits from k_number with correct FDA URL pattern
        if len(k_number) < 3:
            logger.error(f"Invalid k_number format: {k_number}")
            return None
        
        # Extract 2-digit year from k_number (positions 2-3)
        two_digit_year = k_number[1:3]
        
        # FDA URL pattern: 00-09 use single digit (0,1,2...9), 10+ use two digits (10,11,12...)
        if two_digit_year.startswith('0'):
            year_digits = two_digit_year[1]  # "07" -> "7", "02" -> "2"
        else:
            year_digits = two_digit_year  # "22" -> "22", "18" -> "18"
        
        device_info = {
            'k_number': k_number,
            'year_digits': year_digits,
            'device_name': device_data.get('device_name', 'Unknown'),
            'applicant': device_data.get('applicant', 'Unknown'),
            'decision_date': device_data.get('decision_date', 'Unknown'),
            'decision_description': device_data.get('decision_description', 'Unknown'),
            'statement_or_summary': device_data.get('statement_or_summary', 'Unknown')
        }
        
        logger.info(f"Device: {device_info['device_name']} ({k_number})")
        logger.info(f"Applicant: {device_info['applicant']}")
        logger.info(f"Decision Date: {device_info['decision_date']}")
        logger.info(f"Document Type: {device_info['statement_or_summary']}")
        
        return device_info
        
    except Exception as e:
        logger.error(f"Failed to extract device info: {e}")
        return None

def construct_pdf_url(k_number, year_digits):
    """
    Construct the PDF URL based on k_number and year digits.
    
    Args:
        k_number (str): The k_number (e.g., "K072240")
        year_digits (str): Year digits (e.g., "07")
    
    Returns:
        str: PDF URL
    """
    pdf_url = f"{FDA_PDF_BASE_URL}/pdf{year_digits}/{k_number}.pdf"
    logger.info(f"PDF URL: {pdf_url}")
    return pdf_url

def download_pdf(pdf_url, device_info, output_dir):
    """
    Download the PDF from the given URL.
    
    Args:
        pdf_url (str): URL of the PDF to download
        device_info (dict): Device information for filename generation
        output_dir (Path): Directory to save the PDF
    
    Returns:
        tuple: (success: bool, filepath: str or None, error_message: str or None)
    """
    try:
        # Create filename
        device_name_clean = sanitize_filename(device_info['device_name'])
        filename = f"{device_info['k_number']}_{device_name_clean}.pdf"
        filepath = output_dir / filename
        
        logger.info(f"Downloading PDF from: {pdf_url}")
        
        # Download the PDF with realistic user-agent to avoid abuse detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(pdf_url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            return False, None, "PDF not found (404 error)"
        
        response.raise_for_status()
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the PDF
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Verify file was created and has content
        if filepath.exists() and filepath.stat().st_size > 0:
            logger.info(f"✓ Successfully downloaded: {filepath}")
            return True, str(filepath), None
        else:
            return False, None, "Downloaded file is empty or missing"
        
    except requests.exceptions.RequestException as e:
        return False, None, f"Download failed: {e}"
    except Exception as e:
        return False, None, f"Unexpected error: {e}"

def fetch_510k_pdf(search_term, output_dir=None):
    """
    Main function to search for a device and download its 510(k) PDF.
    
    Args:
        search_term (str): Search term for device name
        output_dir (str or Path, optional): Output directory for PDF
    
    Returns:
        tuple: (success: bool, filepath: str or None, device_info: dict or None)
    """
    if output_dir is None:
        output_dir = DATA_DIR
    else:
        output_dir = Path(output_dir)
    
    # Step 1: Search for devices
    api_data = search_510k_devices(search_term)
    if not api_data or not api_data.get('results'):
        return False, None, None
    
    # Step 2: Try multiple devices until we find one with an accessible PDF
    logger.info(f"Found {len(api_data['results'])} devices, checking for accessible PDFs...")
    
    for i, device in enumerate(api_data['results']):
        device_info = extract_device_info(device)
        if not device_info:
            continue
            
        # Check if device has a summary document (more likely to have PDF)
        statement_or_summary = device_info.get('statement_or_summary', '').strip()
        logger.info(f"Device {i+1}: {device_info['device_name']} ({device_info['k_number']}) - Document type: '{statement_or_summary}'")
        
        # Skip devices without summary documents
        if not statement_or_summary or statement_or_summary.lower() not in ['summary', 'statement']:
            logger.info(f"Skipping {device_info['k_number']} - no summary document indicated")
            continue
        
        # Step 3: Construct PDF URL
        pdf_url = construct_pdf_url(device_info['k_number'], device_info['year_digits'])
        
        # Step 4: Try to download PDF
        success, filepath, error_msg = download_pdf(pdf_url, device_info, output_dir)
        
        if success:
            logger.info(f"✓ Successfully found and downloaded PDF for {device_info['k_number']}")
            return True, filepath, device_info
        else:
            logger.warning(f"Failed to download PDF for {device_info['k_number']}: {error_msg}")
            continue
    
    # If we get here, none of the devices had accessible PDFs
    logger.error("No accessible PDFs found for any of the matching devices")
    return False, None, None

def main():
    """
    Command line interface for the script.
    """
    parser = argparse.ArgumentParser(
        description="Download 510(k) PDF documents from openFDA database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_510k_pdf.py "catheter"
  python fetch_510k_pdf.py "cardiac filter"
  python fetch_510k_pdf.py "insulin pump"
        """
    )
    
    parser.add_argument(
        'search_term',
        help='Search term to find devices (e.g., "catheter", "cardiac filter")'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help=f'Output directory for downloaded PDFs (default: {DATA_DIR})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        success, filepath, device_info = fetch_510k_pdf(args.search_term, args.output_dir)
        
        if success:
            print(f"\n✓ SUCCESS!")
            print(f"Downloaded: {filepath}")
            if device_info:
                print(f"Device: {device_info['device_name']}")
                print(f"K-Number: {device_info['k_number']}")
                print(f"Applicant: {device_info['applicant']}")
            sys.exit(0)
        else:
            print(f"\n✗ FAILED!")
            if device_info:
                print(f"Found device but couldn't download PDF: {device_info['device_name']} ({device_info['k_number']})")
            else:
                print(f"No devices found for search term: '{args.search_term}'")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()