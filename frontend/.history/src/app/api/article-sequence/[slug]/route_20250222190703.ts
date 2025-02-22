import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";
import mongoose from "mongoose";

export async function GET(
  req: Request,
  context: { params: { id: string } }
) {
  try {
    await connectToDatabase();
    
    const db = mongoose.connection.db;
    if (!db) {
      throw new Error('Database connection not established');
    }
    
    const { id } = context.params;
    console.log('Looking for adjacent articles for id:', id);

    // Find current article
    const currentArticle = await (Article.findById(id) as any).lean().exec();
    if (!currentArticle) {
      return NextResponse.json(
        { error: "Article not found" },
        { status: 404 }
      );
    }

    // Find previous and next articles based on createdAt timestamp
    const [prevArticle, nextArticle] = await Promise.all([
      // Previous article (created before current)
      Article.findOne({
        createdAt: { $lt: currentArticle.createdAt }
      })
      .sort({ createdAt: -1 })
      .select('title slug')
      .lean()
      .exec(),

      // Next article (created after current)
      Article.findOne({
        createdAt: { $gt: currentArticle.createdAt }
      })
      .sort({ createdAt: 1 })
      .select('title slug')
      .lean()
      .exec()
    ]);

    console.log('Found adjacent articles:', {
      prev: prevArticle ? prevArticle.title : null,
      next: nextArticle ? nextArticle.title : null
    });

    return NextResponse.json({
      prev: prevArticle ? {
        title: prevArticle.title,
        slug: prevArticle.slug
      } : null,
      next: nextArticle ? {
        title: nextArticle.title,
        slug: nextArticle.slug
      } : null
    });

  } catch (error) {
    console.error("Error in GET /api/article-sequence/[id]:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 