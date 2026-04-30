import { useState, useRef, useEffect } from 'react';
import type { InputDefinition } from '../data/inputDefinitions';

// Small ⓘ icon next to an input label that shows a popover with the
// input's plain-English definition plus links to the statute, the IRS
// form/schedule, and the PolicyEngine variable file.
//
// Hover-driven on desktop, click-driven on touch — so mobile users can
// still pin the popover open and tap the links.
export function InfoTooltip({ definition }: { definition: InputDefinition }) {
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLSpanElement>(null);

  // Click outside closes the pinned popover.
  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, [open]);

  return (
    <span
      ref={wrapperRef}
      className="relative inline-flex align-middle ml-1.5"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
        aria-label="More info"
        className="text-pe-text-tertiary hover:text-pe-teal-600 transition-colors"
      >
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
          <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 12.5a5.5 5.5 0 110-11 5.5 5.5 0 010 11zM7.25 6.75a.75.75 0 011.5 0v4a.75.75 0 01-1.5 0v-4zM8 4.25a.9.9 0 110 1.8.9.9 0 010-1.8z" />
        </svg>
      </button>

      {open && (
        <div
          className="absolute z-30 left-0 top-5 w-72 p-3 bg-white rounded-pe-lg shadow-lg border border-pe-gray-200 text-xs text-left cursor-default"
          // Stop hover from leaving the wrapper when moving into the popover.
          onMouseEnter={() => setOpen(true)}
        >
          <p className="text-pe-text-primary leading-relaxed">{definition.description}</p>
          {(definition.statute || definition.form || definition.policyengine) && (
            <div className="flex flex-col gap-1 mt-3 pt-2.5 border-t border-pe-gray-100">
              {definition.statute && (
                <a
                  href={definition.statute.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-pe-teal-600 hover:text-pe-teal-700 hover:underline inline-flex items-center gap-1.5"
                >
                  <span aria-hidden>📜</span>
                  {definition.statute.label}
                </a>
              )}
              {definition.form && (
                <a
                  href={definition.form.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-pe-teal-600 hover:text-pe-teal-700 hover:underline inline-flex items-center gap-1.5"
                >
                  <span aria-hidden>📋</span>
                  {definition.form.label}
                </a>
              )}
              {definition.policyengine && (
                <a
                  href={definition.policyengine.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-pe-text-tertiary hover:text-pe-text-secondary hover:underline inline-flex items-center gap-1.5 font-mono"
                >
                  <span aria-hidden>🔗</span>
                  {definition.policyengine.label}
                </a>
              )}
            </div>
          )}
        </div>
      )}
    </span>
  );
}
