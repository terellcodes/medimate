interface Citation {
  tool: string;
  text: string;
}

interface AnalysisResult {
  substantially_equivalent: boolean;
  reasons: string[];
  citations: Citation[];
  suggestions: string[];
}

interface AnalysisResultsProps {
  result: AnalysisResult;
}

export default function AnalysisResults({ result }: AnalysisResultsProps) {
  const isEquivalent = result.substantially_equivalent;

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Substantial Equivalence Analysis
      </h3>
      
      <div className={`
        rounded-lg p-6 border-2 mb-6
        ${isEquivalent 
          ? 'bg-green-50 border-green-200' 
          : 'bg-red-50 border-red-200'
        }
      `}>
        <div className="flex items-center mb-4">
          <div className={`text-3xl mr-3 ${isEquivalent ? 'text-green-600' : 'text-red-600'}`}>
            {isEquivalent ? '✅' : '❌'}
          </div>
          <div>
            <h4 className={`text-xl font-semibold ${isEquivalent ? 'text-green-800' : 'text-red-800'}`}>
              {isEquivalent ? 'Substantially Equivalent' : 'Not Substantially Equivalent'}
            </h4>
            <p className={`text-sm ${isEquivalent ? 'text-green-700' : 'text-red-700'}`}>
              Based on FDA 510(k) guidelines and predicate device analysis
            </p>
          </div>
        </div>
      </div>

      {/* Reasons */}
      <div className="mb-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Analysis Reasoning</h4>
        <ul className="space-y-2">
          {result.reasons.map((reason, index) => (
            <li key={index} className="flex items-start">
              <span className="text-blue-600 mr-2 mt-1">•</span>
              <span className="text-gray-700">{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-semibold text-gray-900 mb-3">
            {isEquivalent ? 'Next Steps' : 'Recommendations'}
          </h4>
          <ul className="space-y-2">
            {result.suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="text-amber-600 mr-2 mt-1">→</span>
                <span className="text-gray-700">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Citations */}
      {result.citations.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Supporting Evidence</h4>
          <div className="space-y-3">
            {result.citations.map((citation, index) => (
              <div key={index} className="bg-white p-3 rounded border border-gray-200">
                <div className="text-xs font-medium text-gray-500 mb-1">
                  Source: {citation.tool === 'fda_guidelines' ? 'FDA Guidelines' : 'Predicate Device'}
                </div>
                <p className="text-sm text-gray-700 italic">"{citation.text}"</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}