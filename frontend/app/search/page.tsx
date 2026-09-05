"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Header } from "@/components/Header";
import { MovieGrid } from "@/components/MovieGrid";
import { searchMovies } from "@/lib/api";
import type { Movie } from "@/types/movie";

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") ?? "";

  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      if (!query.trim()) {
        setMovies([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const results = await searchMovies(query);
        if (!cancelled) setMovies(results);
      } catch (caught) {
        if (!cancelled) {
          setError(
            caught instanceof Error ? caught.message : "Something went wrong"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [query]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black/80 text-zinc-50">
      <Header />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <section className="mb-8">
          <h1 className="text-2xl font-bold">Search results</h1>
          {query && (
            <p className="mt-2 text-sm text-zinc-400">
              Results for &ldquo;{query}&rdquo;
            </p>
          )}
        </section>

        {!query.trim() ? (
          <p className="text-sm text-zinc-500">
            Type a movie title in the search bar to find it.
          </p>
        ) : loading ? (
          <p className="text-sm text-zinc-400">Searching...</p>
        ) : error ? (
          <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-200">
            {error}
          </div>
        ) : (
          <MovieGrid movies={movies} />
        )}
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={null}>
      <SearchContent />
    </Suspense>
  );
}