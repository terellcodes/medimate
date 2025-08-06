'use client';

import { Device } from '@/types/predicate';
import DeviceCard from './DeviceCard';

interface SearchResultsProps {
  devices: Device[];
  isLoading: boolean;
  error: string | null;
  onDownload: (device: Device) => void;
  searchParams?: {
    searchTerm?: string;
    productCode?: string;
  };
}

export default function SearchResults({ 
  devices, 
  isLoading, 
  error, 
  onDownload, 
  searchParams 
}: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          <p className="ml-4 text-slate-800">Searching FDA database...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl p-8 border border-red-200 shadow-sm">
        <div className="text-center py-8">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-slate-800 mb-2">Search Error</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-sm text-slate-800">
            Please try again with different search terms or check your connection.
          </p>
        </div>
      </div>
    );
  }

  if (devices.length === 0) {
    return (
      <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
        <div className="text-center py-12">
          <div className="text-slate-400 text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-slate-800 mb-2">No Devices Found</h3>
          <p className="text-slate-800 mb-4">
            {searchParams?.searchTerm || searchParams?.productCode 
              ? `No devices found for "${searchParams.searchTerm || searchParams.productCode}"`
              : 'No devices found for your search criteria'
            }
          </p>
          <div className="text-sm text-slate-800 space-y-1">
            <p>Try:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Using broader search terms</li>
              <li>Checking the product code spelling</li>
              <li>Searching with just keywords or just product code</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
            2
          </div>
          <h3 className="text-lg font-semibold text-slate-800">
            Search Results
          </h3>
        </div>
        <span className="text-sm text-slate-800">
          {devices.length} device{devices.length !== 1 ? 's' : ''} found
        </span>
      </div>

      {searchParams && (searchParams.searchTerm || searchParams.productCode) && (
        <div className="mb-6 p-4 bg-slate-50 rounded-lg">
          <p className="text-sm text-slate-800">
            <span className="font-medium">Search criteria:</span>
            {searchParams.searchTerm && (
              <span className="ml-2 px-2 py-1 bg-white rounded text-slate-700">
                "{searchParams.searchTerm}"
              </span>
            )}
            {searchParams.productCode && (
              <span className="ml-2 px-2 py-1 bg-white rounded text-slate-700 font-mono">
                {searchParams.productCode}
              </span>
            )}
          </p>
        </div>
      )}

      <div className="space-y-4">
        {devices.map((device, index) => (
          <DeviceCard
            key={device.k_number || index}
            device={device}
            onDownload={onDownload}
          />
        ))}
      </div>

      {devices.length > 0 && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-800">
            💡 <span className="font-medium">Tip:</span> Review device statements and classifications carefully. 
            Devices with similar product codes and intended use are typically the best predicate candidates.
          </p>
        </div>
      )}
    </div>
  );
}