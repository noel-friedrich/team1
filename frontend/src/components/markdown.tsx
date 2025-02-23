"use client"

import ReactMarkdown from "react-markdown"
import Link from "next/link"

export default function Markdown({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        h2: ({ children }) => <h2 className="text-[1.5rem] font-serif mt-6 mb-3 pb-1 border-b">{children}</h2>,
        h3: ({ children }) => <h3 className="text-[1.3rem] font-serif mt-4 mb-2">{children}</h3>,
        p: ({ children }) => <p className="text-[0.875rem] font-serif leading-[1.6] mb-4 font-[Liberation Sans]">{children}</p>,
        ul: ({ children }) => <ul className="list-disc font-serif pl-6 mb-4 space-y-1 text-[0.875rem]">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal font-serif pl-6 mb-4 space-y-1 text-[0.875rem]">{children}</ol>,
        li: ({ children }) => <li className="text-[0.875rem] font-serif leading-[1.6]">{children}</li>,
        a: ({ href, children }) => (
          <Link href={href || "#"} className="text-[#36c] hover:text-[#447ff5] hover:underline">
            {children}
          </Link>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

