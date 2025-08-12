'use client';

import { MessageSquarePlus, X, FileText, Calendar, Building2, Tag } from 'lucide-react';

interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

interface DeviceDetailsPanelProps {
  device: Device;
  onCreateSession: (deviceId: string) => void;
  onCollapse: () => void;
  currentSessionId: string | null;
}

export default function DeviceDetailsPanel({ 
  device, 
  onCreateSession, 
  onCollapse,
  currentSessionId 
}: DeviceDetailsPanelProps) {
  
  const handleCreateSession = () => {
    onCreateSession(device.id);
  };

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Header with collapse button */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Device Details</h2>
        <button
          onClick={onCollapse}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          title="Collapse panel"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Device Information */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Main Info */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">{device.name}</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Tag className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">K-Number:</span>
              <span className="text-sm font-medium text-gray-900">{device.kNumber}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">Classification:</span>
              <span className="text-sm font-medium text-gray-900">{device.classification}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">Cleared:</span>
              <span className="text-sm font-medium text-gray-900">
                {new Date(device.clearanceDate).toLocaleDateString()}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`
                w-2 h-2 rounded-full
                ${device.status === 'cleared' ? 'bg-green-500' : 'bg-red-500'}
              `} />
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`
                text-sm font-medium capitalize
                ${device.status === 'cleared' ? 'text-green-700' : 'text-red-700'}
              `}>
                {device.status}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <FileText className="w-4 h-4 mr-2 text-gray-400" />
            Description
          </h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            {device.description}
          </p>
        </div>

        {/* Additional Mock Information */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Technical Specifications</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Operating Voltage:</span>
              <span className="text-gray-900">120V AC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Frequency Range:</span>
              <span className="text-gray-900">50-60 Hz</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Dimensions:</span>
              <span className="text-gray-900">12" x 8" x 4"</span>
            </div>
          </div>
        </div>

        {/* Intended Use */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Intended Use</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            This device is intended for use in clinical settings to monitor patient vital signs 
            and provide healthcare professionals with accurate, real-time physiological data 
            for diagnostic and therapeutic decision-making.
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 border-t border-gray-200 space-y-3">
        {/* New Chat Session Button */}
        <button
          onClick={handleCreateSession}
          className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          <MessageSquarePlus className="w-4 h-4" />
          <span>New Chat Session</span>
        </button>

        {currentSessionId && (
          <div className="text-xs text-green-600 text-center p-2 bg-green-50 rounded">
            ✓ Session created: {currentSessionId.split('-').slice(-1)[0]}
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-2">
          <button className="px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors">
            View PDF
          </button>
          <button className="px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors">
            Compare
          </button>
        </div>
      </div>
    </div>
  );
}