'use client';

import { useState } from 'react';
import HelpModal from './HelpModal';
import { helpContent } from '@/lib/help-content';

interface HelpButtonProps {
  pageKey: string;
}

export default function HelpButton({ pageKey }: HelpButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const content = helpContent[pageKey];

  if (!content) {
    console.warn(`Help content not found for key: ${pageKey}`);
    return null;
  }

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 hover:bg-primary-100 border border-primary-200 rounded-lg transition-colors"
        aria-label="ヘルプを表示"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        ヘルプ
      </button>
      <HelpModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        content={content}
      />
    </>
  );
}
