import type { InputHTMLAttributes } from "react";
import { cn } from "~/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn("px-4 py-2 rounded-md border border-gray-300 text-sm", className)}
      {...props}
    />
  );
}