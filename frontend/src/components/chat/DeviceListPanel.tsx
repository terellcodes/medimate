'use client';

import { useState } from 'react';
import { Search, Filter } from 'lucide-react';

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
}

export default function DeviceListPanel({ devices, selectedDevice, onDeviceSelect }: DeviceListPanelProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterClass, setFilterClass] = useState('all');

  // Filter devices based on search and classification
  const filteredDevices = devices.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         device.kNumber.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterClass === 'all' || device.classification === filterClass;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Panel Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Medical Devices</h2>
        
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search devices or K-numbers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="text-gray-400 w-4 h-4" />
          <select
            value={filterClass}
            onChange={(e) => setFilterClass(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Classes</option>
            <option value="Class I">Class I</option>
            <option value="Class II">Class II</option>
            <option value="Class III">Class III</option>
          </select>
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
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 text-sm truncate">
                    {device.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {device.kNumber} • {device.classification}
                  </p>
                </div>
                <div className={`
                  px-2 py-1 rounded-full text-xs font-medium
                  ${device.status === 'cleared' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                  }
                `}>
                  {device.status}
                </div>
              </div>
              
              <p className="text-xs text-gray-600 truncate">
                {device.description}
              </p>
              
              <div className="mt-2 text-xs text-gray-500">
                Cleared: {new Date(device.clearanceDate).toLocaleDateString()}
              </div>
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