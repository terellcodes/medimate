'use client';

import { useState } from 'react';
import { SearchParams } from '@/types/predicate';

interface SearchFormProps {
  onSearch: (params: SearchParams) => void;
  isLoading: boolean;
}

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [productCode, setProductCode] = useState('');
  const [maxDownloads, setMaxDownloads] = useState(5);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!searchTerm.trim() && !productCode.trim()) {
      setError('Please provide either a device keyword or product code');
      return;
    }

    const params: SearchParams = {
      searchTerm: searchTerm.trim() || undefined,
      productCode: productCode.trim() || undefined,
      maxDownloads,
      includeRecalled: false
    };

    onSearch(params);
  };

  return (
    <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
      <div className="flex items-center mb-6">
        <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
          1
        </div>
        <h3 className="text-lg font-semibold text-slate-800">Search for Predicate Devices</h3>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search Fields */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="searchTerm" className="block text-sm font-medium text-slate-900 mb-2">
              Device Keyword
            </label>
            <input
              type="text"
              id="searchTerm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="e.g., catheter, stent, defibrillator"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p className="text-xs text-slate-900 mt-1">
              Search by device name or technology
            </p>
          </div>
          
          <div>
            <label htmlFor="productCode" className="block text-sm font-medium text-slate-900 mb-2">
              Product Code (Optional)
            </label>
            <input
              type="text"
              id="productCode"
              value={productCode}
              onChange={(e) => setProductCode(e.target.value.toUpperCase())}
              placeholder="e.g., DYB, NIQ, BSZ"
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p className="text-xs text-slate-900 mt-1">
              FDA product classification code
            </p>
          </div>
        </div>

        {/* Max Downloads */}
        <div className="max-w-xs">
          <label htmlFor="maxDownloads" className="block text-sm font-medium text-slate-900 mb-2">
            Maximum PDF Downloads
          </label>
          <select
            id="maxDownloads"
            value={maxDownloads}
            onChange={(e) => setMaxDownloads(Number(e.target.value))}
            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            {[1, 2, 3, 4, 5, 10].map(num => (
              <option key={num} value={num}>
                {num} PDF{num > 1 ? 's' : ''}
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-900 mt-1">
            Limit automatic downloads for faster results
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={isLoading}
            className="bg-green-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-600 transition duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Searching...
              </div>
            ) : (
              'Find Predicates'
            )}
          </button>
        </div>
      </form>

      {/* Tips */}
      <div className="mt-6 p-4 bg-slate-50 rounded-lg">
        <h4 className="text-sm font-medium text-slate-800 mb-2">Search Tips:</h4>
        <ul className="text-xs text-slate-900 space-y-1">
          <li>• Use specific terms like "cardiac catheter" rather than just "catheter"</li>
          <li>• Product codes provide more precise results (e.g., DYB for cardiac catheters)</li>
          <li>• Combine both keyword and product code for best results</li>
        </ul>
      </div>
    </div>
  );
}