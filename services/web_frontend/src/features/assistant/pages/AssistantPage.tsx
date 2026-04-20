import { Bot, SendHorizonal, ShoppingCart, Sparkles } from "lucide-react";
import { useState } from "react";

import { useAssistantChat } from "@/features/assistant/api/assistant";
import { RecommendationRail } from "@/features/assistant/components/RecommendationRail";
import { useCart } from "@/features/cart/api/cart";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { PanelCard } from "@/components/ui/panel-card";
import { StatusBadge } from "@/components/ui/status-badge";

interface ChatMessage {
  id: string;
  role: "assistant" | "user";
  body: string;
}

const starterPrompts = [
  "Suggest products for study and portable work",
  "Recommend add-ons for my cart",
  "Help me choose wellness essentials",
  "Find products for a calm home routine",
];

export function AssistantPage() {
  const { data: cart } = useCart();
  const chatMutation = useAssistantChat();
  const [draft, setDraft] = useState("");
  const [latestResponse, setLatestResponse] = useState<typeof chatMutation.data>(undefined);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "assistant-welcome",
      role: "assistant",
      body: "NovaMarket AI is ready. Ask for product suggestions, cart add-ons, or a category-specific shortlist.",
    },
  ]);

  const cartProductSlugs = cart?.items.map((item) => item.product_slug) ?? [];
  const cartCategoryNames = cart?.items.map((item) => item.category) ?? [];

  function submitMessage(message: string) {
    const trimmed = message.trim();
    if (!trimmed || chatMutation.isPending) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        body: trimmed,
      },
    ]);
    setDraft("");

    chatMutation.mutate(
      {
        message: trimmed,
        context: {
          cart_product_slugs: cartProductSlugs,
          cart_category_names: cartCategoryNames,
        },
      },
      {
        onSuccess: (response) => {
          setLatestResponse(response);
          setMessages((current) => [
            ...current,
            {
              id: `assistant-${Date.now()}`,
              role: "assistant",
              body: response.answer,
            },
          ]);
        },
      },
    );
  }

  const mutationError = chatMutation.error instanceof Error ? chatMutation.error.message : null;
  const promptSuggestions = latestResponse?.suggested_prompts ?? starterPrompts;

  return (
    <div className="grid gap-6">
      <PageHeader
        eyebrow="Shopping assistant"
        title="AI guidance is now live in the shell."
        description="This assistant keeps the conversation inside the NovaMarket experience, reads cart context, and returns ranked products from the AI service through the gateway."
        actions={
          <StatusBadge tone={cartProductSlugs.length > 0 ? "primary" : "neutral"}>
            {cartProductSlugs.length > 0 ? `${cartProductSlugs.length} cart products in context` : "No cart context"}
          </StatusBadge>
        }
      >
        <div className="flex flex-wrap gap-2">
          {promptSuggestions.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => submitMessage(prompt)}
              className="rounded-full"
              disabled={chatMutation.isPending}
            >
              <StatusBadge tone="neutral">{prompt}</StatusBadge>
            </button>
          ))}
        </div>
      </PageHeader>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.12fr)_380px]">
        <PanelCard
          eyebrow="Conversation"
          title="NovaMarket Assistant"
          description="The layout stays commerce-specific: conversation on the left, ranked products and session insights on the right."
          icon={<Bot size={18} strokeWidth={1.7} />}
        >
          <div className="grid gap-4">
            <div className="grid max-h-[520px] gap-3 overflow-y-auto pr-1">
              {messages.map((message) => {
                const isAssistant = message.role === "assistant";
                return (
                  <article
                    key={message.id}
                    className={[
                      "max-w-[88%] rounded-[24px] px-4 py-4 text-[15px] leading-7 shadow-[var(--shadow-card)]",
                      isAssistant
                        ? "border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)]"
                        : "ml-auto bg-[var(--color-accent)] text-white",
                    ].join(" ")}
                  >
                    <div className="mb-2 flex items-center gap-2">
                      <span className="label-eyebrow">{isAssistant ? "Assistant" : "You"}</span>
                    </div>
                    <p>{message.body}</p>
                  </article>
                );
              })}

              {chatMutation.isPending ? (
                <article className="max-w-[88%] rounded-[24px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-4 text-[15px] leading-7 text-[var(--color-text-soft)] shadow-[var(--shadow-card)]">
                  AI service is ranking products and preparing a response...
                </article>
              ) : null}
            </div>

            <form
              className="grid gap-3 rounded-[24px] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-4"
              onSubmit={(event) => {
                event.preventDefault();
                submitMessage(draft);
              }}
            >
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                rows={4}
                placeholder="Ask for product guidance, budget-oriented recommendations, or cart add-ons"
                className="min-h-[120px] resize-y rounded-[20px] border border-[var(--color-border)] bg-white px-4 py-4 text-[15px] text-[var(--color-text)] outline-none transition focus:border-[var(--color-border-strong)]"
              />
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge tone="primary">Gateway-backed</StatusBadge>
                  <StatusBadge tone="neutral">Cart-aware</StatusBadge>
                </div>
                <Button variant="primary" className="gap-2" type="submit" disabled={!draft.trim() || chatMutation.isPending}>
                  <SendHorizonal size={16} strokeWidth={1.7} />
                  {chatMutation.isPending ? "Thinking..." : "Send message"}
                </Button>
              </div>
              {mutationError ? (
                <div className="rounded-[18px] border border-[#f1d0d0] bg-[#fbe8e8] px-4 py-3 text-[14px] leading-6 text-[#8b4545]">
                  {mutationError}
                </div>
              ) : null}
            </form>
          </div>
        </PanelCard>

        <div className="grid gap-4">
          <RecommendationRail
            eyebrow="AI shortlist"
            title="Ranked products from the latest reply"
            description="Every assistant response can bring back intent prediction, graph-backed retrieval evidence, matching category, and a live product shortlist."
            data={latestResponse}
            isLoading={chatMutation.isPending}
            errorMessage={mutationError}
            emptyTitle="Start a conversation to get recommendations"
            emptyDescription="The rail will populate after the first question and stay aligned with the assistant response."
          />

          <PanelCard
            eyebrow="Session context"
            title="Assistant inputs"
            description="The chat service reads the current cart so it can recommend products with real checkout context."
            icon={<ShoppingCart size={18} strokeWidth={1.7} />}
          >
            <div className="grid gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone={cartProductSlugs.length > 0 ? "primary" : "neutral"}>
                  {cartProductSlugs.length > 0 ? `${cartProductSlugs.length} cart slugs` : "No cart products"}
                </StatusBadge>
                <StatusBadge tone={cartCategoryNames.length > 0 ? "success" : "neutral"}>
                  {cartCategoryNames.length > 0 ? `${cartCategoryNames.length} cart categories` : "No category context"}
                </StatusBadge>
                <StatusBadge tone="warning">Chat-native UI</StatusBadge>
              </div>
              <p className="text-[15px] leading-7 text-[var(--color-text-soft)]">
                This page is no longer a placeholder. It sends user prompts through the gateway to the AI service and keeps the interaction inside the NovaMarket interface instead of mimicking a generic chat layout.
              </p>
            </div>
          </PanelCard>

          <PanelCard
            eyebrow="Prompt starters"
            title="Fast ways to demo the flow"
            description="Use these to quickly demonstrate intent prediction, category matching, and recommendation output during the demo."
            icon={<Sparkles size={18} strokeWidth={1.7} />}
          >
            <div className="flex flex-wrap gap-2">
              {starterPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => submitMessage(prompt)}
                  className="rounded-full"
                  disabled={chatMutation.isPending}
                >
                  <StatusBadge tone="neutral">{prompt}</StatusBadge>
                </button>
              ))}
            </div>
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
