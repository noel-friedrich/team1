import Link from "next/link";
import SearchBox from "@/components/SearchBox";
import RandomArticleLink from "@/components/random-article-link";
import { Pagination } from "@/components/ui/pagination";

// Add this interface near the top of the file, after the imports
interface Article {
  slug: string;
  title: string;
  createdAt: string;
}

async function getHistory(page: number = 1) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/history?page=${page}&limit=10`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export default async function HistoryPage({
  searchParams,
}: {
  searchParams?: { [key: string]: string | string[] | undefined }
}) {
  const page = parseInt(searchParams?.page?.toString() || "1");
  const { articles, pagination } = await getHistory(page);

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar with logo and navigation */}
      <aside className="w-[14rem] p-4 border-r min-h-screen text-[0.875rem] hidden lg:block">
        <div className="mb-6 flex items-center gap-2">
          <Link href="/" className="hover:opacity-80">
            <span className="font-serif text-xl">Williampedia</span>
          </Link>
        </div>
        <nav className="space-y-6">
          <div>
            <div className="font-medium mb-2 text-[#54595d]">Navigation</div>
            <ul className="space-y-1">
              <li>
                <Link
                  href="/"
                  className="text-[#36c] hover:text-[#447ff5] block py-1"
                >
                  Main page
                </Link>
              </li>
              <li>
                <Link
                  href="/history"
                  className="text-[#36c] hover:text-[#447ff5] block py-1"
                >
                  Recent changes
                </Link>
              </li>
              <li>
                <RandomArticleLink />
              </li>
              <li>
                <Link
                  href="/about"
                  className="text-[#36c] hover:text-[#447ff5] block py-1"
                >
                  About
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar: Search */}
        <nav className="border-b">
          <div className="max-w-[960px] mx-auto px-4 flex justify-center items-center h-14">
            <SearchBox />
          </div>
        </nav>

        {/* History Content */}
        <main className="flex-1 flex justify-center">
          <div className="w-full max-w-2xl px-4 py-8">
            <h1 className="text-2xl font-serif mb-6 text-center">
              Article History
            </h1>

            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-16 top-0 bottom-0 w-px bg-gray-200" />

              {/* Timeline entries */}
              <div className="space-y-8">
                {articles.map((article: Article) => (
                  <div
                    key={article.slug}
                    className="relative flex items-start gap-8 group"
                  >
                    {/* Timeline dot */}
                    <div className="absolute left-16 w-3 h-3 -translate-x-[6px] translate-y-1.5">
                      <div className="w-full h-full rounded-full border-2 border-primary bg-white group-hover:bg-primary transition-colors" />
                    </div>

                    {/* Date */}
                    <div className="w-16 pt-1 text-sm text-muted-foreground font-medium">
                      {new Date(article.createdAt).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                      })}
                    </div>

                    {/* Content */}
                    <div className="flex-1 bg-card hover:bg-accent/50 rounded-lg p-4 transition-colors">
                      <Link
                        href={`/article/${article.slug}`}
                        className="text-[#36c] hover:text-[#447ff5] font-serif text-lg hover:underline"
                      >
                        {article.title}
                      </Link>
                      <div className="text-sm text-muted-foreground mt-1">
                        Created on {formatDate(article.createdAt)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pagination */}
            {pagination.totalPages > 1 && (
              <div className="mt-8 flex justify-center">
                <Pagination
                  currentPage={pagination.currentPage}
                  totalPages={pagination.totalPages}
                  hasNextPage={pagination.hasNextPage}
                  hasPreviousPage={pagination.hasPreviousPage}
                />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
