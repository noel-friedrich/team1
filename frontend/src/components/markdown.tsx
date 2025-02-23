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

// "use client"

// import ReactMarkdown from "react-markdown"
// import Link from "next/link"

// // Define the mapping of phrases to MongoDB IDs
// const PHRASE_TO_ID_MAP: Record<string, string> = {
//   "Joyce": "67bb040c35434446a359dfc5",
//   "stream-of-consciousness technique": "67bb041b35434446a359dfc6",
//   "Joyce draws": "67bb040c35434446a359dfc5",
//   "Joyce reinterprets": "67bb040c35434446a359dfc5",
//   "stream-of-consciousness Joyce": "67bb041b35434446a359dfc6",
//   "Joyce captures": "67bb040c35434446a359dfc5"
// }

// // Define mapping of MongoDB IDs to slugs
// const ID_TO_SLUG_MAP: Record<string, string> = {
//   "67bb040c35434446a359dfc5": "james-joyce",
//   "67bb041b35434446a359dfc6": "stream-of-consciousness-technique"
// }

// export default function Markdown({ content, currentSlug }: { content: string, currentSlug?: string }) {
//   // Function to create a link for a matched phrase
//   const createLink = (phrase: string) => {
//     const mongoId = PHRASE_TO_ID_MAP[phrase];
//     const slug = ID_TO_SLUG_MAP[mongoId];
//     // Don't create a link if it points to the current page
//     if (slug && slug !== currentSlug) {
//       return `<a href="/article/${slug}" class="text-[#36c] hover:text-[#447ff5] hover:underline">${phrase}</a>`;
//     }
//     return phrase;
//   };

//   // Function to process text and add links
//   const processText = (text: string) => {
//     let result = text;
    
//     // Sort phrases by length (longest first) to avoid partial matches
//     const phrases = Object.keys(PHRASE_TO_ID_MAP).sort((a, b) => b.length - a.length);
    
//     for (const phrase of phrases) {
//       const regex = new RegExp(`(${phrase})`, 'g');
//       result = result.replace(regex, createLink(phrase));
//     }
    
//     return result;
//   }

//   return (
//     <ReactMarkdown
//       components={{
//         h2: ({ children }) => <h2 className="text-[1.5rem] font-serif mt-6 mb-3 pb-1 border-b">{children}</h2>,
//         h3: ({ children }) => <h3 className="text-[1.3rem] font-serif mt-4 mb-2">{children}</h3>,
//         p: ({ children }) => {
//           if (typeof children === 'string') {
//             // Create element with processed HTML
//             return <p className="text-[0.875rem] font-serif leading-[1.6] mb-4 font-[Liberation Sans]" 
//                       dangerouslySetInnerHTML={{ __html: processText(children) }} />;
//           }
//           return <p className="text-[0.875rem] font-serif leading-[1.6] mb-4 font-[Liberation Sans]">{children}</p>;
//         },
//         ul: ({ children }) => <ul className="list-disc font-serif pl-6 mb-4 space-y-1 text-[0.875rem]">{children}</ul>,
//         ol: ({ children }) => <ol className="list-decimal font-serif pl-6 mb-4 space-y-1 text-[0.875rem]">{children}</ol>,
//         li: ({ children }) => <li className="text-[0.875rem] font-serif leading-[1.6]">{children}</li>,
//         a: ({ href, children }) => (
//           <Link href={href || "#"} className="text-[#36c] hover:text-[#447ff5] hover:underline">
//             {children}
//           </Link>
//         ),
//       }}
//     >
//       {content}
//     </ReactMarkdown>
//   )
// }

