const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'

export async function fetchArticle(slug: string) {
  const res = await fetch(`${baseUrl}/api/article/${slug}`, {
    // Add cache: 'no-store' to disable caching if needed
    // cache: 'no-store'
  })
  if (!res.ok) return null
  return res.json()
}

export async function fetchAdjacentArticles(currentId: string) {
  const res = await fetch(`${baseUrl}/api/article/${currentId}/adjacent`, {
    // Add cache: 'no-store' to disable caching if needed
    // cache: 'no-store'
  })
  if (!res.ok) return { prev: null, next: null }
  return res.json()
} 