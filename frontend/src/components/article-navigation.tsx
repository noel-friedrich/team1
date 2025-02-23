"use client"

import type { Article } from "@/lib/articles"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, ArrowRight, ThumbsDown, ThumbsUp } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

export function ArticleNavigation({
  article,
  nextArticle,
  previousArticle,
}: {
  article: Article
  nextArticle: Article | undefined
  previousArticle: Article | undefined
}) {
  const [votes, setVotes] = useState(article.votes)

  const handleVote = (type: "up" | "down") => {
    setVotes((prev) => ({
      ...prev,
      [type]: prev[type] + 1,
    }))
  }

  return (
    <Card className="mb-6">
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">Article {article.id} of 6</div>
          <div className="flex items-center gap-2">
            {previousArticle && (
              <Button asChild variant="ghost" size="sm">
                <Link href={`/wiki/${previousArticle.slug}`}>
                  <ArrowLeft className="mr-1 h-4 w-4" />
                  Previous: {previousArticle.title}
                </Link>
              </Button>
            )}
            {nextArticle && (
              <Button asChild variant="ghost" size="sm">
                <Link href={`/wiki/${nextArticle.slug}`}>
                  Next: {nextArticle.title}
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => handleVote("up")} className="text-green-600">
              <ThumbsUp className="mr-1 h-4 w-4" />
              {votes.up}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => handleVote("down")} className="text-red-600">
              <ThumbsDown className="mr-1 h-4 w-4" />
              {votes.down}
            </Button>
          </div>
          <div className="text-sm text-muted-foreground">
            Created on {new Date(article.createdAt).toLocaleDateString()}
          </div>
        </div>
      </div>
    </Card>
  )
}

