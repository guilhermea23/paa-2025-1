"use client";
import { useState } from "react";
import { Search, Star, Calendar, Film, Sparkles, Play } from "lucide-react";

interface Movie {
  id: string;
  nome: string;
  sinopse: string;
  estrelas: number;
  generos: string[];
  data_lancamento: string; // ISO date string
}

export default function Home() {
  const [prompt, setPrompt] = useState<string>("");
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setMovies(data.filmes);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).getFullYear();
  };

  const renderStars = (rating: number) => {
    // Convert 0-10 rating to 0-5 stars for visual display
    const starRating = (rating / 10) * 5;
    const clampedRating = Math.min(Math.max(starRating, 0), 5);
    
    const fullStars = Math.floor(clampedRating);
    const hasHalfStar = (clampedRating % 1) >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <div className="flex items-center gap-1">
        {Array(fullStars).fill(0).map((_, i) => (
          <Star key={`full-${i}`} className="w-4 h-4 text-amber-400 fill-amber-400" />
        ))}
        {hasHalfStar && (
          <div className="relative">
            <Star className="w-4 h-4 text-amber-400" />
            <Star className="w-4 h-4 text-amber-400 fill-amber-400 absolute top-0 left-0" style={{ clipPath: 'inset(0 50% 0 0)' }} />
          </div>
        )}
        {Array(emptyStars).fill(0).map((_, i) => (
          <Star key={`empty-${i}`} className="w-4 h-4 text-slate-600" />
        ))}
        <span className="text-sm text-slate-400 ml-2">{rating.toFixed(1)}/10</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <main className="relative z-10 flex flex-col items-center px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl">
              <Film className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 text-transparent bg-clip-text">
              CineAI
            </h1>
          </div>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Descubra filmes incríveis com nossa IA avançada. Faça perguntas em linguagem natural e encontre a experiência cinematográfica perfeita para você.
          </p>
        </div>

        {/* Search Section */}
        <div className="w-full max-w-3xl mb-12">
          <div className="bg-white/10 backdrop-blur-lg p-8 rounded-3xl shadow-2xl border border-white/20">
            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full h-32 resize-none text-white bg-slate-800/50 border-2 border-slate-600/50 rounded-2xl p-6 placeholder-slate-400 focus:border-purple-400 focus:outline-none transition-all duration-300 text-lg"
                placeholder="✨ Ex: Quero um filme de ficção científica épico, Me recomende uma comédia romântica dos anos 2000, Filmes com Tom Hanks que me façam chorar..."
              />
              <div className="absolute bottom-4 right-4">
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
            </div>

            <button
              onClick={handleClick}
              disabled={isLoading || !prompt.trim()}
              className="mt-6 w-full bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 text-white py-4 px-8 rounded-2xl font-semibold text-lg flex items-center justify-center gap-3 transition-all duration-300 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed shadow-lg"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Buscando filmes...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Descobrir Filmes
                </>
              )}
            </button>
          </div>
        </div>

        {/* Movies Grid */}
        {movies.length > 0 && (
          <div className="w-full max-w-7xl">
            <div className="flex items-center gap-3 mb-8">
              <Play className="w-6 h-6 text-purple-400" />
              <h2 className="text-3xl font-bold text-white">Suas Recomendações</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-purple-400 to-transparent"></div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {movies.map((movie, index) => (
                <div
                  key={movie.id}
                  className="group bg-white/10 backdrop-blur-lg rounded-3xl overflow-hidden shadow-2xl border border-white/20 hover:border-purple-400/50 transition-all duration-500 hover:scale-105 hover:shadow-purple-500/20"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {/* Movie Poster Placeholder */}
                  <div className="h-48 bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600 relative overflow-hidden">
                    <div className="absolute inset-0 bg-black/20"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Film className="w-16 h-16 text-white/80" />
                    </div>
                    <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-full px-3 py-1">
                      <span className="text-white font-semibold text-sm">{formatDate(movie.data_lancamento)}</span>
                    </div>
                  </div>

                  {/* Movie Info */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors duration-300">
                      {movie.nome}
                    </h3>

                    {/* Rating */}
                    <div className="mb-4">
                      {renderStars(movie.estrelas)}
                    </div>

                    {/* Genres */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {movie.generos.slice(0, 3).map((genero, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-purple-500/30 text-purple-200 rounded-full text-sm font-medium border border-purple-400/30"
                        >
                          {genero}
                        </span>
                      ))}
                      {movie.generos.length > 3 && (
                        <span className="px-3 py-1 bg-slate-500/30 text-slate-300 rounded-full text-sm">
                          +{movie.generos.length - 3}
                        </span>
                      )}
                    </div>

                    {/* Synopsis */}
                    <p className="text-slate-300 text-sm leading-relaxed line-clamp-4">
                      {movie.sinopse}
                    </p>

                    {/* Release Date */}
                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/10">
                      <Calendar className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-400 text-sm">Lançamento: {formatDate(movie.data_lancamento)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {movies.length === 0 && !isLoading && (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Film className="w-12 h-12 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">Pronto para descobrir?</h3>
            <p className="text-slate-400 max-w-md mx-auto">
              Digite suas preferências acima e deixe nossa IA encontrar os filmes perfeitos para você!
            </p>
          </div>
        )}
      </main>
    </div>
  );
}