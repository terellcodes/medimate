#!/usr/bin/env python3
"""
510(k) PDF Retrieval Script

This script searches the openFDA 510(k) database for medical devices matching a search term,
and downloads the corresponding 510(k) PDF documents from FDA's database.

Features:
- Searches openFDA API for device matches
- Downloads multiple PDFs (configurable limit)
- Returns comprehensive metadata for all found devices
- Filters for devices with available summary documents
- Correctly handles FDA's year-based URL pattern
- Downloads PDFs with proper user-agent headers
- Robust error handling and logging

Usage:
    python fetch_510k_pdf.py "search term"
    python fetch_510k_pdf.py "catheter" --max-downloads 3
    python fetch_510k_pdf.py "insulin pump" --list-all
    python fetch_510k_pdf.py "defibrillator" -n 5 -l -v
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

def search_510k_devices(search_term=None, product_code=None, limit=10):
    """
    Search the openFDA 510(k) database for devices.
    
    Args:
        search_term (str, optional): Search term for device name
        product_code (str, optional): FDA product code to filter by
        limit (int): Number of results to return
    
    Returns:
        dict: API response data
    """
    try:
        # Construct search query based on parameters
        if product_code and search_term:
            # Combined search for most specific results
            search_query = f'product_code:"{product_code}" AND device_name:"{search_term}"'
            logger.info(f'Searching for devices with product code "{product_code}" and name matching "{search_term}"')
        elif product_code:
            # Product code only - category specific
            search_query = f'product_code:"{product_code}"'
            logger.info(f'Searching for devices with product code: "{product_code}"')
        elif search_term:
            # Device name only - broad search
            search_query = f'device_name:"{search_term}"'
            logger.info(f'Searching for devices matching: "{search_term}"')
        else:
            logger.error("Must provide either search_term or product_code")
            return None
        
        params = {
            'search': search_query,
            'limit': limit
        }
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
            'statement_or_summary': device_data.get('statement_or_summary', 'Unknown'),
            'product_code': device_data.get('product_code', 'Unknown')
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

def fetch_510k_pdf(search_term=None, product_code=None, output_dir=None, max_downloads=1):
    """
    Main function to search for devices and download their 510(k) PDFs.
    
    Args:
        search_term (str, optional): Search term for device name
        product_code (str, optional): FDA product code to filter by
        output_dir (str or Path, optional): Output directory for PDF
        max_downloads (int): Maximum number of PDFs to download
    
    Returns:
        dict: {
            'downloads': [list of successful downloads],
            'all_devices': [list of all devices found with metadata],
            'summary': {download and search statistics}
        }
    """
    if output_dir is None:
        output_dir = DATA_DIR
    else:
        output_dir = Path(output_dir)
    
    # Step 1: Search for devices
    api_data = search_510k_devices(search_term=search_term, product_code=product_code)
    if not api_data or not api_data.get('results'):
        return {
            'downloads': [],
            'all_devices': [],
            'summary': {
                'total_found': 0, 
                'devices_with_documents': 0,
                'downloads_attempted': 0,
                'downloads_successful': 0, 
                'max_downloads_requested': max_downloads
            }
        }
    
    # Initialize result containers
    downloads = []
    all_devices = []
    downloads_attempted = 0
    
    # Step 2: Process all devices and collect metadata
    logger.info(f"Found {len(api_data['results'])} devices, processing all...")
    
    for i, device in enumerate(api_data['results']):
        device_info = extract_device_info(device)
        if not device_info:
            continue
        
        # Determine if device has 510(k) document available
        statement_or_summary = device_info.get('statement_or_summary', '').strip()
        has_510k_document = bool(statement_or_summary and statement_or_summary.lower() in ['summary', 'statement'])
        
        # Create comprehensive device metadata
        device_metadata = {
            'device_name': device_info['device_name'],
            'applicant': device_info['applicant'],
            'decision_date': device_info['decision_date'],
            'k_number': device_info['k_number'],
            'product_code': device_info.get('product_code', 'Unknown'),
            'has_510k_document': has_510k_document,
            'document_type': statement_or_summary if statement_or_summary else None,
            'decision_description': device_info.get('decision_description')
        }
        all_devices.append(device_metadata)
        
        # Log device information
        doc_status = f"Document: {statement_or_summary}" if statement_or_summary else "No document"
        logger.info(f"Device {i+1}: {device_info['device_name']} ({device_info['k_number']}) - {doc_status}")
        
        # Try to download PDF if we haven't reached the limit and device has document
        if len(downloads) < max_downloads and has_510k_document:
            downloads_attempted += 1
            
            # Step 3: Construct PDF URL
            pdf_url = construct_pdf_url(device_info['k_number'], device_info['year_digits'])
            
            # Step 4: Try to download PDF
            success, filepath, error_msg = download_pdf(pdf_url, device_info, output_dir)
            
            if success:
                download_info = {
                    'device_name': device_info['device_name'],
                    'k_number': device_info['k_number'],
                    'applicant': device_info['applicant'],
                    'decision_date': device_info['decision_date'],
                    'filepath': filepath,
                    'pdf_url': pdf_url
                }
                downloads.append(download_info)
                logger.info(f"✓ Successfully downloaded PDF {len(downloads)}/{max_downloads}: {device_info['k_number']}")
            else:
                logger.warning(f"Failed to download PDF for {device_info['k_number']}: {error_msg}")
    
    # Create summary
    summary = {
        'total_found': len(all_devices),
        'devices_with_documents': len([d for d in all_devices if d['has_510k_document']]),
        'downloads_attempted': downloads_attempted,
        'downloads_successful': len(downloads),
        'max_downloads_requested': max_downloads
    }
    
    return {
        'downloads': downloads,
        'all_devices': all_devices,
        'summary': summary
    }

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
        nargs='?',  # Make optional since we can use product code instead
        help='Search term to find devices (e.g., "catheter", "cardiac filter")'
    )
    
    parser.add_argument(
        '--product-code', '-p',
        type=str,
        help='FDA product code to filter by (e.g., "DYB" for cardiac catheters)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help=f'Output directory for downloaded PDFs (default: {DATA_DIR})'
    )
    
    parser.add_argument(
        '--max-downloads', '-n',
        type=int,
        default=1,
        help='Maximum number of PDFs to download (default: 1)'
    )
    
    parser.add_argument(
        '--list-all', '-l',
        action='store_true',
        help='List all found devices even if no PDFs are downloaded'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate that at least one search parameter is provided
    if not args.search_term and not args.product_code:
        parser.error("Must provide either search_term or --product-code")
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        result = fetch_510k_pdf(
            search_term=args.search_term,
            product_code=args.product_code,
            output_dir=args.output_dir,
            max_downloads=args.max_downloads
        )
        
        # Display summary
        summary = result['summary']
        downloads = result['downloads']
        all_devices = result['all_devices']
        
        print(f"\n📊 SEARCH RESULTS")
        print(f"Search term: '{args.search_term}'")
        print(f"Total devices found: {summary['total_found']}")
        print(f"Devices with 510(k) documents: {summary['devices_with_documents']}")
        print(f"Downloads attempted: {summary['downloads_attempted']}")
        print(f"Downloads successful: {summary['downloads_successful']}")
        
        # Display successful downloads
        if downloads:
            print(f"\n✅ SUCCESSFUL DOWNLOADS ({len(downloads)}):")
            for i, download in enumerate(downloads, 1):
                print(f"  {i}. {download['device_name']}")
                print(f"     K-Number: {download['k_number']}")
                print(f"     Applicant: {download['applicant']}")
                print(f"     Date: {download['decision_date']}")
                print(f"     File: {download['filepath']}")
                print()
        
        # Display all devices if requested or if verbose
        if args.list_all or args.verbose or not downloads:
            print(f"\n📋 ALL DEVICES FOUND ({len(all_devices)}):")
            for i, device in enumerate(all_devices, 1):
                doc_indicator = "✓" if device['has_510k_document'] else "✗"
                doc_type = f" ({device['document_type']})" if device['document_type'] else ""
                
                print(f"  {i}. {doc_indicator} {device['device_name']}")
                print(f"     K-Number: {device['k_number']}")
                print(f"     Applicant: {device['applicant']}")
                print(f"     Date: {device['decision_date']}")
                print(f"     510(k) Document: {'Yes' if device['has_510k_document'] else 'No'}{doc_type}")
                print()
        
        # Exit with appropriate status
        if downloads:
            sys.exit(0)
        else:
            print(f"✗ No PDFs were downloaded")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()