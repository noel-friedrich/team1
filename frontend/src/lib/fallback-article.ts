export const fallbackArticle = {
  id: "fallback",
  title: "Article Not Found",
  content: `# Article Not Found

This article could not be loaded at the moment. This could be because:

- The article doesn't exist
- There was a temporary server error
- The database connection failed

Please try:
- Checking the URL is correct
- Refreshing the page
- Coming back later

You can also:
- [Go to the homepage](/)
- [View recent changes](/history)
- [Search for another article](/search)`,
  slug: "article-not-found",
  image_url: "/placeholder.svg",
  createdAt: new Date().toISOString(),
  votes: 0
}; 