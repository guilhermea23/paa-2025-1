
import { NextResponse } from "next/server";

export async function POST(_request: Request) {
  
  // comentado para não dar erro na compilação
  // const { prompt } = await request.json() as { prompt : string };
  
  // Mock de retorno com 10 filmes, 3 estrelas e nome Tom Hanks
  const movies = Array.from({ length: 10 }, (_, i) => ({
    id: i,
    name: "Tom Hanks",
    stars: 3,
  }));
  return NextResponse.json(movies);
}
