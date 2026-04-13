import google.generativeai as genai
import json
import re
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def safe_json_parse(text):
    """Try to extract JSON from Gemini response."""
    text = text.strip()
    # Remove markdown code blocks if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        # Try to find JSON object in text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        # Try to find JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None

def extract_features(product):
    """Use Gemini to extract structured features from product specs and reviews."""
    specs = product.get("specifications", "{}")
    if isinstance(specs, str):
        try:
            specs = json.loads(specs)
        except Exception:
            specs = {}

    reviews_raw = product.get("reviews", "[]")
    if isinstance(reviews_raw, str):
        try:
            reviews = json.loads(reviews_raw)
        except Exception:
            reviews = []
    else:
        reviews = reviews_raw

    reviews_text = "\n".join(reviews[:5]) if reviews else "No reviews available"

    prompt = f"""You are a product feature extractor. Analyze the following product and extract structured features.

Product: {product.get('title', '')}
Category: {product.get('category', '')}
Price: ₹{product.get('price', 0)}
Specifications: {json.dumps(specs, indent=2)}
Sample Reviews: {reviews_text}

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "key_features": ["feature1", "feature2", "feature3", "feature4", "feature5"],
  "use_cases": ["use_case1", "use_case2", "use_case3"],
  "target_audience": "description of ideal user",
  "performance_tier": "budget/mid-range/premium",
  "standout_feature": "the single most impressive feature"
}}"""

    try:
        response = model.generate_content(prompt)
        result = safe_json_parse(response.text)
        if result:
            return result
    except Exception as e:
        print(f"Feature extraction error: {e}")

    # Fallback
    return {
        "key_features": list(specs.values())[:5] if specs else [],
        "use_cases": ["General use"],
        "target_audience": "General consumers",
        "performance_tier": "mid-range",
        "standout_feature": "Value for money"
    }

def analyze_sentiment(product):
    """Use Gemini to analyze pros and cons from reviews."""
    reviews_raw = product.get("reviews", "[]")
    if isinstance(reviews_raw, str):
        try:
            reviews = json.loads(reviews_raw)
        except Exception:
            reviews = []
    else:
        reviews = reviews_raw

    reviews_text = "\n".join([f"- {r}" for r in reviews]) if reviews else "No reviews available"

    prompt = f"""You are a sentiment analysis expert for product reviews.

Product: {product.get('title', '')}
Rating: {product.get('rating', 0)}/5 from {product.get('num_reviews', 0)} reviews
Reviews:
{reviews_text}

Analyze these reviews and return ONLY a valid JSON object (no markdown, no explanation):
{{
  "pros": ["pro1", "pro2", "pro3"],
  "cons": ["con1", "con2", "con3"],
  "overall_sentiment": "positive/neutral/negative",
  "sentiment_score": 0.0
}}

Rules:
- pros: 2-4 genuine strengths from reviews
- cons: 2-3 genuine weaknesses or limitations
- sentiment_score: float between 0 and 1 (1 = very positive)"""

    try:
        response = model.generate_content(prompt)
        result = safe_json_parse(response.text)
        if result:
            return result
    except Exception as e:
        print(f"Sentiment analysis error: {e}")

    # Fallback based on rating
    rating = product.get("rating", 3.0)
    return {
        "pros": ["Decent performance", "Good value"],
        "cons": ["Could be improved"],
        "overall_sentiment": "positive" if rating >= 4 else "neutral",
        "sentiment_score": rating / 5.0
    }

def generate_recommendation_explanation(product, user_prefs, match_score, features, sentiment):
    """Generate a human-readable explanation for why this product is recommended."""

    prompt = f"""You are a product recommendation expert. Generate a clear, helpful explanation for why this product matches the user's needs.

USER PREFERENCES:
- Budget: ₹{user_prefs.get('budget_min', 0)} - ₹{user_prefs.get('budget_max', 100000)}
- Product Type: {user_prefs.get('product_type', '')}
- Feature Requirements: {', '.join(user_prefs.get('features', []))}
- Use Case: {user_prefs.get('use_case', '')}
- Brand Preference: {user_prefs.get('brand_preference', 'No preference')}

PRODUCT DETAILS:
- Name: {product.get('title', '')}
- Price: ₹{product.get('price', 0)}
- Rating: {product.get('rating', 0)}/5 ({product.get('num_reviews', 0)} reviews)
- Match Score: {match_score:.0%}
- Key Features: {', '.join(features.get('key_features', [])[:3])}
- Pros: {', '.join(sentiment.get('pros', [])[:2])}
- Cons: {', '.join(sentiment.get('cons', [])[:2])}

Write a 3-4 sentence explanation that:
1. Explains why this product matches the user's specific needs
2. Highlights the most relevant features for their use case
3. Mentions any trade-offs honestly
4. Is conversational and helpful (not salesy)

Return ONLY the explanation text, no JSON, no formatting."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Explanation generation error: {e}")
        return f"This product matches {match_score:.0%} of your requirements. It offers good value with a rating of {product.get('rating', 0)}/5 from {product.get('num_reviews', 0)} reviews. Consider the pros and cons before making your decision."
