import { forwardRef, type ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--color-accent)] text-white border-[var(--color-accent)] shadow-[0_14px_32px_rgba(47,109,246,0.22)] hover:bg-[var(--color-accent-strong)] hover:border-[var(--color-accent-strong)]",
  secondary:
    "bg-white text-[var(--color-text)] border-[var(--color-border-strong)] hover:bg-[var(--color-surface-muted)]",
  ghost:
    "bg-transparent text-[var(--color-text-faint)] border-transparent hover:bg-[var(--color-surface)] hover:text-[var(--color-text)]",
};

const sizeClasses: Record<ButtonSize, string> = {
  md: "h-11 px-4 text-[15px]",
  lg: "h-12 px-5 text-[15px]",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "secondary", size = "md", type = "button", ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex items-center justify-center rounded-2xl border font-medium transition duration-150 ease-out whitespace-nowrap",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]/30",
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      {...props}
    />
  );
});
