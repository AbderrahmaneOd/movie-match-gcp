import { Header } from "@/components/Header";
import { MovieGrid } from "@/components/MovieGrid";
import { getPopularMovies } from "@/lib/api";
import type { Movie } from "@/types/movie";

export const metadata = {
  title: "MovieMatch — Popular Movies",
  description: "Browse popular movies, search titles, and keep favorites.",
};

export default async function HomePage() {
  let movies: Movie[] = [];
  let error: string | null = null;

  try {
    movies = await getPopularMovies();
  } catch (caught) {
    error = caught instanceof Error ? caught.message : "Something went wrong";
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black/80 text-zinc-50">
      <Header />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <section className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight md:text-5xl">
            Popular Movies
          </h1>
          <p className="mt-3 max-w-2xl text-zinc-400">
            Discover what is trending right now. Search any title from the
            header to find more.
          </p>
        </section>

        {error ? (
          <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-200">
            <p className="font-semibold">Could not load movies</p>
            <p className="mt-1 text-red-300/80">{error}</p>
            <p className="mt-2 text-red-300/60">
              Make sure the backend is running on port 5000.
            </p>
          </div>
        ) : (
          <MovieGrid movies={movies} />
        )}
      </main>
    </div>
  );
}