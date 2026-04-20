import { cn } from "@/lib/utils/cn";

interface SkeletonBlockProps {
  className?: string;
}

export function SkeletonBlock({ className }: SkeletonBlockProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-[20px] bg-[linear-gradient(135deg,rgba(47,109,246,0.08)_0%,rgba(236,235,231,0.8)_100%)]",
        className,
      )}
    />
  );
}
