"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Header } from "@/components/Header";
import { FavoriteButton } from "@/components/FavoriteButton";
import { getMovieDetails } from "@/lib/api";
import type { MovieDetails } from "@/types/movie";

export default function MoviePage() {
  const params = useParams<{ id: string }>();
  const movieId = params.id;

  const [movie, setMovie] = useState<MovieDetails | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setError(null);
      setMovie(null);
      try {
        const details = await getMovieDetails(movieId);
        if (!cancelled) setMovie(details);
      } catch (caught) {
        if (!cancelled) {
          setError(
            caught instanceof Error ? caught.message : "Something went wrong"
          );
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [movieId]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black/80 text-zinc-50">
      <Header />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Link
          href="/"
          className="mb-6 inline-block text-sm text-zinc-400 hover:text-zinc-100"
        >
          ← Back to popular
        </Link>

        {error && (
          <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-200">
            <p className="font-semibold">Could not load this movie</p>
            <p className="mt-1 text-red-300/80">{error}</p>
          </div>
        )}

        {movie && (
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="md:col-span-1">
              <div className="relative aspect-[2/3] w-full overflow-hidden rounded-xl bg-zinc-800 shadow-2xl">
                {movie.posterUrl ? (
                  <Image
                    src={movie.posterUrl}
                    alt={movie.title}
                    fill
                    sizes="(max-width: 768px) 100vw, 33vw"
                    className="object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center p-6 text-center text-sm text-zinc-500">
                    No poster available
                  </div>
                )}
              </div>
              <div className="mt-4">
                <FavoriteButton movieId={movie.id} />
              </div>
            </div>

            <div className="md:col-span-2">
              <h1 className="text-3xl font-extrabold tracking-tight">
                {movie.title}
              </h1>
              {movie.tagline && (
                <p className="mt-1 text-sm italic text-zinc-400">
                  {movie.tagline}
                </p>
              )}

              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-zinc-400">
                {typeof movie.voteAverage === "number" &&
                  movie.voteAverage > 0 && (
                    <div className="font-semibold text-zinc-100">
                      {movie.voteAverage.toFixed(1)} / 10
                    </div>
                  )}
                {movie.year && <div>{movie.year}</div>}
                {movie.releaseDate && <div>Released {movie.releaseDate}</div>}
                {movie.runtime && movie.runtime > 0 && (
                  <div>{movie.runtime} min</div>
                )}
              </div>

              {movie.genres.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {movie.genres.map((genre) => (
                    <span
                      key={genre}
                      className="rounded-full bg-white/5 px-3 py-1 text-xs text-zinc-300"
                    >
                      {genre}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-6">
                <h2 className="text-lg font-semibold">Overview</h2>
                <p className="mt-2 text-sm leading-6 text-zinc-300">
                  {movie.overview || "No overview available."}
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}