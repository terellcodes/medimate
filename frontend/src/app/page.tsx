'use client';

import { useState, useRef } from 'react';
import Header from '@/components/Header';
import Hero from '@/components/Hero';
import FeatureCards from '@/components/FeatureCards';
import FileUpload from '@/components/FileUpload';
import DocumentSummary from '@/components/DocumentSummary';
import IndicationInput from '@/components/IndicationInput';
import AnalysisResults from '@/components/AnalysisResults';
import { API_ENDPOINTS } from '../config/api';

interface DocumentSummary {
  device_name: string;
  description: string;
  indication_of_use: string;
  manufacturer: string;
}

interface AnalysisResult {
  substantially_equivalent: boolean;
  reasons: string[];
  citations: Array<{
    tool: string;
    text: string;
  }>;
  suggestions: string[];
}

export default function Home() {
  const [documentSummary, setDocumentSummary] = useState<DocumentSummary | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const functionalUIRef = useRef<HTMLElement>(null);

  const handleTryNowClick = () => {
    functionalUIRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  };

  const handleUploadSuccess = (summary: DocumentSummary) => {
    setDocumentSummary(summary);
    setAnalysisResult(null); // Reset analysis when new document is uploaded
  };

  const handleAnalyzeDevice = async (indication: string, technicalCharacteristics: string) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const response = await fetch(API_ENDPOINTS.ANALYZE_DEVICE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_device_indication: indication,
          technical_characteristics: technicalCharacteristics
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      
      if (data.success && data.analysis) {
        setAnalysisResult(data.analysis);
      } else {
        throw new Error(data.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      // You could add error state here
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      
      <Hero onTryNowClick={handleTryNowClick} />
      
      <FeatureCards />
      
      <section 
        ref={functionalUIRef}
        className="py-16 bg-white border-t border-slate-200"
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-800 mb-4">
              Try Vera Now
            </h2>
            <p className="text-lg text-slate-800">
              Upload your predicate device 510(k) document and analyze substantial equivalence
            </p>
          </div>
          
          <div className="space-y-8">
            {/* Step 1: Upload PDF */}
            <div className="bg-slate-50 rounded-xl p-8 border border-slate-200">
              <div className="flex items-center mb-4">
                <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                  1
                </div>
                <h3 className="text-lg font-semibold text-slate-800">Upload Predicate Device Document</h3>
              </div>
              <FileUpload 
                onUploadSuccess={handleUploadSuccess} 
                isUploaded={!!documentSummary}
              />
            </div>

            {/* Step 2: Document Summary */}
            {documentSummary && (
              <div className="bg-slate-50 rounded-xl p-8 border border-slate-200">
                <div className="flex items-center mb-4">
                  <div className="bg-emerald-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                    2
                  </div>
                  <h3 className="text-lg font-semibold text-slate-800">Review Document Summary</h3>
                </div>
                <DocumentSummary summary={documentSummary} />
              </div>
            )}

            {/* Step 3: New Device Input */}
            {documentSummary && (
              <div className="bg-slate-50 rounded-xl p-8 border border-slate-200">
                <div className="flex items-center mb-4">
                  <div className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                    3
                  </div>
                  <h3 className="text-lg font-semibold text-slate-800">Enter New Device Information</h3>
                </div>
                <IndicationInput 
                  onSubmit={handleAnalyzeDevice}
                  isAnalyzing={isAnalyzing}
                />
              </div>
            )}

            {/* Step 4: Analysis Results */}
            {analysisResult && (
              <div className="bg-slate-50 rounded-xl p-8 border border-slate-200">
                <div className="flex items-center mb-4">
                  <div className="bg-emerald-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                    4
                  </div>
                  <h3 className="text-lg font-semibold text-slate-800">Analysis Results</h3>
                </div>
                <AnalysisResults result={analysisResult} />
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}