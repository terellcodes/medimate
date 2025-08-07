'use client';

import { Device } from '@/types/predicate';
import DeviceCard from './DeviceCard';

interface SearchResultsProps {
  devicesWithPDF: Device[];
  devicesWithoutPDF: Device[];
  isLoading: boolean;
  error: string | null;
  onDownload: (device: Device) => void;
  searchParams?: {
    searchTerm?: string;
    productCode?: string;
  };
  selectedDevices?: Set<string>;
  isSelectAllWith510k?: boolean;
  isSelectAllWithout510k?: boolean;
  onDeviceToggle?: (kNumber: string) => void;
  onSelectAll?: (section: 'with510k' | 'without510k') => void;
  onClearSelection?: () => void;
  onFetchIFU?: () => void;
  isFetchingIFU?: boolean;
}

export default function SearchResults({ 
  devicesWithPDF,
  devicesWithoutPDF,
  isLoading, 
  error, 
  onDownload, 
  searchParams,
  selectedDevices = new Set(),
  isSelectAllWith510k = false,
  isSelectAllWithout510k = false,
  onDeviceToggle,
  onSelectAll,
  onClearSelection,
  onFetchIFU,
  isFetchingIFU = false
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

  const totalDevices = devicesWithPDF.length + devicesWithoutPDF.length;
  
  if (totalDevices === 0) {
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
        <div className="flex items-center space-x-4">
          <span className="text-sm text-slate-800">
            {totalDevices} device{totalDevices !== 1 ? 's' : ''} found
          </span>
          {selectedDevices.size > 0 && (
            <span className="text-sm text-green-600 font-medium">
              {selectedDevices.size} selected
            </span>
          )}
          {selectedDevices.size > 0 && onClearSelection && (
            <button
              onClick={onClearSelection}
              className="text-sm text-slate-500 hover:text-slate-700 underline"
            >
              Clear selection
            </button>
          )}
        </div>
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

      {/* Devices with 510(k) PDFs Section */}
      {devicesWithPDF.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="bg-green-100 text-green-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3">
                PDF
              </div>
              <h4 className="text-xl font-semibold text-slate-800">
                Devices with 510(k) Documents Available
              </h4>
              <span className="ml-2 text-sm text-slate-600">
                ({devicesWithPDF.length})
              </span>
            </div>
            {onSelectAll && (
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={isSelectAllWith510k}
                  onChange={() => onSelectAll('with510k')}
                  className="w-4 h-4 text-green-600 bg-white border-slate-300 rounded focus:ring-green-500 focus:ring-2 mr-2"
                />
                <label className="text-sm text-slate-700 cursor-pointer" onClick={() => onSelectAll && onSelectAll('with510k')}>
                  Select All
                </label>
              </div>
            )}
          </div>
          <div className="space-y-4">
            {devicesWithPDF.map((device, index) => (
              <DeviceCard
                key={device.k_number || `with-${index}`}
                device={device}
                onDownload={onDownload}
                isSelected={selectedDevices.has(device.k_number)}
                onToggle={() => onDeviceToggle && onDeviceToggle(device.k_number)}
                isSelectable={!!onDeviceToggle}
              />
            ))}
          </div>
        </div>
      )}

      {/* Separator if both sections exist */}
      {devicesWithPDF.length > 0 && devicesWithoutPDF.length > 0 && (
        <div className="border-t border-slate-200 my-8"></div>
      )}

      {/* Devices without 510(k) PDFs Section */}
      {devicesWithoutPDF.length > 0 && (
        <div className="mb-6 bg-slate-50 p-6 rounded-lg border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="bg-slate-100 text-slate-600 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3">
                ⚬
              </div>
              <h4 className="text-xl font-semibold text-slate-800">
                Devices without 510(k) Documents
              </h4>
              <span className="ml-2 text-sm text-slate-600">
                ({devicesWithoutPDF.length})
              </span>
            </div>
            {onSelectAll && (
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={isSelectAllWithout510k}
                  onChange={() => onSelectAll('without510k')}
                  className="w-4 h-4 text-green-600 bg-white border-slate-300 rounded focus:ring-green-500 focus:ring-2 mr-2"
                />
                <label className="text-sm text-slate-700 cursor-pointer" onClick={() => onSelectAll && onSelectAll('without510k')}>
                  Select All
                </label>
              </div>
            )}
          </div>
          <div className="space-y-4">
            {devicesWithoutPDF.map((device, index) => (
              <DeviceCard
                key={device.k_number || `without-${index}`}
                device={device}
                onDownload={onDownload}
                isSelected={selectedDevices.has(device.k_number)}
                onToggle={() => onDeviceToggle && onDeviceToggle(device.k_number)}
                isSelectable={!!onDeviceToggle}
              />
            ))}
          </div>
        </div>
      )}

      {/* Fetch IFU Button */}
      {selectedDevices.size > 0 && onFetchIFU && (
        <div className="mt-6 flex justify-center">
          <button 
            onClick={onFetchIFU}
            disabled={isFetchingIFU}
            className="bg-green-500 text-white px-6 py-3 rounded-lg text-base font-medium hover:bg-green-600 transition duration-200 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isFetchingIFU ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing {selectedDevices.size} devices...
              </>
            ) : (
              <>
                <span className="mr-2">📄</span>
                Fetch IFU for Selected Devices ({selectedDevices.size})
              </>
            )}
          </button>
        </div>
      )}

      {totalDevices > 0 && (
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