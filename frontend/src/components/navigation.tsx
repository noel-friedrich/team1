import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Menu } from "lucide-react"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

export function Navigation() {
  return (
    <>
      {/* Mobile Navigation */}
      <div className="border-b p-4 lg:hidden">
        <div className="flex items-center gap-4">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[300px] p-0">
              <NavigationContent />
            </SheetContent>
          </Sheet>
          <Link href="/" className="font-semibold">
            Williampedia
          </Link>
        </div>
      </div>

      {/* Desktop Navigation */}
      <div className="hidden border-r lg:block lg:w-[300px] lg:shrink-0">
        <NavigationContent />
      </div>
    </>
  )
}

function NavigationContent() {
  return (
    <div className="flex h-full flex-col gap-4 p-4">
      <Link href="/" className="text-xl font-semibold">
        Williampedia
      </Link>
      <div className="relative">
        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search" className="pl-8" />
      </div>
      <nav className="grid gap-2">
        <Button asChild variant="ghost" className="justify-start">
          <Link href="/">Main Page</Link>
        </Button>
        <Button asChild variant="ghost" className="justify-start">
          <Link href="/wiki/random">Random Article</Link>
        </Button>
        <Button asChild variant="ghost" className="justify-start">
          <Link href="/live">Live Changes</Link>
        </Button>
      </nav>
    </div>
  )
}

