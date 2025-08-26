'use client';

import { useState } from 'react';

interface IndicationInputProps {
  onSubmit: (indication: string, technicalCharacteristics: string) => void;
  isAnalyzing: boolean;
}

export default function IndicationInput({ onSubmit, isAnalyzing }: IndicationInputProps) {
  const [indication, setIndication] = useState('');
  const [technicalCharacteristics, setTechnicalCharacteristics] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (indication.trim() && technicalCharacteristics.trim() && !isAnalyzing) {
      onSubmit(indication.trim(), technicalCharacteristics.trim());
    }
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Your Device&apos;s Intended Uses
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="indication" className="block text-sm font-medium text-gray-700 mb-2">
            Enter the intended use statement for your device to check substantial equivalence:
          </label>
          <textarea
            id="indication"
            value={indication}
            onChange={(e) => setIndication(e.target.value)}
            className="w-full h-32 p-4 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-slate-900 placeholder-slate-500 bg-white"
            placeholder="For balloon dilatation of a hemodynamically significant coronary artery or bypass graft stenosis in patients evidencing coronary ischemia, to improve myocardial perfusion"
            disabled={isAnalyzing}
          />
          <p className="text-xs text-gray-500 mt-1">
            💡 Tip: Provide a clear and specific description of what your device is intended to do, similar to how predicate devices describe their intended use.
          </p>
        </div>

        <div>
          <label htmlFor="technicalCharacteristics" className="block text-sm font-medium text-gray-700 mb-2">
            Enter the technical characteristics of your device:
          </label>
          <textarea
            id="technicalCharacteristics"
            value={technicalCharacteristics}
            onChange={(e) => setTechnicalCharacteristics(e.target.value)}
            className="w-full h-32 p-4 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-slate-900 placeholder-slate-500 bg-white"
            placeholder="Example: Single-use balloon catheter with semi-compliant balloon, 0.014&quot; guidewire compatibility, balloon diameters 2.0-4.0mm, lengths 8-40mm, rated burst pressure 14-20 ATM..."
            disabled={isAnalyzing}
          />
          <p className="text-xs text-gray-500 mt-1">
            💡 Tip: Include key technical specifications like materials, dimensions, operating parameters, and performance characteristics.
          </p>
        </div>
        
        <button
          type="submit"
          disabled={!indication.trim() || !technicalCharacteristics.trim() || isAnalyzing}
          className={`
            w-full py-3 px-6 rounded-lg text-white font-semibold transition duration-200
            ${!indication.trim() || !technicalCharacteristics.trim() || isAnalyzing
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