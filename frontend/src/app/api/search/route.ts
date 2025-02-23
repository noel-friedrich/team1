import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import Article from "@/lib/models/Article";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get("q");

    if (!query) {
      return NextResponse.json({ articles: [] });
    }

    await connectToDatabase();

    // Create a case-insensitive regex pattern for fuzzy matching
    const searchRegex = new RegExp(
      query.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"),
      "i"
    );

    // @ts-expect-error got to get it to work
    const articles = await Article.find(
      { title: searchRegex },
      { title: 1, slug: 1, _id: 0 } // Only return title and slug
    ).limit(10);

    return NextResponse.json({ articles });
  } catch (error) {
    console.error("Search error:", error);
    return NextResponse.json(
      { error: "Failed to search articles" },
      { status: 500 }
    );
  }
}
