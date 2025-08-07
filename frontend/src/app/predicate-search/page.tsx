'use client';

import { useState, useRef } from 'react';
import Header from '@/components/Header';
import PredicateHero from '@/components/predicate_search/PredicateHero';
import PredicateFeatures from '@/components/predicate_search/PredicateFeatures';
import SearchForm from '@/components/predicate_search/SearchForm';
import SearchResults from '@/components/predicate_search/SearchResults';
import { SearchParams, Device, DeviceInfo, IFUExtraction, BulkIFUResponse, AnalysisResult, PredicateEquivalenceResponse } from '@/types/predicate';

export default function PredicateSearchPage() {
  const [devicesWithPDF, setDevicesWithPDF] = useState<Device[]>([]);
  const [devicesWithoutPDF, setDevicesWithoutPDF] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useState<SearchParams | undefined>();
  const [hasSearched, setHasSearched] = useState(false);
  
  // Selection state
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(new Set());
  const [isSelectAllWith510k, setIsSelectAllWith510k] = useState(false);
  const [isSelectAllWithout510k, setIsSelectAllWithout510k] = useState(false);
  
  // IFU fetching state
  const [isFetchingIFU, setIsFetchingIFU] = useState(false);
  const [ifuResults, setIfuResults] = useState<IFUExtraction[]>([]);
  const [showIfuResults, setShowIfuResults] = useState(false);
  
  // Substantial equivalence checking state
  const [deviceIntendedUse, setDeviceIntendedUse] = useState('');
  const [equivalenceResults, setEquivalenceResults] = useState<Map<string, AnalysisResult>>(new Map());
  const [checkingEquivalence, setCheckingEquivalence] = useState<Set<string>>(new Set());
  
  const searchFormRef = useRef<HTMLDivElement>(null);

  const handleTryNowClick = () => {
    searchFormRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  };

  // Selection handlers
  const handleDeviceToggle = (kNumber: string) => {
    const newSelected = new Set(selectedDevices);
    if (newSelected.has(kNumber)) {
      newSelected.delete(kNumber);
    } else {
      newSelected.add(kNumber);
    }
    setSelectedDevices(newSelected);
    
    // Update select all states
    const selectedWith510k = devicesWithPDF.filter(d => newSelected.has(d.k_number));
    const selectedWithout510k = devicesWithoutPDF.filter(d => newSelected.has(d.k_number));
    
    setIsSelectAllWith510k(selectedWith510k.length === devicesWithPDF.length && devicesWithPDF.length > 0);
    setIsSelectAllWithout510k(selectedWithout510k.length === devicesWithoutPDF.length && devicesWithoutPDF.length > 0);
  };

  const handleSelectAll = (section: 'with510k' | 'without510k') => {
    const newSelected = new Set(selectedDevices);
    
    if (section === 'with510k') {
      if (isSelectAllWith510k) {
        // Deselect all with 510k
        devicesWithPDF.forEach(device => newSelected.delete(device.k_number));
        setIsSelectAllWith510k(false);
      } else {
        // Select all with 510k
        devicesWithPDF.forEach(device => newSelected.add(device.k_number));
        setIsSelectAllWith510k(true);
      }
    } else {
      if (isSelectAllWithout510k) {
        // Deselect all without 510k
        devicesWithoutPDF.forEach(device => newSelected.delete(device.k_number));
        setIsSelectAllWithout510k(false);
      } else {
        // Select all without 510k
        devicesWithoutPDF.forEach(device => newSelected.add(device.k_number));
        setIsSelectAllWithout510k(true);
      }
    }
    
    setSelectedDevices(newSelected);
  };

  const handleClearSelection = () => {
    setSelectedDevices(new Set());
    setIsSelectAllWith510k(false);
    setIsSelectAllWithout510k(false);
  };

  const handleFetchIFU = async () => {
    if (selectedDevices.size === 0) {
      alert('Please select at least one device');
      return;
    }

    setIsFetchingIFU(true);
    setShowIfuResults(false);

    try {
      const kNumbers = Array.from(selectedDevices);
      
      const response = await fetch('http://localhost:8000/api/fetch-bulk-ifu', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          k_numbers: kNumbers
        }),
      });

      if (!response.ok) {
        throw new Error(`IFU fetch failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as BulkIFUResponse;

      if (!data.success) {
        throw new Error(data.error || 'IFU fetch failed');
      }

      setIfuResults(data.result?.extractions || []);
      setShowIfuResults(true);
      
      // Scroll to results
      setTimeout(() => {
        const resultsElement = document.getElementById('ifu-results');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);

    } catch (err) {
      alert(`IFU fetch failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsFetchingIFU(false);
    }
  };

  const handleCheckEquivalence = async (extraction: IFUExtraction) => {
    if (!deviceIntendedUse.trim()) {
      alert('Please enter your device\'s intended use first');
      return;
    }

    // Add to checking set
    setCheckingEquivalence(prev => new Set(prev).add(extraction.k_number));

    try {
      const response = await fetch('http://localhost:8000/api/check-predicate-equivalence', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_intended_use: deviceIntendedUse,
          predicate_k_number: extraction.k_number
        }),
      });

      if (!response.ok) {
        throw new Error(`Equivalence check failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as PredicateEquivalenceResponse;

      if (!data.success) {
        throw new Error(data.error || 'Equivalence check failed');
      }

      if (data.analysis) {
        setEquivalenceResults(prev => new Map(prev).set(extraction.k_number, data.analysis!));
      }

    } catch (err) {
      alert(`Equivalence check failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      // Remove from checking set
      setCheckingEquivalence(prev => {
        const newSet = new Set(prev);
        newSet.delete(extraction.k_number);
        return newSet;
      });
    }
  };

  const handleSearch = async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);
    setSearchParams(params);
    setHasSearched(true);
    
    // Clear previous selections
    handleClearSelection();

    try {
      const requestBody = {
        search_params: {
          search_term: params.searchTerm || undefined,
          product_code: params.productCode || undefined,
          max_downloads: params.maxDownloads,
          include_recalled: params.includeRecalled
        }
      };

      const response = await fetch('http://localhost:8000/api/search-devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Search failed');
      }

      // Backend returns two separate lists, process them separately
      const withPDF = (data.result?.devices_with_510k || []).map((deviceInfo: DeviceInfo) => ({
        ...deviceInfo,
        pdf_available: deviceInfo.has_510k_document,
        clearance_type: deviceInfo.document_type || '510(k)',
        recall_status: deviceInfo.safety_status === 'recalled' ? 'recalled' : 'safe'
      }));
      
      const withoutPDF = (data.result?.devices_without_510k || []).map((deviceInfo: DeviceInfo) => ({
        ...deviceInfo,
        pdf_available: deviceInfo.has_510k_document,
        clearance_type: deviceInfo.document_type || '510(k)',
        recall_status: deviceInfo.safety_status === 'recalled' ? 'recalled' : 'safe'
      }));
      
      // Set separate state for each list
      setDevicesWithPDF(withPDF);
      setDevicesWithoutPDF(withoutPDF);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setDevicesWithPDF([]);
      setDevicesWithoutPDF([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (device: Device) => {
    if (!device.pdf_available) {
      alert('PDF not available for this device');
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/api/discover-predicates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_params: {
            search_term: device.device_name,
            product_code: device.product_code,
            max_downloads: 1,
            include_recalled: false
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Download failed');
      }
      
      if (data.result?.downloads && data.result.downloads.length > 0) {
        const downloadInfo = data.result.downloads[0];
        if (downloadInfo.pdf_url) {
          // Open PDF in new tab
          window.open(downloadInfo.pdf_url, '_blank');
        } else {
          alert('PDF download URL not available');
        }
      } else {
        alert('PDF not found for this device');
      }
    } catch (err) {
      alert(`Download failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <PredicateHero onTryNowClick={handleTryNowClick} />
      <PredicateFeatures />
      
      <section className="py-16 bg-white" ref={searchFormRef}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">
              Search FDA 510(k) Database
            </h2>
            <p className="text-lg text-slate-800 max-w-2xl mx-auto">
              Find predicate devices by entering device keywords, FDA product codes, or both. 
              Our system searches the complete openFDA database in real-time.
            </p>
          </div>
          
          <div className="space-y-8">
            <SearchForm 
              onSearch={handleSearch} 
              isLoading={isLoading}
            />
            
            {hasSearched && (
              <SearchResults
                devicesWithPDF={devicesWithPDF}
                devicesWithoutPDF={devicesWithoutPDF}
                isLoading={isLoading}
                error={error}
                onDownload={handleDownload}
                searchParams={searchParams}
                selectedDevices={selectedDevices}
                isSelectAllWith510k={isSelectAllWith510k}
                isSelectAllWithout510k={isSelectAllWithout510k}
                onDeviceToggle={handleDeviceToggle}
                onSelectAll={handleSelectAll}
                onClearSelection={handleClearSelection}
                onFetchIFU={handleFetchIFU}
                isFetchingIFU={isFetchingIFU}
              />
            )}
            
            {/* IFU Results Section */}
            {showIfuResults && (
              <div id="ifu-results" className="mt-8 bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
                <div className="flex items-center mb-6">
                  <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                    📄
                  </div>
                  <h3 className="text-lg font-semibold text-slate-800">
                    IFU Extraction Results
                  </h3>
                  <span className="ml-2 text-sm text-slate-600">
                    ({ifuResults.length} processed)
                  </span>
                </div>
                
                {/* Device Intended Use Input */}
                <div className="mb-8 p-6 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center mb-4">
                    <div className="bg-purple-100 text-purple-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3">
                      ⚖️
                    </div>
                    <h4 className="text-lg font-semibold text-slate-800">
                      Your Device&apos;s Intended Use
                    </h4>
                  </div>
                  <div className="space-y-3">
                    <label htmlFor="device-intended-use" className="block text-sm font-medium text-slate-700">
                      Enter the intended use statement for your device to check substantial equivalence:
                    </label>
                    <textarea
                      id="device-intended-use"
                      value={deviceIntendedUse}
                      onChange={(e) => setDeviceIntendedUse(e.target.value)}
                      placeholder="Example: The XYZ Device is intended for use in measuring blood glucose levels in patients with diabetes for glucose monitoring to aid in diabetes management."
                      className="w-full p-4 border border-slate-300 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-slate-800 placeholder-slate-500"
                      rows={4}
                    />
                    <p className="text-xs text-slate-600">
                      💡 <span className="font-medium">Tip:</span> Provide a clear and specific description of what your device is intended to do, similar to how predicate devices describe their intended use.
                    </p>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {ifuResults.map((extraction, index: number) => (
                    <div key={extraction.k_number || index} className="border border-slate-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-slate-800 mb-2">
                            {extraction.device_name}
                          </h4>
                          <p className="text-sm text-slate-600 font-mono">
                            K-Number: {extraction.k_number}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                            extraction.extraction_status === 'success' 
                              ? 'bg-green-100 text-green-800'
                              : extraction.extraction_status === 'no_pdf'
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {extraction.extraction_status === 'success' && '✓ Success'}
                            {extraction.extraction_status === 'no_pdf' && '⚠ No PDF'}
                            {extraction.extraction_status === 'no_ifu_found' && '⚠ No IFU Found'}
                            {extraction.extraction_status === 'extraction_failed' && '✗ Failed'}
                          </span>
                        </div>
                      </div>
                      
                      {extraction.extraction_status === 'success' && extraction.ifu_text && (
                        <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                          <p className="text-xs text-slate-700 uppercase tracking-wide font-medium mb-2">
                            Indication for Use
                          </p>
                          <p className="text-sm text-slate-800 leading-relaxed">
                            {extraction.ifu_text}
                          </p>
                        </div>
                      )}
                      
                      {extraction.error_message && (
                        <div className="mb-4 p-4 bg-red-50 rounded-lg">
                          <p className="text-xs text-red-700 uppercase tracking-wide font-medium mb-2">
                            Error Details
                          </p>
                          <p className="text-sm text-red-800">
                            {extraction.error_message}
                          </p>
                        </div>
                      )}
                      
                      {/* Equivalence Analysis Results */}
                      {equivalenceResults.has(extraction.k_number) && (
                        <div className="mt-4 p-4 border rounded-lg bg-purple-50 border-purple-200">
                          <div className="flex items-center mb-3">
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 ${
                              equivalenceResults.get(extraction.k_number)?.substantially_equivalent 
                                ? 'bg-green-500' 
                                : 'bg-red-500'
                            }`}>
                              {equivalenceResults.get(extraction.k_number)?.substantially_equivalent ? '✓' : '✗'}
                            </div>
                            <h5 className="font-semibold text-slate-800">
                              {equivalenceResults.get(extraction.k_number)?.substantially_equivalent 
                                ? 'Substantially Equivalent' 
                                : 'Not Substantially Equivalent'}
                            </h5>
                          </div>
                          
                          {equivalenceResults.get(extraction.k_number)?.reasons && equivalenceResults.get(extraction.k_number)!.reasons.length > 0 && (
                            <div className="mb-3">
                              <p className="text-sm font-medium text-slate-700 mb-2">Analysis:</p>
                              <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                                {equivalenceResults.get(extraction.k_number)!.reasons.map((reason, idx) => (
                                  <li key={idx}>{reason}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {equivalenceResults.get(extraction.k_number)?.suggestions && equivalenceResults.get(extraction.k_number)!.suggestions.length > 0 && (
                            <div className="mb-3">
                              <p className="text-sm font-medium text-slate-700 mb-2">Recommendations:</p>
                              <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                                {equivalenceResults.get(extraction.k_number)!.suggestions.map((suggestion, idx) => (
                                  <li key={idx}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {equivalenceResults.get(extraction.k_number)?.citations && equivalenceResults.get(extraction.k_number)!.citations.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-slate-700 mb-2">FDA Guidelines References:</p>
                              <div className="space-y-1 text-xs text-slate-500">
                                {equivalenceResults.get(extraction.k_number)!.citations.map((citation, idx) => (
                                  <div key={idx}>
                                    <strong>{citation.tool}:</strong> {citation.text}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Action Buttons */}
                      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                        <div className="flex items-center space-x-3">
                          {extraction.pdf_url && (
                            <button
                              onClick={() => window.open(extraction.pdf_url, '_blank')}
                              className="text-sm text-blue-600 hover:text-blue-800 underline"
                            >
                              View Original PDF
                            </button>
                          )}
                        </div>
                        
                        {/* Check Substantial Equivalence Button */}
                        {extraction.extraction_status === 'success' && extraction.ifu_text && (
                          <button
                            onClick={() => handleCheckEquivalence(extraction)}
                            disabled={!deviceIntendedUse.trim() || checkingEquivalence.has(extraction.k_number)}
                            className="bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-600 transition duration-200 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                            title={!deviceIntendedUse.trim() ? 'Please enter your device\'s intended use above' : 'Check if this predicate device is substantially equivalent'}
                          >
                            {checkingEquivalence.has(extraction.k_number) ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Analyzing...
                              </>
                            ) : (
                              <>
                                <span className="mr-2">⚖️</span>
                                Check for Substantial Equivalence
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    💡 <span className="font-medium">Results Summary:</span> IFU extraction completed for {ifuResults.length} devices. 
                    This AI-powered extraction identifies the &quot;Indications for Use&quot; sections from FDA 510(k) documents.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}