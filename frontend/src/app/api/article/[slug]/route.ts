import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/models/Article";
import mongoose from "mongoose";

export async function GET(
  req: Request,
  context: { params: { slug: string } }
) {
  try {
    const { slug } = context.params;

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
    const article = await Article.findOne({ slug }).lean();
    console.log('Query result:', article);

    if (!article) {
      console.log('No article found with slug:', slug);
      return NextResponse.json(
        { error: "Article not found" },
        { status: 404 }
      );
    }

    // Log success
    console.log('Successfully found article:', article.title);
    return NextResponse.json(article);

  } catch (error) {
    console.error("Error in GET /api/article/[slug]:", error);
    return NextResponse.json(
      { error: "Internal Server Error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
