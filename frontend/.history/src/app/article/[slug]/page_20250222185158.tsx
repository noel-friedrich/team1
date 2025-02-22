import Link from "next/link"
import { Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import WikiLogo from "@/components/wiki-logo"
import type { Metadata } from "next"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import VoteButtons from "@/components/vote-buttons"
import Markdown from "@/components/markdown"
import Image from "next/image"

type Props = {
  params: { slug: string }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/article/${params.slug}`, { cache: "no-store" })
  if (!res.ok) {
    // fallback title if article is not found
    const title = params.slug.replace(/_/g, " ")
    return { title: `${title} - Williampedia` }
  }
  const article = await res.json()
  return {
    title: `${article.title} - Williampedia`
  }
}

export default async function ArticlePage({ params }: Props) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/article/${params.slug}`, { cache: "no-store" })
  if (!res.ok) return <div>Article not found</div>
  const article = await res.json()

  return (
    <div className="min-h-screen bg-white text-[#202122] flex">
      {/* Sidebar with the Williampedia logo */}
      <aside className="w-[14rem] p-4 border-r min-h-screen text-[0.875rem] hidden lg:block">
        <div className="mb-6 flex items-center gap-2">
          <span className="font-serif text-xl">Williampedia</span>
        </div>
        <nav className="space-y-6">
          <div>
            <div className="font-medium mb-2 text-[#54595d]">Navigation</div>
            <ul className="space-y-1">
              <li>
                <Link href="/" className="text-[#36c] hover:text-[#447ff5] block py-1">
                  Main page
                </Link>
              </li>
              <li>
                <Link href="/history" className="text-[#36c] hover:text-[#447ff5] block py-1">
                  Recent changes
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#36c] hover:text-[#447ff5] block py-1">
                  Random article
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <div className="font-medium mb-2 text-[#54595d]">Contribute</div>
            <ul className="space-y-1">
              <li>
                <Link href="#" className="text-[#36c] hover:text-[#447ff5] block py-1">
                  Help
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#36c] hover:text-[#447ff5] block py-1">
                  About
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar: Search bar */}
        <nav className="border-b">
          <div className="max-w-[960px] mx-auto px-4 flex justify-center items-center h-14">
            <div className="relative w-full max-w-xl">
              <Input
                type="search"
                placeholder="Search Williampedia"
                className="w-full pl-4 pr-10"
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2"
              >
                <Search className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </nav>

        {/* Tab Navigation */}
        <div className="border-b">
          <div className="flex text-[0.875rem]">
            <div className="flex border-b border-primary -mb-px">
              <Button
                variant="ghost"
                className="rounded-none px-4 py-2 h-auto text-sm font-medium"
              >
                Article
              </Button>
            </div>
            <div className="flex ml-auto">
              <Button variant="ghost" className="rounded-none px-4 py-2 h-auto text-sm">
                Read
              </Button>
              <Button variant="ghost" className="rounded-none px-4 py-2 h-auto text-sm">
                Edit
              </Button>
            </div>
          </div>
        </div>

        {/* Centered Article Content */}
        <main className="flex-1 flex justify-center">
          <div className="w-full max-w-[960px]">
            <article className="p-6 text-[0.875rem] leading-[1.6]">
              {/* Top Info Row */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">AI-Generated</Badge>
                  <span className="text-muted-foreground">
                    Created on {article.createdAt ? new Date(article.createdAt).toLocaleDateString() : 'Unknown date'}
                  </span>
                </div>
                <VoteButtons articleId={article.id} votes={article.votes} />
              </div>

              {/* Article Title */}
              <h1 className="text-[2rem] font-serif mb-4">{article.title}</h1>

              {/* Article Image */}
              {article.image_url && (
                <div className="float-right ml-6 mb-4 w-[400px]">
                  <figure className="border rounded p-2 bg-gray-50">
                    <Image
                      src={article.image_url}
                      alt={article.title}
                      width={400}
                      height={300}
                      className="w-full h-auto"
                    />
                  </figure>
                </div>
              )}

              {/* Article Body */}
              <div className="prose max-w-none wiki-article">
                <Markdown content={article.content} />
              </div>
            </article>
          </div>
        </main>
      </div>
    </div>
  )
}
