import type { Product } from "@/lib/api/types";

interface ProductMedia {
  imageUrl: string;
  imageAlt: string;
}

const PRODUCT_MEDIA_MAP: Record<string, ProductMedia> = {
  "novabook-flex-13": {
    imageUrl:
      "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Slim silver laptop on a clean desk",
  },
  "luma-desk-light": {
    imageUrl:
      "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Minimal desk lamp lighting a bright workspace",
  },
  "cloudrest-throw": {
    imageUrl:
      "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Soft neutral throw blanket folded on a sofa",
  },
  "aromanest-diffuser": {
    imageUrl:
      "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Ceramic aroma diffuser on a bright shelf",
  },
  "brewmate-press": {
    imageUrl:
      "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "French press with coffee on a kitchen counter",
  },
  "sliceboard-duo": {
    imageUrl:
      "https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Wood cutting boards in a clean kitchen",
  },
  "corebalance-mat": {
    imageUrl:
      "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Yoga mat laid out in a bright studio corner",
  },
  "puresip-bottle": {
    imageUrl:
      "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Insulated water bottle on a clean surface",
  },
  "transit-weekender": {
    imageUrl:
      "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Structured weekender bag ready for travel",
  },
  "linencarry-tote": {
    imageUrl:
      "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Soft everyday tote bag in natural fabric",
  },
  "glowmirror-mini": {
    imageUrl:
      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Portable mirror with soft beauty lighting",
  },
  "calmskin-set": {
    imageUrl:
      "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=1200&q=80",
    imageAlt: "Minimal skincare set arranged on a white surface",
  },
};

export function resolveProductMedia(product: Pick<Product, "slug" | "name">): ProductMedia {
  return (
    PRODUCT_MEDIA_MAP[product.slug] ?? {
      imageUrl:
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=80",
      imageAlt: product.name,
    }
  );
}
