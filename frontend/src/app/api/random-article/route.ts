import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";

export async function GET() {
  try {
    await connectToDatabase();
    
    // Get the count of all articles
    const count = await Article.countDocuments();
    
    // Generate a random index
    const random = Math.floor(Math.random() * count);
    
    // Skip to the random document
    // @ts-expect-error making it work 
    const article = await Article.findOne()
      .skip(random)
      .lean()
      .exec();

    if (!article) {
      return NextResponse.json(
        { error: "No articles found" },
        { status: 404 }
      );
    }

    return NextResponse.json(article);

  } catch (error) {
    console.error("Error in GET /api/random-article:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
