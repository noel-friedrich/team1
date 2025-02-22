// import type React from "react"
// import type { Metadata } from "next"
// import { Inter } from "next/font/google"
// import "./globals.css"
// import { Navigation } from "@/components/navigation"

// const inter = Inter({ subsets: ["latin"] })

// export const metadata: Metadata = {
//   title: "Williampedia",
//   description: "The AI-powered knowledge engine",
// }

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode
// }) {
//   return (
//     <html lang="en">
//       <body className={inter.className}>
//         <div className="flex min-h-screen flex-col lg:flex-row">
//           <Navigation />
//           <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
//         </div>
//       </body>
//     </html>
//   )
// }


import type React from "react"
import "./globals.css"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Wikipedia - The Free Encyclopedia",
  description: "The free encyclopedia that anyone can edit.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Linux+Libertine:wght@400;700&display=swap"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}

