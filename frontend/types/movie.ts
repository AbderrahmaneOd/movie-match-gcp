export interface Movie {
  id: number;
  title: string;
  overview: string | null;
  posterUrl: string | null;
  backdropUrl: string | null;
  releaseDate: string | null;
  year: number | null;
  voteAverage: number | null;
  voteCount: number | null;
}

export interface MovieDetails extends Movie {
  runtime: number | null;
  genres: string[];
  status?: string | null;
  tagline?: string | null;
}

export interface Favorite {
  movie_id: number;
  title: string;
  poster_url: string | null;
  release_date: string | null;
  year: number | null;
  vote_average: number | null;
  created_at: string | null;
}

export interface PopularResponse {
  results: Movie[];
  page: number;
}

export interface SearchResponse {
  results: Movie[];
  query: string;
}

export interface FavoritesResponse {
  results: Favorite[];
}