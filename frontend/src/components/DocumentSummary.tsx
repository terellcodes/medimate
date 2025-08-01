interface DocumentSummary {
  device_name: string;
  description: string;
  indication_of_use: string;
  manufacturer: string;
}

interface DocumentSummaryProps {
  summary: DocumentSummary;
}

export default function DocumentSummary({ summary }: DocumentSummaryProps) {
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Predicate Device Summary
      </h3>
      
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <div className="text-green-600 text-2xl mr-3">✅</div>
          <p className="text-green-800 font-medium">Document processed successfully</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Device Name</label>
            <p className="text-gray-900 mt-1">{summary.device_name}</p>
          </div>
          
          <div>
            <label className="text-sm font-medium text-gray-700">Manufacturer</label>
            <p className="text-gray-900 mt-1">{summary.manufacturer}</p>
          </div>
          
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-gray-700">Description</label>
            <p className="text-gray-900 mt-1">{summary.description}</p>
          </div>
          
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-gray-700">Indication of Use</label>
            <p className="text-gray-900 mt-1 bg-white p-3 rounded border border-green-300">
              {summary.indication_of_use}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}