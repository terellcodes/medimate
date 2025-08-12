'use client';

import { MessageSquarePlus, X, Clock, MessageSquare, Circle } from 'lucide-react';

interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  lastActivity: string;
}

interface DeviceDetailsPanelProps {
  device: Device;
  onCreateSession: (deviceId: string) => void;
  onCollapse: () => void;
  currentSessionId: string | null;
  chatSessions: ChatSession[];
  onSelectSession: (sessionId: string) => void;
}

export default function DeviceDetailsPanel({ 
  device, 
  onCreateSession, 
  onCollapse,
  currentSessionId,
  chatSessions,
  onSelectSession
}: DeviceDetailsPanelProps) {
  
  const handleCreateSession = () => {
    onCreateSession(device.id);
  };

  // Filter sessions for this device
  const deviceSessions = chatSessions.filter(session => 
    session.id.includes(device.id)
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

      {/* Device Information - Top Section */}
      <div className="p-4 border-b border-gray-200 space-y-4">
        {/* Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-900">Status</span>
          <div className="flex items-center space-x-2">
            <Circle className={`w-2 h-2 ${device.status === 'cleared' ? 'fill-green-500 text-green-500' : 'fill-red-500 text-red-500'}`} />
            <span className={`text-sm font-medium capitalize ${device.status === 'cleared' ? 'text-green-700' : 'text-red-700'}`}>
              {device.status}
            </span>
          </div>
        </div>

        {/* Created On */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-900">Created On</span>
          <span className="text-sm text-gray-600">
            {new Date(device.clearanceDate).toLocaleDateString()}
          </span>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-2">Description</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            {device.description}
          </p>
        </div>

        {/* Intended Use */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-2">Intended Use</h4>
          <p className="text-sm text-gray-600 leading-relaxed">
            This device is intended for use in clinical settings to monitor patient vital signs 
            and provide healthcare professionals with accurate, real-time physiological data 
            for diagnostic and therapeutic decision-making.
          </p>
        </div>
      </div>

      {/* Chat Sessions - Bottom Section */}
      <div className="flex-1 flex flex-col">
        {/* New Chat Session Button */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={handleCreateSession}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            <MessageSquarePlus className="w-4 h-4" />
            <span>New Chat Session</span>
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <MessageSquare className="w-4 h-4 mr-2 text-gray-400" />
              Chat History
            </h4>
            
            {deviceSessions.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p className="text-sm text-gray-500">No chat sessions yet</p>
                <p className="text-xs text-gray-400 mt-1">
                  Create your first session to start analyzing
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {deviceSessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => onSelectSession(session.id)}
                    className={`
                      w-full text-left p-3 rounded-lg border transition-all duration-200
                      ${currentSessionId === session.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <h5 className="font-medium text-sm text-gray-900 truncate">
                        {session.title}
                      </h5>
                      {currentSessionId === session.id && (
                        <Circle className="w-2 h-2 fill-blue-500 text-blue-500 mt-1 flex-shrink-0 ml-2" />
                      )}
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="w-3 h-3 mr-1" />
                      <span>{formatDate(session.lastActivity)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}