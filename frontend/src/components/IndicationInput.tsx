'use client';

import { useState } from 'react';

interface IndicationInputProps {
  onSubmit: (indication: string) => void;
  isAnalyzing: boolean;
}

export default function IndicationInput({ onSubmit, isAnalyzing }: IndicationInputProps) {
  const [indication, setIndication] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (indication.trim() && !isAnalyzing) {
      onSubmit(indication.trim());
    }
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        New Device Indication for Use
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="indication" className="block text-sm font-medium text-gray-700 mb-2">
            Enter the indication for use of your new device:
          </label>
          <textarea
            id="indication"
            value={indication}
            onChange={(e) => setIndication(e.target.value)}
            className="w-full h-32 p-4 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-slate-900 placeholder-slate-500 bg-white"
            placeholder="Example: For use in the non-invasive diagnosis of coronary artery disease in adult patients through measurement of fractional flow reserve."
            disabled={isAnalyzing}
          />
        </div>
        
        <button
          type="submit"
          disabled={!indication.trim() || isAnalyzing}
          className={`
            w-full py-3 px-6 rounded-lg text-white font-semibold transition duration-200
            ${!indication.trim() || isAnalyzing
              ? 'bg-slate-400 cursor-not-allowed'
              : 'bg-green-500 hover:bg-green-600 shadow-lg hover:shadow-xl'
            }
          `}
        >
          {isAnalyzing ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Analyzing Substantial Equivalence...
            </div>
          ) : (
            'Analyze Substantial Equivalence'
          )}
        </button>
      </form>
    </div>
  );
}