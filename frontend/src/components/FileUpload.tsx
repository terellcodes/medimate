'use client';

import { useState } from 'react';

interface DocumentSummary {
  device_name: string;
  description: string;
  indication_of_use: string;
  manufacturer: string;
}

interface FileUploadProps {
  onUploadSuccess: (summary: DocumentSummary) => void;
  isUploaded?: boolean;
}

export default function FileUpload({ onUploadSuccess, isUploaded = false }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    if (isUploaded) {
      setError('A document has already been uploaded. Please refresh to upload a new document.');
      return;
    }

    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload_pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      if (data.success && data.document_summary) {
        onUploadSuccess(data.document_summary);
      } else {
        throw new Error(data.message || 'Upload failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">
        Upload 510(K) Document for Predicate Device
      </h3>
      
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isUploaded 
            ? 'border-emerald-300 bg-emerald-50 opacity-75 cursor-not-allowed' 
            : dragActive 
              ? 'border-green-500 bg-green-50' 
              : 'border-slate-300'
          }
          ${isUploading || isUploaded 
            ? 'opacity-50 cursor-not-allowed' 
            : 'cursor-pointer hover:border-slate-400'
          }
        `}
        onDragOver={(e) => {
          e.preventDefault();
          if (!isUploaded) setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !isUploading && !isUploaded && document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="hidden"
          disabled={isUploading || isUploaded}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mb-4"></div>
            <p className="text-gray-600">Processing PDF...</p>
          </div>
        ) : isUploaded ? (
          <div className="flex flex-col items-center">
            <div className="text-4xl mb-4">✅</div>
            <p className="text-lg text-emerald-700 mb-2 font-medium">
              Document Successfully Uploaded
            </p>
            <p className="text-sm text-emerald-600">
              PDF processed and ready for analysis
            </p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-4">📄</div>
            <p className="text-lg text-slate-700 mb-2">
              Drop your 510(K) PDF here or click to browse
            </p>
            <p className="text-sm text-slate-500">
              PDF files only, up to 10MB
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}