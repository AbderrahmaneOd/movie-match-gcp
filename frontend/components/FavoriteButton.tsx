"use client";

import { useCallback, useEffect, useState } from "react";
import { addFavorite, getFavorites, removeFavorite } from "@/lib/api";
import { ensureSessionId } from "@/lib/session";

export function FavoriteButton({ movieId }: { movieId: number }) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const sessionId = ensureSessionId();
    if (!sessionId) return;

    getFavorites(sessionId)
      .then((favorites) => {
        if (!cancelled) {
          setIsFavorite(favorites.some((f) => f.movie_id === movieId));
        }
      })
      .catch(() => {
        // favorites are best-effort; ignore errors here
      });

    return () => {
      cancelled = true;
    };
  }, [movieId]);

  const toggle = useCallback(async () => {
    if (busy) return;
    const sessionId = ensureSessionId();
    if (!sessionId) return;

    setBusy(true);
    try {
      if (isFavorite) {
        await removeFavorite(sessionId, movieId);
        setIsFavorite(false);
      } else {
        await addFavorite(sessionId, movieId);
        setIsFavorite(true);
      }
    } catch {
      // keep previous state on failure
    } finally {
      setBusy(false);
    }
  }, [busy, isFavorite, movieId]);

  return (
    <button
      onClick={toggle}
      disabled={busy}
      aria-pressed={isFavorite}
      className={`w-full rounded-full px-4 py-2 text-sm font-medium transition-colors ${
        isFavorite
          ? "bg-yellow-400 text-black hover:bg-yellow-300"
          : "border border-zinc-700 text-zinc-100 hover:border-zinc-500"
      }`}
    >
      {isFavorite ? "In Favorites" : "Add to Favorites"}
    </button>
  );
}