"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"

export default function RandomArticleLink() {
  const router = useRouter()

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/random-article')
      if (!response.ok) throw new Error('Failed to fetch random article')
      const article = await response.json()
      router.push(`/article/${article.slug}`)
    } catch (error) {
      console.error('Error fetching random article:', error)
    }
  }

  return (
    <Link 
      href="#"
      onClick={handleClick}
      className="text-[#36c] hover:text-[#447ff5] block py-1"
    >
      Random article
    </Link>
  )
} 