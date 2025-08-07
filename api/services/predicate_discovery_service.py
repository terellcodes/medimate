import logging
import re
import aiohttp
from pathlib import Path
from typing import Optional, Dict
from models.schemas.predicate_discovery import (
    PredicateSearchParams,
    DeviceInfo,
    DownloadedDevice,
    PredicateSearchSummary,
    PredicateDiscoveryResult
)

logger = logging.getLogger(__name__)

# Constants
OPENFDA_510K_URL = "https://api.fda.gov/device/510k.json"
FDA_PDF_BASE_URL = "https://www.accessdata.fda.gov/cdrh_docs"


class PredicateDiscoveryService:
    """Service for discovering and retrieving 510(k) predicate devices."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the service with optional data directory."""
        if data_dir is None:
            # Default to project data directory
            self.data_dir = Path(__file__).parent.parent.parent / "project" / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def discover_predicates(self, search_params: PredicateSearchParams) -> PredicateDiscoveryResult:
        """
        Main entry point for predicate discovery process.
        
        Args:
            search_params: Search parameters including search term, product code, etc.
            
        Returns:
            Complete discovery result with devices and downloads
        """
        logger.info(f"Starting predicate discovery with params: {search_params}")
        
        # Step 1: Search for devices
        devices_data = await self._search_devices_api(search_params)
        
        if not devices_data or not devices_data.get('results'):
            return PredicateDiscoveryResult(
                downloads=[],
                all_devices=[],
                devices_with_510k=[],
                devices_without_510k=[],
                summary=PredicateSearchSummary(
                    total_found=0,
                    devices_with_documents=0,
                    downloads_attempted=0,
                    downloads_successful=0,
                    max_downloads_requested=search_params.max_downloads
                ),
                search_params=search_params
            )
        
        # Step 2: Process all devices and collect metadata
        all_devices = []
        devices_with_510k = []
        devices_without_510k = []
        downloads = []
        downloads_attempted = 0
        
        logger.info(f"Found {len(devices_data['results'])} devices, processing all...")
        
        for device in devices_data['results']:
            device_info = self._extract_device_info(device)
            if not device_info:
                continue
            
            all_devices.append(device_info)
            
            # Separate into two lists
            if device_info.has_510k_document:
                devices_with_510k.append(device_info)
            else:
                devices_without_510k.append(device_info)
            
            # Try to download PDF if we haven't reached limit and device has document
            if (len(downloads) < search_params.max_downloads and 
                device_info.has_510k_document):
                
                downloads_attempted += 1
                download_result = await self._download_device_pdf(device_info)
                
                if download_result:
                    downloads.append(download_result)
                    logger.info(f"✓ Downloaded PDF {len(downloads)}/{search_params.max_downloads}: {device_info.k_number}")
                else:
                    logger.warning(f"Failed to download PDF for {device_info.k_number}")
        
        # Sort both lists by decision_date (most recent first)
        devices_with_510k.sort(key=lambda x: self._parse_date(x.decision_date), reverse=True)
        devices_without_510k.sort(key=lambda x: self._parse_date(x.decision_date), reverse=True)
        
        # Create summary
        summary = PredicateSearchSummary(
            total_found=len(all_devices),
            devices_with_documents=len(devices_with_510k),
            downloads_attempted=downloads_attempted,
            downloads_successful=len(downloads),
            max_downloads_requested=search_params.max_downloads
        )
        
        return PredicateDiscoveryResult(
            downloads=downloads,
            all_devices=all_devices,
            devices_with_510k=devices_with_510k,
            devices_without_510k=devices_without_510k,
            summary=summary,
            search_params=search_params
        )

    async def _search_devices_api(self, search_params: PredicateSearchParams) -> Optional[Dict]:
        """Search the openFDA 510(k) database for devices."""
        try:
            # Construct search query based on parameters
            if search_params.product_code and search_params.search_term:
                search_query = f'product_code:"{search_params.product_code}" AND device_name:"{search_params.search_term}"'
            elif search_params.product_code:
                search_query = f'product_code:"{search_params.product_code}"'
            elif search_params.search_term:
                search_query = f'device_name:"{search_params.search_term}"'
            else:
                logger.error("Must provide either search_term or product_code")
                return None
            
            params = {
                'search': search_query,
                'limit': 10  # Fixed limit for API call
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(OPENFDA_510K_URL, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Found {len(data.get('results', []))} devices from API")
                        return data
                    else:
                        logger.error(f"API request failed with status {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    def _extract_device_info(self, device_data: Dict) -> Optional[DeviceInfo]:
        """Extract relevant information from a device record."""
        try:
            k_number = device_data.get('k_number')
            if not k_number or len(k_number) < 3:
                return None
            
            # Determine if device has 510(k) document available
            statement_or_summary = device_data.get('statement_or_summary', '').strip()
            has_510k_document = bool(statement_or_summary and 
                                   statement_or_summary.lower() in ['summary', 'statement'])
            
            return DeviceInfo(
                k_number=k_number,
                device_name=device_data.get('device_name', 'Unknown'),
                applicant=device_data.get('applicant', 'Unknown'),
                decision_date=device_data.get('decision_date', 'Unknown'),
                product_code=device_data.get('product_code', 'Unknown'),
                has_510k_document=has_510k_document,
                document_type=statement_or_summary if statement_or_summary else None,
                decision_description=device_data.get('decision_description', 'Unknown'),
                safety_status="unknown"  # Will be updated when recall checking is added
            )
            
        except Exception as e:
            logger.error(f"Failed to extract device info: {e}")
            return None

    async def _download_device_pdf(self, device_info: DeviceInfo) -> Optional[DownloadedDevice]:
        """Download PDF for a specific device."""
        try:
            # Construct PDF URL
            year_digits = self._get_year_digits(device_info.k_number)
            if not year_digits:
                return None
            
            pdf_url = f"{FDA_PDF_BASE_URL}/pdf{year_digits}/{device_info.k_number}.pdf"
            
            # Generate filename
            device_name_clean = self._sanitize_filename(device_info.device_name)
            filename = f"{device_info.k_number}_{device_name_clean}.pdf"
            filepath = self.data_dir / filename
            
            # Download the PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save the PDF
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        return DownloadedDevice(
                            device_name=device_info.device_name,
                            k_number=device_info.k_number,
                            applicant=device_info.applicant,
                            decision_date=device_info.decision_date,
                            filepath=str(filepath),
                            pdf_url=pdf_url
                        )
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to download PDF for {device_info.k_number}: {e}")
            return None

    def _get_year_digits(self, k_number: str) -> Optional[str]:
        """Extract year digits for PDF URL construction."""
        if len(k_number) < 3:
            return None
        
        # Extract 2-digit year from k_number (positions 2-3)
        two_digit_year = k_number[1:3]
        
        # FDA URL pattern: 00-09 use single digit, 10+ use two digits
        if two_digit_year.startswith('0'):
            return two_digit_year[1]  # "07" -> "7"
        else:
            return two_digit_year     # "22" -> "22"

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be used as a filename."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra whitespace and limit length
        filename = re.sub(r'\s+', '_', filename.strip())
        return filename[:100]  # Limit filename length

    def _parse_date(self, date_str: str):
        """Parse FDA date format safely for sorting."""
        from datetime import datetime
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.min  # Put invalid dates at the end


# Global service instance
predicate_discovery_service = PredicateDiscoveryService()