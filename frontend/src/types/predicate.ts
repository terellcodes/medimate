// TypeScript types for predicate discovery functionality

export interface SearchParams {
  searchTerm?: string;
  productCode?: string;
  maxDownloads: number;
  includeRecalled: boolean;
}

export interface DeviceInfo {
  k_number: string;
  device_name: string;
  applicant: string;
  decision_date: string;
  product_code?: string;
  has_510k_document: boolean;
  document_type?: string;
  decision_description?: string;
  safety_status?: string;
}

// Alias for component compatibility
export interface Device extends DeviceInfo {
  // Add compatibility properties that components expect
  pdf_available?: boolean;
  clearance_type?: string;
  statement?: string;
  recall_status?: string;
}

export interface DownloadedDevice {
  device_name: string;
  k_number: string;
  applicant: string;
  decision_date: string;
  filepath: string;
  pdf_url: string;
}

export interface PredicateSearchSummary {
  total_found: number;
  devices_with_documents: number;
  downloads_attempted: number;
  downloads_successful: number;
  max_downloads_requested: number;
}

export interface PredicateDiscoveryResult {
  downloads: DownloadedDevice[];
  all_devices: DeviceInfo[];
  devices_with_510k: DeviceInfo[];
  devices_without_510k: DeviceInfo[];
  summary: PredicateSearchSummary;
  search_params: SearchParams;
}

export interface PredicateDiscoveryResponse {
  success: boolean;
  result?: PredicateDiscoveryResult;
  error?: string;
}

export interface IFUExtraction {
  k_number: string;
  device_name: string;
  ifu_text?: string;
  extraction_status: 'success' | 'no_pdf' | 'extraction_failed' | 'no_ifu_found';
  error_message?: string;
  pdf_url?: string;
}

export interface BulkIFUResult {
  extractions: IFUExtraction[];
  summary: Record<string, number>;
  total_processed: number;
}

export interface BulkIFUResponse {
  success: boolean;
  result?: BulkIFUResult;
  error?: string;
}

export interface AnalysisResult {
  substantially_equivalent: boolean;
  reasons: string[];
  citations: Citation[];
  suggestions: string[];
}

export interface Citation {
  tool: string;
  text: string;
}

export interface PredicateEquivalenceRequest {
  device_intended_use: string;
  predicate_k_number: string;
}

export interface PredicateEquivalenceResponse {
  success: boolean;
  analysis?: AnalysisResult;
  error?: string;
}