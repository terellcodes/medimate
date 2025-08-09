import logging
import re
import aiohttp
from pathlib import Path
from typing import Optional, Dict
from services.storage_service import get_storage_service
from models.schemas.predicate_discovery import (
    PredicateSearchParams,
    DeviceInfo,
    DownloadedDevice,
    PredicateSearchSummary,
    PredicateDiscoveryResult,
    BulkIFUResult,
    IFUExtraction
)

logger = logging.getLogger(__name__)

# Constants
OPENFDA_510K_URL = "https://api.fda.gov/device/510k.json"
FDA_PDF_BASE_URL = "https://www.accessdata.fda.gov/cdrh_docs"


class PredicateDiscoveryService:
    """Service for discovering and retrieving 510(k) predicate devices."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the service with optional data directory."""
        # Storage service will be lazy-loaded when needed
        self._storage_service = None
        
        # Keep data_dir for backward compatibility
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "project" / "data"
        else:
            self.data_dir = Path(data_dir)
    
    @property
    def storage_service(self):
        """Lazy-load storage service."""
        if self._storage_service is None:
            self._storage_service = get_storage_service()
            if self._storage_service:
                logger.info("🌥️  R2 storage service loaded successfully")
            else:
                logger.info("📁 Using local storage (R2 not configured)")
                # Ensure local directory exists
                self.data_dir.mkdir(parents=True, exist_ok=True)
        return self._storage_service

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

    async def extract_bulk_ifu(self, k_numbers: list[str]) -> BulkIFUResult:
        """
        Extract IFU (Indications for Use) from multiple device PDFs.
        
        Args:
            k_numbers: List of K-numbers to process
            
        Returns:
            BulkIFUResult with extracted IFU information for each device
        """
        logger.info(f"Starting bulk IFU extraction for {len(k_numbers)} devices")
        
        extractions = []
        status_counts = {
            'success': 0,
            'no_pdf': 0,
            'extraction_failed': 0,
            'no_ifu_found': 0
        }
        
        # Process each K-number
        for k_number in k_numbers:
            try:
                extraction = await self._extract_single_ifu(k_number)
                extractions.append(extraction)
                status_counts[extraction.extraction_status] += 1
                
            except Exception as e:
                logger.error(f"Failed to process K-number {k_number}: {e}")
                extractions.append(IFUExtraction(
                    k_number=k_number,
                    device_name="Unknown",
                    extraction_status="extraction_failed",
                    error_message=str(e)
                ))
                status_counts['extraction_failed'] += 1
        
        logger.info(f"Bulk IFU extraction completed. Success: {status_counts['success']}, Failed: {sum(status_counts.values()) - status_counts['success']}")
        
        return BulkIFUResult(
            extractions=extractions,
            summary=status_counts,
            total_processed=len(k_numbers)
        )

    async def _extract_single_ifu(self, k_number: str, save_pdf: bool = True) -> IFUExtraction:
        """Extract IFU from a single device PDF."""
        try:
            # First, try to get device info from FDA API
            device_info = await self._get_device_info_by_k_number(k_number)
            device_name = device_info.get('device_name', 'Unknown') if device_info else 'Unknown'
            
            # Try to download and process the PDF
            year_digits = self._get_year_digits(k_number)
            if not year_digits:
                return IFUExtraction(
                    k_number=k_number,
                    device_name=device_name,
                    extraction_status="no_pdf",
                    error_message="Could not determine PDF URL pattern"
                )
            
            pdf_url = f"{FDA_PDF_BASE_URL}/pdf{year_digits}/{k_number}.pdf"
            
            # Download PDF content
            pdf_content = await self._download_pdf_content(pdf_url)
            if not pdf_content:
                return IFUExtraction(
                    k_number=k_number,
                    device_name=device_name,
                    extraction_status="no_pdf",
                    error_message="PDF not accessible or not found",
                    pdf_url=pdf_url
                )
            
            # Save PDF to storage if requested
            pdf_save_success = True
            storage_url = None
            if save_pdf:
                if self.storage_service:
                    # Use R2 storage
                    logger.info(f"🌐 Using R2 cloud storage for {k_number} (size: {len(pdf_content)} bytes)")
                    try:
                        result = await self.storage_service.upload_pdf(
                            k_number=k_number,
                            pdf_content=pdf_content,
                            metadata={'device_name': device_name, 'fda_pdf_url': pdf_url}
                        )
                        if result['success']:
                            storage_url = result['url']
                            logger.info(f"✅ Successfully saved PDF for {k_number} to R2")
                            logger.info(f"   📍 Storage URL: {storage_url}")
                            logger.info(f"   📦 Bucket: {result['bucket']}")
                            logger.info(f"   🔑 Key: {result['key']}")
                        else:
                            logger.error(f"❌ Failed to save PDF to R2: {result.get('error')}")
                            pdf_save_success = False
                    except Exception as e:
                        logger.error(f"❌ Exception saving PDF for {k_number} to R2: {e}")
                        pdf_save_success = False
                else:
                    # Fallback to local storage
                    logger.warning(f"⚠️  R2 storage not configured, using local storage for {k_number}")
                    try:
                        pdf_filename = f"{k_number}.pdf"
                        pdf_filepath = self.data_dir / pdf_filename
                        
                        with open(pdf_filepath, 'wb') as f:
                            f.write(pdf_content)
                        
                        logger.info(f"💾 Saved PDF for {k_number} to local storage: {pdf_filepath}")
                    except Exception as e:
                        logger.error(f"❌ Failed to save PDF for {k_number} locally: {e}")
                        pdf_save_success = False
            
            # Process PDF and extract IFU
            ifu_text = await self._extract_ifu_from_pdf_content(pdf_content)
            
            if not ifu_text or ifu_text.strip() in ["Unknown", "Not specified", ""]:
                return IFUExtraction(
                    k_number=k_number,
                    device_name=device_name,
                    extraction_status="no_ifu_found",
                    error_message="IFU section not found in document" + ("" if pdf_save_success else " (Note: PDF download succeeded but storage save failed)"),
                    pdf_url=pdf_url
                )
            
            # Success case - include PDF save status in error message if applicable
            error_message = None if pdf_save_success else "PDF download succeeded but storage save failed"
            
            return IFUExtraction(
                k_number=k_number,
                device_name=device_name,
                ifu_text=ifu_text,
                extraction_status="success",
                error_message=error_message,
                pdf_url=storage_url or pdf_url  # Use storage URL if available, else FDA URL
            )
            
        except Exception as e:
            logger.error(f"Failed to extract IFU for {k_number}: {e}")
            return IFUExtraction(
                k_number=k_number,
                device_name="Unknown",
                extraction_status="extraction_failed",
                error_message=str(e)
            )

    async def _get_device_info_by_k_number(self, k_number: str) -> Optional[Dict]:
        """Get device information from FDA API by K-number."""
        try:
            params = {
                'search': f'k_number:"{k_number}"',
                'limit': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(OPENFDA_510K_URL, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('results'):
                            return data['results'][0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get device info for {k_number}: {e}")
            return None

    async def _download_pdf_content(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
            return None
            
        except Exception as e:
            logger.error(f"Failed to download PDF from {pdf_url}: {e}")
            return None

    async def _extract_ifu_from_pdf_content(self, pdf_content: bytes) -> Optional[str]:
        """Extract IFU text from PDF content using AI-powered extraction."""
        import tempfile
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams
        from langchain_openai.embeddings import OpenAIEmbeddings
        from config.settings import get_settings
        
        try:
            # Save PDF content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_path = temp_file.name
            
            try:
                # Load and process PDF
                loader = PyPDFLoader(temp_path)
                documents = loader.load()
                
                # Split into chunks
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(documents)
                
                # Create temporary vector store
                temp_client = QdrantClient(":memory:")
                collection_name = f"temp_ifu_{hash(pdf_content) % 10000}"
                
                temp_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                
                settings = get_settings()
                embedding_model = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    openai_api_key=settings.OPENAI_API_KEY
                )
                
                vector_store = QdrantVectorStore(
                    client=temp_client,
                    collection_name=collection_name,
                    embedding=embedding_model
                )
                
                # Add documents to vector store
                await vector_store.aadd_documents(documents=chunks)
                
                # Create retriever and extract IFU
                retriever = vector_store.as_retriever(search_kwargs={"k": 5})
                
                # Use IFU-specific queries
                ifu_queries = [
                    "indication for use",
                    "indications for use", 
                    "intended use",
                    "indication:",
                    "indications:",
                    "use:",
                    "purpose"
                ]
                
                # Search for IFU-related content
                ifu_docs = []
                for query in ifu_queries:
                    docs = await retriever.ainvoke(query)
                    ifu_docs.extend(docs)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_docs = []
                for doc in ifu_docs:
                    if doc.page_content not in seen:
                        seen.add(doc.page_content)
                        unique_docs.append(doc)
                
                if not unique_docs:
                    return None
                
                # Combine relevant content
                combined_text = "\n\n".join([doc.page_content for doc in unique_docs[:3]])  # Use top 3 relevant chunks
                
                # Use AI to extract IFU from combined text
                from langchain_openai import ChatOpenAI
                
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                
                prompt = f"""
Extract the Indication for Use (IFU) or Intended Use statement from the following text. Look for:
- Indications for Use
- Intended Use
- Purpose of the device
- What the device is used for
- Clinical indication

Return the complete indication statement exactly as written in the document.
If no clear indication is found, return "Not specified".

Text:
{combined_text}

Indication for Use:"""

                response = await llm.ainvoke(prompt)
                return response.content.strip()
                
            finally:
                # Clean up temp file
                import os
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Failed to extract IFU from PDF content: {e}")
            return None

    async def load_predicate_pdf_to_vector_store(self, k_number: str) -> bool:
        """
        Load a specific predicate device PDF into its own vector store collection.
        
        Args:
            k_number: The K-number of the predicate device
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            # Import vector store manager
            from core.vector_store import vector_store_manager
            
            # Check if collection already exists and has content
            if vector_store_manager.predicate_collection_exists(k_number):
                collection_info = vector_store_manager.client.get_collection(
                    vector_store_manager.get_predicate_collection_name(k_number)
                )
                if collection_info.points_count > 0:
                    logger.info(f"Collection for {k_number} already exists with {collection_info.points_count} points")
                    return True
            
            # Try to load PDF from R2 first, then fall back to local
            pdf_filepath = None
            
            # Check R2 storage first
            if self.storage_service:
                logger.info(f"🔍 Checking R2 storage for {k_number}...")
                if await self.storage_service.pdf_exists(k_number):
                    logger.info(f"✅ Found {k_number} in R2 storage, will load from cloud")
                    # load_predicate_to_collection will handle R2 retrieval
                    pdf_filepath = None
                else:
                    logger.info(f"⚠️  {k_number} not found in R2, checking local storage...")
                    # Fall back to local storage
                    local_path = self.data_dir / f"{k_number}.pdf"
                    if local_path.exists():
                        logger.info(f"✅ Found {k_number} in local storage at {local_path}")
                        pdf_filepath = str(local_path)
                    else:
                        logger.error(f"❌ PDF not found for {k_number} in R2 or local storage")
                        return False
            else:
                logger.warning(f"⚠️  R2 storage not configured, checking local storage only...")
                # Fall back to local storage
                local_path = self.data_dir / f"{k_number}.pdf"
                if local_path.exists():
                    logger.info(f"✅ Found {k_number} in local storage at {local_path}")
                    pdf_filepath = str(local_path)
                else:
                    logger.error(f"❌ PDF not found for {k_number} in local storage")
                    return False
            
            # Load the PDF into its own collection
            summary = await vector_store_manager.load_predicate_to_collection(k_number, pdf_filepath)
            
            if summary.get("status") == "exists":
                logger.info(f"Collection for {k_number} already existed")
                return True
            
            logger.info(f"Successfully loaded {k_number} PDF into dedicated collection with {summary.get('chunks_loaded', 0)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load {k_number} PDF into vector store: {e}")
            return False


# Global service instance
predicate_discovery_service = PredicateDiscoveryService()