"use client"

import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

type VoteButtonsProps = {
  articleId: string
  votes: {
    up: number
    down: number
  }
}

export default function VoteButtons({ articleId }: VoteButtonsProps) {
  const [voted, setVoted] = useState<"up" | "down" | null>(null)
  const [isAnimating, setIsAnimating] = useState(false)

  const handleVote = async (type: "up" | "down") => {
    // If clicking the same button, remove the vote
    if (voted === type) {
      setVoted(null)
      // Send vote removal to API
      await fetch(`/api/articles/${articleId}/vote`, {
        method: 'DELETE'
      });
      return
    }

    // Send vote to API
    await fetch(`/api/articles/${articleId}/vote`, {
      method: 'POST',
      body: JSON.stringify({ type })
    });

    // Trigger animation
    setIsAnimating(true)
    // Reset animation after it completes
    setTimeout(() => setIsAnimating(false), 500)

    setVoted(type)
  }

  return (
    <div className="flex items-center gap-4">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleVote("up")}
        className={cn(
          "flex items-center gap-2 transition-all",
          voted === "up" && "text-green-600 scale-110",
          "hover:text-green-600 hover:scale-110",
        )}
      >
        <ThumbsUp
          className={cn(
            "w-4 h-4 transition-transform duration-200",
            voted === "up" && isAnimating && "animate-bounce-once",
          )}
        />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleVote("down")}
        className={cn(
          "flex items-center gap-2 transition-all",
          voted === "down" && "text-red-600 scale-110",
          "hover:text-red-600 hover:scale-110",
        )}
      >
        <ThumbsDown
          className={cn(
            "w-4 h-4 transition-transform duration-200",
            voted === "down" && isAnimating && "animate-bounce-once",
          )}
        />
      </Button>
    </div>
  )
}

