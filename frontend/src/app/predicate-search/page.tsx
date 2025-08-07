'use client';

import { useState, useRef } from 'react';
import Header from '@/components/Header';
import PredicateHero from '@/components/predicate_search/PredicateHero';
import PredicateFeatures from '@/components/predicate_search/PredicateFeatures';
import SearchForm from '@/components/predicate_search/SearchForm';
import SearchResults from '@/components/predicate_search/SearchResults';
import { SearchParams, Device } from '@/types/predicate';

export default function PredicateSearchPage() {
  const [devicesWithPDF, setDevicesWithPDF] = useState<Device[]>([]);
  const [devicesWithoutPDF, setDevicesWithoutPDF] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useState<SearchParams | undefined>();
  const [hasSearched, setHasSearched] = useState(false);
  
  const searchFormRef = useRef<HTMLDivElement>(null);

  const handleTryNowClick = () => {
    searchFormRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  };

  const handleSearch = async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);
    setSearchParams(params);
    setHasSearched(true);

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
      const withPDF = (data.result?.devices_with_510k || []).map((deviceInfo: any) => ({
        ...deviceInfo,
        pdf_available: deviceInfo.has_510k_document,
        clearance_type: deviceInfo.document_type || '510(k)',
        recall_status: deviceInfo.safety_status === 'recalled' ? 'recalled' : 'safe'
      }));
      
      const withoutPDF = (data.result?.devices_without_510k || []).map((deviceInfo: any) => ({
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
              />
            )}
          </div>
        </div>
      </section>
    </div>
  );
}