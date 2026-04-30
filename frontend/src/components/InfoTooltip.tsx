import { useState, useRef, useEffect, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';
import type { InputDefinition } from '../data/inputDefinitions';

// Small ⓘ icon next to an input label that shows a popover with the
// input's plain-English definition plus links to the statute, the IRS
// form/schedule, and the PolicyEngine variable file.
//
// The popover renders into document.body via a React portal with fixed
// positioning so it escapes parent overflow clipping (the inputs panel
// has overflow-y: auto which would otherwise crop the popover).
export function InfoTooltip({ definition }: { definition: InputDefinition }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });
  const wrapperRef = useRef<HTMLSpanElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<number | null>(null);

  const POPOVER_WIDTH = 288;
  const VIEWPORT_PADDING = 8;

  const cancelClose = () => {
    if (closeTimer.current !== null) {
      window.clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  };
  const scheduleClose = () => {
    cancelClose();
    closeTimer.current = window.setTimeout(() => setOpen(false), 200);
  };

  // Position the popover under the icon, shifted left if it would
  // overflow the viewport's right edge.
  useLayoutEffect(() => {
    if (!open || !buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    let left = rect.left;
    const overflowRight = left + POPOVER_WIDTH - (window.innerWidth - VIEWPORT_PADDING);
    if (overflowRight > 0) left -= overflowRight;
    if (left < VIEWPORT_PADDING) left = VIEWPORT_PADDING;
    setPos({ top: rect.bottom + 6, left });
  }, [open]);

  // Click-outside closes the popover.
  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      const target = e.target as Node;
      if (wrapperRef.current?.contains(target)) return;
      if (popoverRef.current?.contains(target)) return;
      setOpen(false);
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, [open]);

  useEffect(() => () => cancelClose(), []);

  return (
    <>
      <span
        ref={wrapperRef}
        className="relative inline-flex align-middle ml-1.5"
        onMouseEnter={() => {
          cancelClose();
          setOpen(true);
        }}
        onMouseLeave={scheduleClose}
      >
        <button
          ref={buttonRef}
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            setOpen((v) => !v);
          }}
          aria-label="More info"
          className="text-pe-text-tertiary hover:text-pe-teal-600 transition-colors"
        >
          <svg className="w-4 h-4" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
            <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 12.5a5.5 5.5 0 110-11 5.5 5.5 0 010 11zM7.25 6.75a.75.75 0 011.5 0v4a.75.75 0 01-1.5 0v-4zM8 4.25a.9.9 0 110 1.8.9.9 0 010-1.8z" />
          </svg>
        </button>
      </span>

      {open &&
        createPortal(
          <div
            ref={popoverRef}
            style={{ top: pos.top, left: pos.left, width: POPOVER_WIDTH }}
            className="fixed z-50 p-3 bg-white rounded-pe-lg shadow-lg border border-pe-gray-200 text-xs text-left cursor-default normal-case font-normal"
            onMouseEnter={cancelClose}
            onMouseLeave={scheduleClose}
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
                    className="text-pe-text-tertiary hover:text-pe-text-secondary hover:underline inline-flex items-center gap-1.5 font-mono text-[11px]"
                  >
                    <span aria-hidden>🔗</span>
                    {definition.policyengine.label}
                  </a>
                )}
              </div>
            )}
          </div>,
          document.body
        )}
    </>
  );
}
