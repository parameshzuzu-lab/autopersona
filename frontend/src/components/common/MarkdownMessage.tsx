import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Check, Copy } from 'lucide-react';

interface MarkdownMessageProps {
  content: string;
}

export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content }) => {
  const [copied, setCopied] = useState<string | null>(null);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(code);
    setTimeout(() => setCopied(null), 1800);
  };

  return (
    <div className="markdown-body text-sm text-slate-200 leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const codeText = String(children).replace(/\n$/, '');
            if (match) {
              return (
                <div className="relative group my-3 overflow-hidden rounded-xl border border-slate-700/70 bg-slate-950/90">
                  <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-700/60">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">
                      {match[1]}
                    </span>
                    <button
                      onClick={() => handleCopy(codeText)}
                      className="flex items-center space-x-1 text-[10px] font-mono text-slate-400 hover:text-cyan-300 transition-colors px-1 py-0.5"
                    >
                      {copied === codeText ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="p-3 overflow-x-auto text-[12.5px] leading-relaxed">
                    <code className={className}>{children}</code>
                  </pre>
                </div>
              );
            }
            return (
              <code
                className="px-1.5 py-0.5 mx-0.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-cyan-300 text-[12px] font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },
          a({ node, children, ...props }) {
            return (
              <a
                {...props}
                target="_blank"
                rel="noreferrer"
                className="text-cyan-400 hover:text-cyan-300 hover:underline"
              >
                {children}
              </a>
            );
          },
          h1: (props) => <h1 className="text-lg font-bold text-white mt-3 mb-1.5" {...props} />,
          h2: (props) => <h2 className="text-base font-bold text-white mt-3 mb-1.5" {...props} />,
          h3: (props) => <h3 className="text-sm font-bold text-cyan-300 mt-2.5 mb-1" {...props} />,
          ul: (props) => <ul className="list-disc pl-5 my-1.5 space-y-1" {...props} />,
          ol: (props) => <ol className="list-decimal pl-5 my-1.5 space-y-1" {...props} />,
          li: (props) => <li className="text-slate-300" {...props} />,
          p: (props) => <p className="my-1.5" {...props} />,
          strong: (props) => <strong className="text-slate-50 font-semibold" {...props} />,
          blockquote: (props) => (
            <blockquote
              className="border-l-2 border-cyan-500/50 pl-3 my-2 text-slate-400 italic"
              {...props}
            />
          ),
          table: (props) => (
            <div className="overflow-x-auto my-2">
              <table className="min-w-full text-xs border-collapse" {...props} />
            </div>
          ),
          th: (props) => (
            <th className="border border-slate-700 px-2 py-1 text-left text-slate-100 font-semibold" {...props} />
          ),
          td: (props) => <td className="border border-slate-700 px-2 py-1 text-slate-300" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};