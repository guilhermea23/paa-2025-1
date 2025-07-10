
import { NextResponse } from "next/server";

interface Movie {
  id: string;
  nome: string;
  estrelas: number;
}

export async function POST(_request: Request) {
  try{
  
  const { prompt } = await _request.json() as { prompt : string };
  
  if (!prompt) {
    return NextResponse.json(
      { error: "O campo 'prompt' é obrigatório." },
      { status: 400 }
    );
  }

  const backendUrl = 'http://127.0.0.1:8000/recommendations';
    
  const backendResponse = await fetch(backendUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      
      prompt: prompt,
    }),
  });

  if (!backendResponse.ok) {
    // Se o backend retornou um erro, repasse a mensagem e o status.
    const errorData = await backendResponse.json();
    return NextResponse.json(
      { error: errorData.message || "Erro ao comunicar com o backend." },
      { status: backendResponse.status }
    );
  }
    
    // 5. Extrair os dados JSON da resposta do backend.
    const movies: Movie[] = await backendResponse.json();

    // 6. Retornar os dados do backend para o cliente final.
    return NextResponse.json(movies);

  } catch (error) {
    // Captura erros de rede, JSON inválido, etc.
    console.error("Erro na API Route:", error);
    return NextResponse.json(
      { error: "Ocorreu um erro interno no servidor." },
      { status: 500 }
    );
  }
  // Mock de retorno com 10 filmes, 3 estrelas e nome Tom Hanks
  // const movies = Array.from({ length: 10 }, (_, i) => ({
  //   id: i,
  //   name: "Tom Hanks",
  //   stars: 3,
  // }));
}  
