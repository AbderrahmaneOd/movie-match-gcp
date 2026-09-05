"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Header } from "@/components/Header";
import { getFavorites, removeFavorite } from "@/lib/api";
import { ensureSessionId } from "@/lib/session";
import type { Favorite } from "@/types/movie";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      const sessionId = ensureSessionId();
      try {
        if (!sessionId) return;
        const results = await getFavorites(sessionId);
        if (!cancelled) setFavorites(results);
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

    void run();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleRemove = useCallback(
    async (movieId: number) => {
      const sessionId = ensureSessionId();
      if (!sessionId) return;
      try {
        await removeFavorite(sessionId, movieId);
        setFavorites((current) =>
          current.filter((favorite) => favorite.movie_id !== movieId)
        );
      } catch {
        // ignore removal failures
      }
    },
    []
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black/80 text-zinc-50">
      <Header />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <section className="mb-8">
          <h1 className="text-2xl font-bold">Your Favorites</h1>
          <p className="mt-2 text-sm text-zinc-400">
            Movies you added from their detail page.
          </p>
        </section>

        {loading ? (
          <p className="text-sm text-zinc-400">Loading...</p>
        ) : error ? (
          <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-200">
            {error}
          </div>
        ) : favorites.length === 0 ? (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-8 text-center">
            <p className="text-sm text-zinc-400">
              No favorites yet. Open a movie and click &ldquo;Add to
              Favorites&rdquo;.
            </p>
            <Link
              href="/"
              className="mt-4 inline-block text-sm font-medium text-zinc-100 underline underline-offset-4"
            >
              Browse popular movies
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-6 sm:grid-cols-3 md:grid-cols-4">
            {favorites.map((favorite) => (
              <div
                key={favorite.movie_id}
                className="overflow-hidden rounded-lg bg-white/[0.03]"
              >
                <Link href={`/movie/${favorite.movie_id}`} className="block">
                  <div className="relative aspect-[2/3] w-full overflow-hidden bg-zinc-800">
                    {favorite.poster_url ? (
                      <Image
                        src={favorite.poster_url}
                        alt={favorite.title}
                        fill
                        sizes="(max-width: 768px) 50vw, 25vw"
                        className="object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center bg-zinc-900 p-4 text-center text-sm text-zinc-500">
                        {favorite.title}
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <h2 className="line-clamp-1 text-sm font-semibold text-zinc-100">
                      {favorite.title}
                    </h2>
                    <div className="mt-1 text-xs text-zinc-400">
                      {favorite.year ?? favorite.release_date ?? "—"}
                    </div>
                  </div>
                </Link>
                <div className="px-3 pb-3">
                  <button
                    onClick={() => handleRemove(favorite.movie_id)}
                    className="w-full rounded-full border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:border-red-700 hover:text-red-300"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}