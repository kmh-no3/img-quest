import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'IMG-Quest',
  description: '導入の意思決定フローを疑似体験し、必要設定・成果物を自動生成するWebアプリ',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="bg-primary-600 text-white shadow-lg">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <h1 className="text-2xl font-bold">IMG-Quest</h1>
                  <span className="text-primary-200 text-sm">v0.1</span>
                </div>
                <nav className="flex items-center space-x-6">
                  <a href="/" className="hover:text-primary-100 transition-colors">
                    プロジェクト
                  </a>
                  <a href="/guide" className="hover:text-primary-100 transition-colors flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    使い方ガイド
                  </a>
                  <a href="/about" className="hover:text-primary-100 transition-colors">
                    About
                  </a>
                </nav>
              </div>
            </div>
          </header>
          
          <main className="flex-1 container mx-auto px-4 py-8">
            {children}
          </main>
          
          <footer className="bg-gray-100 border-t border-gray-200">
            <div className="container mx-auto px-4 py-6 text-center text-gray-600 text-sm">
              <p>IMG-Quest - Turn decisions into configuration.</p>
              <p className="mt-2">教育・支援用途 | SAP社とは無関係</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
