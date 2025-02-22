import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article, { IArticle } from "@/models/Article";
import mongoose from "mongoose";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  try {
    // Await the resolution of params
    const { slug } = await params;

    await connectToDatabase();

    const db = mongoose.connection.db;
    if (!db) {
      throw new Error('Database connection not established');
    }

    // Log current database connection info
    console.log('Connected to database:', db.databaseName);
    console.log('Looking for article with slug:', slug);

    // List all collections in the database
    const collections = await db.collections();
    console.log('Available collections:', collections.map(c => c.collectionName));

    // Find the article
    // @ts-expect-error making it work 
    const article = await Article.findOne<IArticle>({ slug }).exec();
    console.log("Query result:", article);

    if (!article) {
      console.log('No article found with slug:', slug);
      return NextResponse.json(
        { error: "Article not found" },
        { status: 404 }
      );
    }

    // Find the previous and next articles based on createdAt timestamp
    const [previousArticle, nextArticle] = await Promise.all([
      // @ts-expect-error making it work 
      Article.findOne(
        { createdAt: { $lt: article.createdAt } }
      )
      .sort({ createdAt: -1 })
      .select({ slug: 1, title: 1, createdAt: 1, _id: 0 })
      .lean()
      .exec(),

      // @ts-expect-error making it work 
      Article.findOne(
        { createdAt: { $gt: article.createdAt } }
      )
      .sort({ createdAt: 1 })
      .select({ slug: 1, title: 1, createdAt: 1, _id: 0 })
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
    console.error("Error in GET /api/article-sequence/[slug]:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
