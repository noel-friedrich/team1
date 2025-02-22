"use client"

import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"

type VoteButtonsProps = {
  articleId: string
  votes: {
    up: number
    down: number
  }
}

export default function VoteButtons({ articleId, votes: initialVotes }: VoteButtonsProps) {
  const [votes, setVotes] = useState(initialVotes)

  const handleVote = async (type: "up" | "down") => {
    // In a real app, this would make an API call
    setVotes((prev) => ({
      ...prev,
      [type]: prev[type] + 1,
    }))
  }

  return (
    <div className="flex items-center gap-4">
      <Button variant="ghost" size="sm" onClick={() => handleVote("up")} className="flex items-center gap-2">
        <ThumbsUp className="w-4 h-4" />
        <span>{votes.up}</span>
      </Button>
      <Button variant="ghost" size="sm" onClick={() => handleVote("down")} className="flex items-center gap-2">
        <ThumbsDown className="w-4 h-4" />
        <span>{votes.down}</span>
      </Button>
    </div>
  )
}

