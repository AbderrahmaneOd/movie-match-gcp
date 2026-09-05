import Image from "next/image";
import Link from "next/link";
import type { Movie } from "@/types/movie";

export function MovieCard({ movie }: { movie: Movie }) {
  return (
    <Link
      href={`/movie/${movie.id}`}
      className="group overflow-hidden rounded-lg bg-white/[0.03] transition-transform hover:scale-[1.02]"
    >
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-zinc-800">
        {movie.posterUrl ? (
          <Image
            src={movie.posterUrl}
            alt={movie.title}
            fill
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-zinc-900 p-4 text-center text-sm text-zinc-500">
            {movie.title}
          </div>
        )}
        {typeof movie.voteAverage === "number" && movie.voteAverage > 0 && (
          <div className="absolute right-2 top-2 rounded-md bg-black/70 px-2 py-1 text-xs font-medium text-zinc-100">
            {movie.voteAverage.toFixed(1)}
          </div>
        )}
      </div>
      <div className="p-3">
        <h3 className="line-clamp-1 text-sm font-semibold text-zinc-100">
          {movie.title}
        </h3>
        <div className="mt-1 text-xs text-zinc-400">
          {movie.year ?? movie.releaseDate ?? "—"}
        </div>
      </div>
    </Link>
  );
}