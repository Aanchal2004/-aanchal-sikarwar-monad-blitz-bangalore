import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/** Renders agent/LLM markdown output with a clean, enterprise look. */
export default function Markdown({ children }: { children: string }) {
  return (
    <div className="text-sm leading-relaxed text-gray-700">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="mt-4 mb-2 text-base font-semibold text-gray-900 first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-4 mb-2 text-sm font-semibold text-gray-900 first:mt-0">{children}</h2>,
          h3: ({ children }) => <h3 className="mt-3 mb-1.5 text-sm font-semibold text-gray-800 first:mt-0">{children}</h3>,
          h4: ({ children }) => <h4 className="mt-3 mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500 first:mt-0">{children}</h4>,
          p: ({ children }) => <p className="mb-2.5 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="mb-2.5 ml-5 list-disc space-y-1 marker:text-indigo-400 last:mb-0">{children}</ul>,
          ol: ({ children }) => <ol className="mb-2.5 ml-5 list-decimal space-y-1 marker:text-gray-400 last:mb-0">{children}</ol>,
          li: ({ children }) => <li className="pl-1 text-gray-700">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noreferrer" className="text-indigo-600 underline hover:text-indigo-700">{children}</a>
          ),
          code: ({ children }) => <code className="rounded bg-gray-100 px-1 py-0.5 font-mono text-[0.85em] text-gray-800">{children}</code>,
          blockquote: ({ children }) => <blockquote className="my-2 border-l-2 border-indigo-200 pl-3 italic text-gray-600">{children}</blockquote>,
          hr: () => <hr className="my-3 border-gray-200" />,
          table: ({ children }) => <div className="my-2 overflow-x-auto"><table className="w-full border-collapse text-xs">{children}</table></div>,
          th: ({ children }) => <th className="border border-gray-200 bg-gray-50 px-2 py-1 text-left font-medium text-gray-600">{children}</th>,
          td: ({ children }) => <td className="border border-gray-200 px-2 py-1 text-gray-700">{children}</td>,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
