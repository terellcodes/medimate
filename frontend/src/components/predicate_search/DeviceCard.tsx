'use client';

import { Device } from '@/types/predicate';

interface DeviceCardProps {
  device: Device;
  onDownload: (device: Device) => void;
  isSelected?: boolean;
  onToggle?: () => void;
  isSelectable?: boolean;
}

export default function DeviceCard({ 
  device, 
  onDownload, 
  isSelected = false, 
  onToggle, 
  isSelectable = true 
}: DeviceCardProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <div className={`bg-white border rounded-lg p-6 hover:shadow-lg transition duration-200 ${
      isSelected 
        ? 'border-green-300 bg-green-50' 
        : 'border-slate-200'
    } ${isSelectable ? 'cursor-pointer' : ''}`}>
      {/* Selection checkbox */}
      {isSelectable && onToggle && (
        <div className="flex items-center mb-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggle}
            className="w-4 h-4 text-green-600 bg-white border-slate-300 rounded focus:ring-green-500 focus:ring-2"
            onClick={(e) => e.stopPropagation()}
          />
          <label className="ml-2 text-sm text-slate-700 cursor-pointer" onClick={onToggle}>
            {isSelected ? 'Selected for IFU extraction' : 'Select for IFU extraction'}
          </label>
        </div>
      )}
      
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-800 mb-2">
            {device.device_name}
          </h3>
          <p className="text-sm text-slate-800 mb-1">
            <span className="font-medium">Applicant:</span> {device.applicant}
          </p>
          {device.product_code && (
            <p className="text-sm text-slate-800 mb-1">
              <span className="font-medium">Product Code:</span> {device.product_code}
            </p>
          )}
        </div>
        
        <div className="flex flex-col items-end gap-2">
          <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
            {device.clearance_type || '510(k)'}
          </span>
          {device.decision_date && (
            <span className="text-xs text-slate-700">
              {formatDate(device.decision_date)}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-slate-700 uppercase tracking-wide font-medium">K Number</p>
          <p className="text-sm font-mono text-slate-800">{device.k_number}</p>
        </div>
        <div>
          <p className="text-xs text-slate-700 uppercase tracking-wide font-medium">Decision</p>
          <p className="text-sm text-slate-800">{device.decision_description || 'Substantially Equivalent'}</p>
        </div>
      </div>

      {device.statement && (
        <div className="mb-4">
          <p className="text-xs text-slate-700 uppercase tracking-wide font-medium mb-1">Statement</p>
          <p className="text-sm text-slate-800 line-clamp-3">{device.statement}</p>
        </div>
      )}

      <div className="flex justify-between items-center pt-4 border-t border-slate-100">
        <div className="flex items-center space-x-4">
          <span className={`px-2 py-1 text-xs font-medium rounded ${
            device.pdf_available 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {device.pdf_available ? 'PDF Available' : 'No PDF'}
          </span>
          
          {device.recall_status && (
            <span className={`px-2 py-1 text-xs font-medium rounded ${
              device.recall_status === 'recalled' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {device.recall_status === 'recalled' ? 'Recalled' : 'Safe'}
            </span>
          )}
        </div>

        <button
          onClick={() => onDownload(device)}
          disabled={!device.pdf_available}
          className="bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Download PDF
        </button>
      </div>
    </div>
  );
}