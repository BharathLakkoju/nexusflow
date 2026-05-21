import * as React from "react";
import { cn } from "@/lib/utils";

function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success";
}) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        {
          default: "border-transparent bg-primary text-primary-foreground",
          secondary:
            "border-transparent bg-secondary text-secondary-foreground",
          destructive:
            "border-transparent bg-destructive text-destructive-foreground",
          outline: "text-foreground",
          success:
            "border-transparent bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        }[variant],
        className,
      )}
      {...props}
    />
  );
}

export { Badge };
