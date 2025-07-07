import type { TextareaHTMLAttributes } from "react";
import { cn } from "~/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn("px-4 py-2 rounded-md border border-gray-300 text-sm", className)}
      {...props}
    />
  );
}