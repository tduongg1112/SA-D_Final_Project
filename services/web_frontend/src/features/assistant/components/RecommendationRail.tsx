import { Link } from "react-router-dom";
import { AlertCircle, Bot, Sparkles } from "lucide-react";

import { PanelCard } from "@/components/ui/panel-card";
import { SkeletonBlock } from "@/components/ui/skeleton-block";
import { StatusBadge } from "@/components/ui/status-badge";
import type { AIRecommendationResponse } from "@/lib/api/types";
import { formatCurrency, formatTitleCase } from "@/lib/utils/format";

interface RecommendationRailProps {
  eyebrow: string;
  title: string;
  description: string;
  data?: AIRecommendationResponse;
  isLoading?: boolean;
  errorMessage?: string | null;
  emptyTitle: string;
  emptyDescription: string;
}

export function RecommendationRail({
  eyebrow,
  title,
  description,
  data,
  isLoading = false,
  errorMessage,
  emptyTitle,
  emptyDescription,
}: RecommendationRailProps) {
  if (isLoading) {
    return (
      <PanelCard eyebrow={eyebrow} title={title} description={description} icon={<Sparkles size={18} strokeWidth={1.7} />}>
        <div className="grid gap-3">
          <SkeletonBlock className="h-20 rounded-[20px]" />
          <SkeletonBlock className="h-24 rounded-[20px]" />
          <SkeletonBlock className="h-24 rounded-[20px]" />
        </div>
      </PanelCard>
    );
  }

  if (errorMessage) {
    return (
      <PanelCard eyebrow={eyebrow} title="AI service is unavailable." description={errorMessage} icon={<AlertCircle size={18} strokeWidth={1.7} />}>
        <div className="rounded-[20px] border border-[#f1d0d0] bg-[#fbe8e8] px-4 py-3 text-[14px] leading-6 text-[#8b4545]">
          The commerce flow still works, but recommendation responses are currently unavailable.
        </div>
      </PanelCard>
    );
  }

  if (!data) {
    return (
      <PanelCard eyebrow={eyebrow} title={emptyTitle} description={emptyDescription} icon={<Bot size={18} strokeWidth={1.7} />}>
        <div className="rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[15px] leading-7 text-[var(--color-text-soft)]">
          The panel is connected and ready, but it needs live shopper context before it can rank products.
        </div>
      </PanelCard>
    );
  }

  return (
    <PanelCard eyebrow={eyebrow} title={title} description={description} icon={<Sparkles size={18} strokeWidth={1.7} />}>
      <div className="grid gap-4">
        <div className="grid gap-3 rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge tone="primary">{formatTitleCase(data.predicted_intent.label)}</StatusBadge>
            {data.matched_category ? <StatusBadge tone="neutral">{formatTitleCase(data.matched_category)}</StatusBadge> : null}
            <StatusBadge tone="success">{Math.round(data.predicted_intent.confidence * 100)}% confidence</StatusBadge>
            <StatusBadge tone={data.retrieval_context.backend === "neo4j" ? "warning" : "neutral"}>
              {data.retrieval_context.backend === "neo4j" ? "Graph-RAG active" : "Graph fallback"}
            </StatusBadge>
          </div>
          <p className="text-[15px] leading-7 text-[var(--color-text-soft)]">{data.answer}</p>
          <p className="text-[14px] leading-6 text-[var(--color-text-faint)]">{data.predicted_intent.explanation}</p>
          {data.supporting_keywords.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {data.supporting_keywords.map((keyword) => (
                <StatusBadge key={keyword} tone="neutral">
                  {keyword}
                </StatusBadge>
              ))}
            </div>
          ) : null}
          {data.retrieval_context.evidence.length > 0 ? (
            <div className="grid gap-2 rounded-[18px] border border-[var(--color-border)] bg-white px-4 py-3">
              <span className="label-eyebrow">Retrieval evidence</span>
              {data.retrieval_context.evidence.map((item) => (
                <p key={item} className="text-[14px] leading-6 text-[var(--color-text-soft)]">
                  {item}
                </p>
              ))}
            </div>
          ) : null}
          {data.retrieval_context.related_categories.length > 0 || data.retrieval_context.observed_intents.length > 0 ? (
            <div className="grid gap-2">
              {data.retrieval_context.related_categories.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {data.retrieval_context.related_categories.map((category) => (
                    <StatusBadge key={category} tone="neutral">
                      Related: {formatTitleCase(category)}
                    </StatusBadge>
                  ))}
                </div>
              ) : null}
              {data.retrieval_context.observed_intents.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {data.retrieval_context.observed_intents.map((intent) => (
                    <StatusBadge key={intent} tone="success">
                      Seen: {formatTitleCase(intent)}
                    </StatusBadge>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {data.retrieval_context.retrieved_product_names.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {data.retrieval_context.retrieved_product_names.map((name) => (
                <StatusBadge key={name} tone="warning">
                  Retrieved: {name}
                </StatusBadge>
              ))}
            </div>
          ) : null}
        </div>

        <div className="grid gap-3">
          {data.recommended_products.map((product) => (
            <article
              key={product.slug}
              className="grid gap-3 rounded-[22px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="grid gap-1">
                  <span className="label-eyebrow">{product.category_name}</span>
                  <strong className="text-[18px] font-semibold tracking-[-0.03em] text-[var(--color-text)]">{product.name}</strong>
                </div>
                <div className="grid gap-1 text-right">
                  <strong className="text-[18px] font-semibold tracking-[-0.03em] text-[var(--color-text)]">{formatCurrency(product.price)}</strong>
                  {product.featured ? <StatusBadge tone="primary">Featured</StatusBadge> : null}
                </div>
              </div>
              <p className="text-[14px] leading-6 text-[var(--color-text-soft)]">{product.short_description}</p>
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone="neutral">{product.brand}</StatusBadge>
                <StatusBadge tone="warning">{product.reason}</StatusBadge>
                <StatusBadge tone="success">Score {product.score.toFixed(1)}</StatusBadge>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-[13px] text-[var(--color-text-faint)]">AI-ranked product detail</span>
                <Link
                  to={product.absolute_url}
                  className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--color-border-strong)] bg-white px-4 text-[14px] font-medium text-[var(--color-text)] transition hover:bg-[var(--color-surface)]"
                >
                  Open product
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </PanelCard>
  );
}
