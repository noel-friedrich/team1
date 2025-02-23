import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "10");
    
    await connectToDatabase();
    
    // Calculate skip value for pagination
    const skip = (page - 1) * limit;
    
    // Get total count of articles
    const totalArticles = await Article.countDocuments();
    
    // Fetch paginated articles sorted by createdAt
    // @ts-expect-error making it work
    const articles = await Article.find({})
      .sort({ createdAt: -1 }) // Sort by newest first
      .skip(skip)
      .limit(limit)
      .select('title slug createdAt') // Only select needed fields
      .lean()
      .exec();
    
    return NextResponse.json({
      articles,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalArticles / limit),
        totalArticles,
        hasNextPage: skip + limit < totalArticles,
        hasPreviousPage: page > 1
      }
    });

  } catch (error) {
    console.error("Error in GET /api/history:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 