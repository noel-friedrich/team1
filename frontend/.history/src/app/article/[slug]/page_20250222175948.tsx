import { notFound } from "next/navigation"
import type { Metadata } from "next"

type Props = {
  params: { slug: string }
}

async function fetchArticle(slug: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/article/${slug}`)
  if (!res.ok) return null
  return res.json()
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const article = await fetchArticle(params.slug)
  return {
    title: article?.title ? `${article.title} - Williampedia` : "Not Found",
  }
}

export default async function ArticlePage({ params }: Props) {
  const article = await fetchArticle(params.slug)
  if (!article) return notFound()

  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">{article.title}</h1>
        <div className="prose">{article.content}</div>
      </main>
    </div>
  )
}
