import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";

export async function GET() {
  try {
    await connectToDatabase();
    
    // Find the most recent article
    // @ts-expect-error making it work 
    const latestArticle = await Article.findOne()
      .sort({ createdAt: -1 })
      .lean()
      .exec();

    if (!latestArticle) {
      return NextResponse.json(
        { error: "No articles found" },
        { status: 404 }
      );
    }

    return NextResponse.json(latestArticle);

  } catch (error) {
    console.error("Error in GET /api/article-of-the-day:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
