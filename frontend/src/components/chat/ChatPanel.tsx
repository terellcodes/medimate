'use client';

import { useState } from 'react';
import { useAssistant } from '@assistant-ui/react';
import { Building2, MessageSquare, Send } from 'lucide-react';
import WorkflowPills from './WorkflowPills';

interface Device {
  id: string;
  name: string;
  kNumber: string;
  classification: string;
  status: 'cleared' | 'withdrawn';
  clearanceDate: string;
  description: string;
}

interface ChatPanelProps {
  selectedDevice: Device | null;
  sessionId: string | null;
}

export default function ChatPanel({ selectedDevice, sessionId }: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Call our mock API
      const response = await fetch('/api/assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });
      
      if (!response.ok) throw new Error('Failed to get response');
      
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');
      
      let assistantContent = '';
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: '',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Stream the response
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        assistantContent += chunk;
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { ...msg, content: assistantContent }
            : msg
        ));
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePillClick = (pillType: 'regulatory-pathway' | 'predicate-discovery' | 'ifu-validation') => {
    const pillMessages = {
      'regulatory-pathway': 'Please guide me through the regulatory pathway for my device.',
      'predicate-discovery': 'Help me find predicate devices for substantial equivalence analysis.',
      'ifu-validation': 'Validate my device\'s Indications for Use (IFU) statement.'
    };
    
    handleSendMessage(pillMessages[pillType]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {selectedDevice ? `Analysis: ${selectedDevice.name}` : 'FDA 510(k) Assistant'}
              </h2>
              {selectedDevice && (
                <p className="text-sm text-gray-500 flex items-center">
                  <Building2 className="w-3 h-3 mr-1" />
                  {selectedDevice.kNumber} • {selectedDevice.classification}
                </p>
              )}
            </div>
          </div>
          {sessionId && (
            <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              Session: {sessionId.split('-').slice(-1)[0]}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Vera Chat
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              I'm your FDA 510(k) analysis assistant. Use the workflow buttons below or ask me anything about regulatory pathways, predicate discovery, or IFU validation.
            </p>
            {selectedDevice && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                <p className="text-sm text-blue-800">
                  <strong>Selected Device:</strong> {selectedDevice.name} ({selectedDevice.kNumber})
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  Ready to analyze substantial equivalence
                </p>
              </div>
            )}
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[80%] rounded-lg px-4 py-3 
                ${message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
                }
              `}
            >
              <div className="whitespace-pre-wrap text-sm">
                {message.content}
              </div>
              <div
                className={`
                  text-xs mt-2 opacity-70
                  ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}
                `}
              >
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        {/* Workflow Pills */}
        <WorkflowPills onPillClick={handlePillClick} />
        
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={selectedDevice 
                ? `Ask about ${selectedDevice.name} analysis...`
                : 'Ask me about FDA 510(k) analysis...'
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        
        <div className="text-xs text-gray-500 mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}