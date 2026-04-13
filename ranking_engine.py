import json
import re

def parse_price_range(budget_str):
    """Parse budget string like '10000-20000' or '10000' into min/max."""
    budget_str = str(budget_str).replace("₹", "").replace(",", "").strip()
    if "-" in budget_str:
        parts = budget_str.split("-")
        try:
            return float(parts[0].strip()), float(parts[1].strip())
        except Exception:
            pass
    try:
        val = float(budget_str)
        return val * 0.7, val
    except Exception:
        return 0, 999999

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 1.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

def compute_match_score(product, user_prefs, features, sentiment):
    """
    Compute a normalized match score (0-1) for a product based on user preferences.
    Factors:
    - Budget compatibility (0-30 points)
    - Feature match (0-25 points)
    - Use-case relevance (0-20 points)
    - Sentiment / rating quality (0-15 points)
    - Brand preference (0-10 points)
    """
    score = 0.0
    breakdown = {}

    price = product.get("price", 0)
    budget_min = user_prefs.get("budget_min", 0)
    budget_max = user_prefs.get("budget_max", 999999)

    # 1. Budget compatibility (30 points)
    if budget_min <= price <= budget_max:
        # Perfectly within budget - score based on position
        budget_range = budget_max - budget_min if budget_max != budget_min else 1
        budget_position = (price - budget_min) / budget_range
        # Prefer products in middle of budget range
        budget_score = 30 * (1 - abs(budget_position - 0.5))
        budget_score = max(20, budget_score)  # At least 20 if in range
    elif price < budget_min:
        # Under budget - still good but slight penalty
        under_pct = (budget_min - price) / budget_min if budget_min > 0 else 0
        budget_score = max(0, 20 - under_pct * 30)
    else:
        # Over budget - penalize
        over_pct = (price - budget_max) / budget_max if budget_max > 0 else 1
        budget_score = max(0, 15 - over_pct * 30)
    breakdown["budget"] = round(budget_score, 2)
    score += budget_score

    # 2. Feature match (25 points)
    required_features = [f.lower() for f in user_prefs.get("features", [])]
    product_features_text = ""
    specs_raw = product.get("specifications", "{}")
    if isinstance(specs_raw, str):
        try:
            specs = json.loads(specs_raw)
        except Exception:
            specs = {}
    else:
        specs = specs_raw

    product_features_text = " ".join([
        product.get("title", "").lower(),
        " ".join(str(v).lower() for v in specs.values()),
        " ".join(features.get("key_features", [])).lower()
    ])

    if required_features:
        matched = sum(1 for f in required_features if f in product_features_text)
        feature_score = 25 * (matched / len(required_features))
    else:
        feature_score = 15  # Neutral if no features specified
    breakdown["features"] = round(feature_score, 2)
    score += feature_score

    # 3. Use-case relevance (20 points)
    use_case = user_prefs.get("use_case", "").lower()
    use_cases_text = " ".join(features.get("use_cases", [])).lower()
    target_audience = features.get("target_audience", "").lower()
    product_title = product.get("title", "").lower()
    all_text = f"{use_cases_text} {target_audience} {product_title}"

    use_case_keywords = {
        "gaming": ["gaming", "game", "fps", "gpu", "graphics", "rtx", "performance"],
        "office": ["office", "productivity", "work", "business", "document"],
        "photography": ["camera", "photo", "photography", "mp", "megapixel", "lens"],
        "student": ["student", "study", "education", "portable", "lightweight", "budget"],
        "music": ["music", "audio", "sound", "bass", "anc", "headphone"],
        "travel": ["travel", "portable", "battery", "lightweight", "anc"],
        "streaming": ["streaming", "display", "screen", "amoled", "oled", "hdr"]
    }

    best_match = 0
    for uc, keywords in use_case_keywords.items():
        if uc in use_case or any(kw in use_case for kw in keywords):
            matched_kw = sum(1 for kw in keywords if kw in all_text)
            match_ratio = matched_kw / len(keywords)
            best_match = max(best_match, match_ratio)

    if best_match > 0:
        use_case_score = 20 * best_match
    elif use_case:
        # Check for direct keyword match in product text
        if any(word in all_text for word in use_case.split()):
            use_case_score = 10
        else:
            use_case_score = 5
    else:
        use_case_score = 12
    breakdown["use_case"] = round(use_case_score, 2)
    score += use_case_score

    # 4. Sentiment / rating quality (15 points)
    rating = product.get("rating", 0)
    num_reviews = product.get("num_reviews", 0)
    sentiment_score_val = sentiment.get("sentiment_score", 0.5)

    rating_normalized = normalize(rating, 1, 5)
    reviews_normalized = min(1.0, num_reviews / 10000)

    quality_score = 15 * (0.5 * rating_normalized + 0.3 * sentiment_score_val + 0.2 * reviews_normalized)
    breakdown["quality"] = round(quality_score, 2)
    score += quality_score

    # 5. Brand preference (10 points)
    brand = product.get("brand", "").lower()
    preferred_brands = [b.lower() for b in user_prefs.get("brand_preference", [])]
    avoided_brands = [b.lower() for b in user_prefs.get("avoid_brands", [])]

    if avoided_brands and brand in avoided_brands:
        brand_score = -10  # Penalize avoided brands
    elif preferred_brands and brand in preferred_brands:
        brand_score = 10
    elif preferred_brands:
        brand_score = 3  # Partial if brand specified but no match
    else:
        brand_score = 5  # Neutral
    brand_score = max(0, brand_score)
    breakdown["brand"] = round(brand_score, 2)
    score += brand_score

    # Normalize to 0-1
    max_possible = 100
    final_score = min(1.0, max(0.0, score / max_possible))
    breakdown["total"] = round(final_score, 4)

    return final_score, breakdown

def rank_products(products_with_scores):
    """Sort products by match score descending."""
    return sorted(products_with_scores, key=lambda x: x["match_score"], reverse=True)
