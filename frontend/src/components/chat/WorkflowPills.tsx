'use client';

import { Building2, Search, FileCheck } from 'lucide-react';

interface WorkflowPillsProps {
  onPillClick: (pillType: 'regulatory-pathway' | 'predicate-discovery' | 'ifu-validation') => void;
}

export default function WorkflowPills({ onPillClick }: WorkflowPillsProps) {
  const pills = [
    {
      id: 'regulatory-pathway' as const,
      icon: Building2,
      label: 'Regulatory Pathway',
      description: 'Guide through 510(k) vs PMA vs De Novo',
      color: 'bg-blue-100 hover:bg-blue-200 text-blue-800 border-blue-300'
    },
    {
      id: 'predicate-discovery' as const,
      icon: Search,
      label: 'Predicate Discovery',
      description: 'Find suitable predicate devices',
      color: 'bg-green-100 hover:bg-green-200 text-green-800 border-green-300'
    },
    {
      id: 'ifu-validation' as const,
      icon: FileCheck,
      label: 'IFU Validation',
      description: 'Validate Instructions for Use',
      color: 'bg-purple-100 hover:bg-purple-200 text-purple-800 border-purple-300'
    }
  ];

  return (
    <div className="mb-4">
      <div className="text-xs text-gray-500 mb-2 font-medium">Quick Actions:</div>
      <div className="flex flex-wrap gap-2">
        {pills.map((pill) => {
          const IconComponent = pill.icon;
          return (
            <button
              key={pill.id}
              onClick={() => onPillClick(pill.id)}
              className={`
                flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all duration-200
                text-sm font-medium ${pill.color}
                hover:shadow-sm active:scale-95
              `}
              title={pill.description}
            >
              <IconComponent className="w-4 h-4" />
              <span>{pill.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}