import { cn } from "~/lib/utils";
import { ButtonHTMLAttributes } from "react";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        // Fundo claro e hover um pouco mais escuro
        "px-4 py-2 rounded-xl text-sm font-medium transition-colors",
        "bg-gray-200 text-gray-900 hover:bg-gray-300",
        // mantém qualquer classe extra que você passar via props
        className
      )}
      {...props}
    />
  );
}