import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";

export async function GET() {
  try {
    await connectToDatabase();
    
    const articles = await Article.aggregate([
      { $sample: { size: 3 } }, // Get 3 random articles
      { 
        $project: {
          title: 1,
          slug: 1,
          content: 1,
          image_url: 1,
          _id: 0
        }
      }
    ]).exec();

    if (!articles || articles.length === 0) {
      return NextResponse.json(
        { error: "No articles found" },
        { status: 404 }
      );
    }

    // Format the articles to match the expected structure
    const formattedArticles = articles.map(article => ({
      id: article.slug, // Using slug as ID since we're not returning _id
      title: article.title,
      slug: article.slug,
      content: article.content,
      image: {
        url: article.image_url || "/placeholder.svg"
      }
    }));

    return NextResponse.json(formattedArticles);

  } catch (error) {
    console.error("Error in GET /api/featured-articles:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 