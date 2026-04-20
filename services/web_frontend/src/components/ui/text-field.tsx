import { forwardRef, type InputHTMLAttributes, type ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  icon?: ReactNode;
  wrapperClassName?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(function TextField(
  { className, wrapperClassName, icon, ...props },
  ref,
) {
  return (
    <label
      className={cn(
        "flex h-14 items-center gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 text-[var(--color-text-faint)] transition focus-within:border-[var(--color-border-strong)] focus-within:bg-white",
        wrapperClassName,
      )}
    >
      {icon}
      <input
        ref={ref}
        className={cn(
          "w-full border-none bg-transparent text-[15px] text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-faint)]",
          className,
        )}
        {...props}
      />
    </label>
  );
});
