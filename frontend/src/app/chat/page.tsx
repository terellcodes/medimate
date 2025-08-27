'use client';

import { useState } from 'react';
import { Allotment } from 'allotment';
import 'allotment/dist/style.css';

import DeviceListPanel from '@/components/chat/DeviceListPanel';
import DeviceDetailsPanel from '@/components/chat/DeviceDetailsPanel';
import ChatPanel from '@/components/chat/ChatPanel';
import WorkspacePanel from '@/components/chat/WorkspacePanel';

// Dummy data types
interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

// Add interface for chat sessions
interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  lastActivity: string;
}

const DUMMY_DEVICES: Device[] = [
  {
    id: '1',
    name: 'Cardiac Monitor System',
    kNumber: 'K123456',
    classification: 'Class II',
    status: 'cleared',
    clearanceDate: '2023-06-15',
    description: 'Continuous cardiac monitoring system with arrhythmia detection capabilities.'
  },
  {
    id: '2', 
    name: 'Blood Pressure Monitor',
    kNumber: 'K789012',
    classification: 'Class II',
    status: 'cleared',
    clearanceDate: '2023-08-22',
    description: 'Automated oscillometric blood pressure measurement device for clinical use.'
  },
  {
    id: '3',
    name: 'Pulse Oximeter',
    kNumber: 'K345678',
    classification: 'Class II', 
    status: 'cleared',
    clearanceDate: '2023-04-10',
    description: 'Non-invasive pulse oximeter for measuring oxygen saturation and pulse rate.'
  },
  {
    id: '4',
    name: 'ECG Machine',
    kNumber: 'K901234',
    classification: 'Class II',
    status: 'cleared', 
    clearanceDate: '2023-09-05',
    description: '12-lead electrocardiogram machine for cardiac rhythm analysis.'
  },
  {
    id: '5',
    name: 'Defibrillator',
    kNumber: 'K567890',
    classification: 'Class III',
    status: 'cleared',
    clearanceDate: '2023-07-18',
    description: 'Automated external defibrillator for emergency cardiac care.'
  }
];

export default function ChatPage() {
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [isDetailsVisible, setIsDetailsVisible] = useState(false);
  const [isWorkspaceVisible, setIsWorkspaceVisible] = useState(true);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);

  const handleDeviceSelect = (device: Device) => {
    setSelectedDevice(device);
    setIsDetailsVisible(true);
  };

  const handleCreateSession = (deviceId: string) => {
    const sessionId = `session-${deviceId}-${Date.now()}`;
    const newSession: ChatSession = {
      id: sessionId,
      title: `Analysis Session ${chatSessions.length + 1}`,
      createdAt: new Date().toISOString(),
      lastActivity: new Date().toISOString()
    };
    
    setChatSessions(prev => [...prev, newSession]);
    setCurrentSessionId(sessionId);
    console.log(`Created new session: ${sessionId} for device: ${deviceId}`);
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleCollapseDetails = () => {
    setIsDetailsVisible(false);
  };

  const handleToggleWorkspace = () => {
    setIsWorkspaceVisible(!isWorkspaceVisible);
  };

  const handleNewDevice = () => {
    // TODO: Implement new device creation logic
    console.log('Creating new device...');
    alert('New device creation functionality will be implemented here');
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="h-16 bg-white border-b border-gray-200 flex items-center px-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-semibold text-sm">M</span>
          </div>
          <h1 className="text-xl font-semibold text-gray-900">MediMate Chat</h1>
        </div>
        <div className="ml-auto text-sm text-gray-500">
          FDA 510(k) Analysis Assistant
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Allotment>
          {/* Device List Panel - Always visible */}
          <Allotment.Pane preferredSize={280} minSize={250} maxSize={400}>
            <DeviceListPanel 
              devices={DUMMY_DEVICES}
              selectedDevice={selectedDevice}
              onDeviceSelect={handleDeviceSelect}
              onNewDevice={handleNewDevice}
            />
          </Allotment.Pane>

          {/* Device Details Panel - Collapsible */}
          {isDetailsVisible && selectedDevice && (
            <Allotment.Pane preferredSize={320} minSize={300} maxSize={500}>
              <DeviceDetailsPanel
                device={selectedDevice}
                onCreateSession={handleCreateSession}
                onCollapse={handleCollapseDetails}
                currentSessionId={currentSessionId}
                chatSessions={chatSessions}
                onSelectSession={handleSelectSession}
              />
            </Allotment.Pane>
          )}

          {/* Chat Panel - Main area */}
          <Allotment.Pane>
            <ChatPanel 
              selectedDevice={selectedDevice}
              sessionId={currentSessionId}
              onToggleWorkspace={handleToggleWorkspace}
              isWorkspaceVisible={isWorkspaceVisible}
            />
          </Allotment.Pane>

          {/* Workspace Panel - Right side - Collapsible */}
          {isWorkspaceVisible && (
            <Allotment.Pane preferredSize={400} minSize={350}>
              <WorkspacePanel 
                selectedDevice={selectedDevice}
                onCollapse={handleToggleWorkspace}
              />
            </Allotment.Pane>
          )}
        </Allotment>
      </div>
    </div>
  );
}