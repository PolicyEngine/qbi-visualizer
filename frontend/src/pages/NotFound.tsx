import { useEffect } from 'react';

// Minimal 404 view. Sets <meta name="robots" content="noindex"> so
// search engines don't index unknown paths as duplicates of the
// calculator landing page.
export default function NotFound() {
  useEffect(() => {
    const meta = document.createElement('meta');
    meta.name = 'robots';
    meta.content = 'noindex';
    document.head.appendChild(meta);
    return () => {
      document.head.removeChild(meta);
    };
  }, []);

  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-md p-8">
        <p className="text-sm font-mono text-pe-text-tertiary mb-2">404</p>
        <h2 className="text-2xl font-semibold text-pe-text-primary mb-3">Page not found</h2>
        <p className="text-sm text-pe-text-secondary mb-6">
          The page you're looking for doesn't exist. Try the QBID calculator instead.
        </p>
        <a
          href="/"
          className="inline-block px-4 py-2 bg-pe-teal-500 text-white rounded-pe-lg font-medium hover:bg-pe-teal-600 transition-colors"
        >
          Go to calculator
        </a>
      </div>
    </div>
  );
}
