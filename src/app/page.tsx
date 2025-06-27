"use client";
import { useState } from "react";
import { Textarea } from "./_components/ui/textarea";
import { Button } from "./_components/ui/button";
import { Search, Star } from "lucide-react";

interface Movie {
  id: number;
  name: string;
  stars: number;
}

export default function Home() {
  const [prompt, setPrompt] = useState<string>("");
  const [movies, setMovies] = useState<Movie[]>([]);

  const handleClick = async () => {
    const res = await fetch("/api/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data: Movie[] = await res.json() as Movie[];
    setMovies(data);
  };

  return (
    <main className="min-h-screen bg-[#0d1117] flex flex-col items-center px-4 py-8">
      <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-orange-500 to-slate-400 text-transparent bg-clip-text mb-4 text-center">
        Recomendações de Filmes
      </h1>
      <p className="text-slate-300 text-center max-w-xl mb-8">
        Descubra os melhores filmes com nossa inteligência artificial. Faça perguntas em linguagem natural e encontre o filme perfeito para você.
      </p>

      <div className="w-full max-w-2xl bg-[#161b22] p-6 rounded-xl shadow-xl">
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full h-24 resize-none text-slate-100 bg-[#0d1117] border border-slate-600"
          placeholder="Ex: Quero um filme de ação dos anos 90, Me recomende uma comédia romântica, Filmes com Tom Hanks"
        />

        <Button 
          onClick={handleClick}
          className="mt-4 w-full bg-gradient-to-r from-red-600 to-blue-600 text-white flex items-center justify-center gap-2"
        >
          <Search className="w-4 h-4" />
          Encontrar Filme
        </Button>
      </div>

      {movies.length > 0 && (
        <div className="mt-8 w-full max-w-6xl">
          <h2 className="text-xl text-slate-100 mb-4">Filmes em Destaque</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {movies.map((movie) => (
              <div key={movie.id} className="bg-[#161b22] p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  {Array(movie.stars)
                    .fill(0)
                    .map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400" />
                    ))}
                </div>
                <h3 className="text-slate-100 font-semibold">{movie.name}</h3>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}