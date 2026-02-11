import { Suspense } from 'react';
import BacklogClient from './BacklogClient';

export function generateStaticParams() {
  return [];
}

export default function Page() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>読み込み中...</p></div>}>
      <BacklogClient />
    </Suspense>
  );
}
