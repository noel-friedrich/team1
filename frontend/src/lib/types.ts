export type Article = {
    id: string
    slug: string
    title: string
    content: string
    image: {
      url: string
      caption: string
    }
    createdAt: string
    votes: {
      up: number
      down: number
    }
  }
  
  export type ChangelogEntry = {
    id: string
    articleId: string
    articleTitle: string
    createdAt: string
    type: "new" | "update"
  }
  
  