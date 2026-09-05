import type {
  Favorite,
  FavoritesResponse,
  Movie,
  MovieDetails,
  PopularResponse,
  SearchResponse,
} from "@/types/movie";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body?.error) message = body.error;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

function withSession(sessionId: string): RequestInit {
  return { headers: { "X-Session-ID": sessionId } };
}

export async function getPopularMovies(page = 1): Promise<Movie[]> {
  const data = await request<PopularResponse>(`/api/movies/popular?page=${page}`);
  return data.results;
}

export async function searchMovies(query: string): Promise<Movie[]> {
  const data = await request<SearchResponse>(
    `/api/movies/search?q=${encodeURIComponent(query)}`
  );
  return data.results;
}

export async function getMovieDetails(movieId: number | string): Promise<MovieDetails> {
  return request<MovieDetails>(`/api/movies/${movieId}`);
}

export async function getFavorites(sessionId: string): Promise<Favorite[]> {
  const data = await request<FavoritesResponse>(
    "/api/favorites",
    withSession(sessionId)
  );
  return data.results;
}

export async function addFavorite(
  sessionId: string,
  movieId: number
): Promise<Favorite> {
  return request<Favorite>(
    `/api/favorites/${movieId}`,
    { method: "POST", ...withSession(sessionId) }
  );
}

export async function removeFavorite(
  sessionId: string,
  movieId: number
): Promise<void> {
  await request<unknown>(
    `/api/favorites/${movieId}`,
    { method: "DELETE", ...withSession(sessionId) }
  );
}