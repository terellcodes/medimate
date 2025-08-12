'use client';

import { useState } from 'react';
import { Search, Plus } from 'lucide-react';

interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

interface DeviceListPanelProps {
  devices: Device[];
  selectedDevice: Device | null;
  onDeviceSelect: (device: Device) => void;
  onNewDevice?: () => void;
}

export default function DeviceListPanel({ devices, selectedDevice, onDeviceSelect, onNewDevice }: DeviceListPanelProps) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter devices based on search
  const filteredDevices = devices.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         device.kNumber.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Panel Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">Medical Devices</h2>
          <button
            onClick={onNewDevice}
            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            title="Add new device"
          >
            <Plus className="w-4 h-4" />
            <span>New</span>
          </button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search devices or K-numbers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-500"
          />
        </div>
      </div>

      {/* Device List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-2">
          {filteredDevices.map((device) => (
            <div
              key={device.id}
              onClick={() => onDeviceSelect(device)}
              className={`
                p-3 rounded-lg border cursor-pointer transition-all duration-200
                ${selectedDevice?.id === device.id 
                  ? 'border-blue-500 bg-blue-50 shadow-sm' 
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              <h3 className="font-medium text-gray-900 text-sm">
                {device.name}
              </h3>
            </div>
          ))}
        </div>

        {filteredDevices.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <Search className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">No devices found</p>
            <p className="text-xs text-gray-400 mt-1">
              Try adjusting your search or filter
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200 text-xs text-gray-500">
        {filteredDevices.length} of {devices.length} devices
      </div>
    </div>
  );
}