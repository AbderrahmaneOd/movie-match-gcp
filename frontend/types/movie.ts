// Interface matching the raw backend response
export interface RawMovie {
  id: number;
  title: string;
  overview: string;
  poster_url: string;
  backdrop_url: string;
  release_date: string;
  vote_average: number;
  vote_count: number;
  year: number;
}

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

export interface RawMovieDetails extends RawMovie {
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
  results: RawMovie[];
  page: number;
}

export interface SearchResponse {
  results: RawMovie[];
  query: string;
}

export interface FavoritesResponse {
  results: Favorite[];
}