import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";

export function Header() {
  return (
    <header className="sticky top-0 z-20 border-b border-white/5 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="text-xl font-extrabold tracking-tight text-zinc-50">
          MovieMatch
        </Link>
        <div className="flex items-center gap-6">
          <nav className="hidden items-center gap-6 text-sm text-zinc-300 sm:flex">
            <Link href="/" className="hover:text-zinc-50">
              Popular
            </Link>
            <Link href="/favorites" className="hover:text-zinc-50">
              Favorites
            </Link>
          </nav>
          <div className="w-56 md:w-72">
            <SearchBar />
          </div>
        </div>
      </div>
    </header>
  );
}