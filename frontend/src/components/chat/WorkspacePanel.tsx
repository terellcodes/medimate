'use client';

import { useState } from 'react';
import { BarChart3, FileText, GitCompare, Settings, TrendingUp, CheckCircle, AlertCircle, X } from 'lucide-react';

interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

interface WorkspacePanelProps {
  selectedDevice: Device | null;
  onCollapse: () => void;
}

export default function WorkspacePanel({ selectedDevice, onCollapse }: WorkspacePanelProps) {
  const [activeTab, setActiveTab] = useState<'analysis' | 'comparison' | 'documents' | 'settings'>('analysis');

  const tabs = [
    { id: 'analysis' as const, label: 'Analysis', icon: BarChart3 },
    { id: 'comparison' as const, label: 'Comparison', icon: GitCompare },
    { id: 'documents' as const, label: 'Documents', icon: FileText },
    { id: 'settings' as const, label: 'Settings', icon: Settings }
  ];

  const mockAnalysisData = {
    decisionPoints: [
      { id: 1, name: 'Predicate Device Validation', status: 'completed', result: 'Pass' },
      { id: 2, name: 'Intended Use Analysis', status: 'completed', result: 'Pass' },
      { id: 3, name: 'Technological Characteristics', status: 'in-progress', result: 'Pending' },
      { id: 4, name: 'Safety/Effectiveness Questions', status: 'pending', result: 'Pending' },
      { id: 5, name: 'Performance Testing', status: 'pending', result: 'Pending' }
    ],
    equivalenceScore: 87,
    riskLevel: 'Medium'
  };

  const mockPredicates = [
    { kNumber: 'K123456', name: 'Cardiac Monitor System', similarity: 95, status: 'recommended' },
    { kNumber: 'K789012', name: 'Blood Pressure Monitor', similarity: 87, status: 'alternative' },
    { kNumber: 'K345678', name: 'Pulse Oximeter', similarity: 82, status: 'alternative' }
  ];

  const renderAnalysisTab = () => (
    <div className="space-y-6">
      {/* Progress Overview */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">510(k) Analysis Progress</h3>
          <TrendingUp className="w-5 h-5 text-blue-600" />
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-600">Overall Progress</span>
              <span className="font-medium text-gray-900">40%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '40%' }}></div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">{mockAnalysisData.equivalenceScore}%</div>
            <div className="text-xs text-gray-500">Similarity</div>
          </div>
        </div>
      </div>

      {/* Decision Points */}
      <div>
        <h4 className="font-medium text-gray-900 mb-3">FDA Decision Points</h4>
        <div className="space-y-2">
          {mockAnalysisData.decisionPoints.map((point) => (
            <div key={point.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-xs font-medium">
                  {point.id}
                </div>
                <span className="text-sm font-medium text-gray-900">{point.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                {point.status === 'completed' && (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                {point.status === 'in-progress' && (
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                )}
                <span className={`
                  text-xs px-2 py-1 rounded-full font-medium
                  ${point.result === 'Pass' ? 'bg-green-100 text-green-800' : 
                    point.result === 'Pending' ? 'bg-gray-100 text-gray-600' : ''}
                `}>
                  {point.result}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Assessment */}
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Risk Assessment</h4>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-yellow-600" />
            <span className="font-medium text-yellow-800">Medium Risk Level</span>
          </div>
          <p className="text-sm text-yellow-700">
            Some technological differences identified that may require additional testing data.
          </p>
        </div>
      </div>
    </div>
  );

  const renderComparisonTab = () => (
    <div className="space-y-6">
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Predicate Candidates</h4>
        <div className="space-y-3">
          {mockPredicates.map((predicate) => (
            <div key={predicate.kNumber} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h5 className="font-medium text-gray-900">{predicate.kNumber}</h5>
                  <p className="text-sm text-gray-600">{predicate.name}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-gray-900">{predicate.similarity}%</div>
                  <div className="text-xs text-gray-500">Match</div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="w-full bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${predicate.similarity}%` }}
                  ></div>
                </div>
                <span className={`
                  text-xs px-2 py-1 rounded-full font-medium
                  ${predicate.status === 'recommended' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}
                `}>
                  {predicate.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Technological Comparison</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-gray-600">Characteristic</th>
                <th className="text-left py-2 text-gray-600">Your Device</th>
                <th className="text-left py-2 text-gray-600">Predicate</th>
                <th className="text-center py-2 text-gray-600">Match</th>
              </tr>
            </thead>
            <tbody className="space-y-1">
              <tr className="border-b border-gray-100">
                <td className="py-2 font-medium">Intended Use</td>
                <td className="py-2 text-gray-600">Cardiac monitoring</td>
                <td className="py-2 text-gray-600">Cardiac monitoring</td>
                <td className="py-2 text-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mx-auto" />
                </td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-2 font-medium">Technology</td>
                <td className="py-2 text-gray-600">Digital ECG</td>
                <td className="py-2 text-gray-600">Digital ECG</td>
                <td className="py-2 text-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mx-auto" />
                </td>
              </tr>
              <tr className="border-b border-gray-100">
                <td className="py-2 font-medium">Materials</td>
                <td className="py-2 text-gray-600">Medical grade plastic</td>
                <td className="py-2 text-gray-600">Similar materials</td>
                <td className="py-2 text-center">
                  <AlertCircle className="w-4 h-4 text-yellow-500 mx-auto" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderDocumentsTab = () => (
    <div className="space-y-4">
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Available Documents</h4>
        <div className="space-y-2">
          {['510(k) Summary - K123456.pdf', 'IFU Document.pdf', 'Technical Specifications.pdf', 'Clinical Data.pdf'].map((doc, index) => (
            <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex items-center space-x-3">
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-900">{doc}</span>
              </div>
              <button className="text-xs text-blue-600 hover:text-blue-800">View</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-4">
      <div>
        <h4 className="font-medium text-gray-900 mb-3">Analysis Settings</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">Similarity Threshold</span>
            <select className="text-sm border border-gray-300 rounded px-2 py-1">
              <option>80%</option>
              <option>85%</option>
              <option>90%</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">Risk Assessment</span>
            <select className="text-sm border border-gray-300 rounded px-2 py-1">
              <option>Conservative</option>
              <option>Balanced</option>
              <option>Aggressive</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">Auto-save Progress</span>
            <input type="checkbox" defaultChecked className="rounded" />
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Workspace</h2>
          {selectedDevice && (
            <p className="text-sm text-gray-500 mt-1">
              Working on: {selectedDevice.kNumber}
            </p>
          )}
        </div>
        <button
          onClick={onCollapse}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          title="Hide workspace"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }
                `}
              >
                <IconComponent className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {!selectedDevice ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Device Selected</h3>
            <p className="text-gray-500 text-sm">
              Select a device from the left panel to view analysis workspace
            </p>
          </div>
        ) : (
          <>
            {activeTab === 'analysis' && renderAnalysisTab()}
            {activeTab === 'comparison' && renderComparisonTab()}
            {activeTab === 'documents' && renderDocumentsTab()}
            {activeTab === 'settings' && renderSettingsTab()}
          </>
        )}
      </div>
    </div>
  );
}