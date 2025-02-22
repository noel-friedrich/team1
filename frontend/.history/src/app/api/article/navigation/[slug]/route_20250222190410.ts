import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";
import mongoose from "mongoose";

export async function GET(
  req: Request,
  context: { params: { slug: string } }
) {
  try {
    await connectToDatabase();
    
    const { slug } = context.params;
    
    // First, get the current article to find its timestamp
    const currentArticle = await Article.findOne({ slug }).lean().exec();
    
    if (!currentArticle) {
      return NextResponse.json(
        { error: "Article not found" },
        { status: 404 }
      );
    }

    // Find the previous and next articles based on createdAt timestamp
    const [previousArticle, nextArticle] = await Promise.all([
      Article.findOne({
        createdAt: { $lt: currentArticle.createdAt }
      })
      .sort({ createdAt: -1 })
      .select('slug title')
      .lean()
      .exec(),
      
      Article.findOne({
        createdAt: { $gt: currentArticle.createdAt }
      })
      .sort({ createdAt: 1 })
      .select('slug title')
      .lean()
      .exec()
    ]);

    return NextResponse.json({
      previous: previousArticle ? {
        slug: previousArticle.slug,
        title: previousArticle.title
      } : null,
      next: nextArticle ? {
        slug: nextArticle.slug,
        title: nextArticle.title
      } : null
    });

  } catch (error) {
    console.error("Error in GET /api/article/navigation/[slug]:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 