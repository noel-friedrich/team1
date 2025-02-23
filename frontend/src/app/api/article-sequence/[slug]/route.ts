import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";
import mongoose from "mongoose";

export async function GET(
  req: Request,
  { params }: { params: { slug: string } }
) {
  try {
    await connectToDatabase();
    
    const db = mongoose.connection.db;
    if (!db) {
      throw new Error('Database connection not established');
    }
    
    // Log current database connection info
    console.log('Connected to database:', db.databaseName);
    
    const { slug } = params;
    console.log('Looking for article with slug:', slug);

    // List all collections in the database
    const collections = await db.collections();
    console.log('Available collections:', collections.map(c => c.collectionName));

    // Find the article
    const article = await Article.findOne({ slug }).lean();
    console.log('Query result:', article);

    if (!article) {
      console.log('No article found with slug:', slug);
      return NextResponse.json(
        { error: "Article not found" },
        { status: 404 }
      );
    }

    // Find the previous and next articles based on createdAt timestamp
    const [previousArticle, nextArticle] = await Promise.all([
      Article.findOne({
        createdAt: { $lt: article.createdAt }
      })
      .sort({ createdAt: -1 })
      .select('slug title createdAt')
      .lean()
      .exec(),
      
      Article.findOne({
        createdAt: { $gt: article.createdAt }
      })
      .sort({ createdAt: 1 })
      .select('slug title createdAt')
      .lean()
      .exec()
    ]);

    return NextResponse.json({
      current: {
        slug: article.slug,
        title: article.title,
        createdAt: article.createdAt
      },
      previous: previousArticle ? {
        slug: previousArticle.slug,
        title: previousArticle.title,
        createdAt: previousArticle.createdAt
      } : null,
      next: nextArticle ? {
        slug: nextArticle.slug,
        title: nextArticle.title,
        createdAt: nextArticle.createdAt
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