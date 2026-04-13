from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import json
import os
from database import init_db, seed_sample_data, get_products_by_category, get_all_products, save_product_features, get_product_features
from gemini_engine import extract_features, analyze_sentiment, generate_recommendation_explanation
from ranking_engine import parse_price_range, compute_match_score, rank_products

app = Flask(__name__)
app.secret_key = "recoai_secret_key_2024_ultra_secure"

# ─── Demo user store (in production, use a real DB) ─────────────────────────
USERS = {
    "demo@recoai.com": {"password": "demo123", "name": "Demo User"},
    "admin@recoai.com": {"password": "admin123", "name": "Admin"},
}
SEARCH_HISTORY = {}  # keyed by email

# ─── Auth helpers ────────────────────────────────────────────────────────────
def logged_in():
    return "user_email" in session

def current_user():
    email = session.get("user_email")
    if email and email in USERS:
        return {"email": email, **USERS[email]}
    return None

# ─── Pages ───────────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if logged_in():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = USERS.get(email)
        if user and user["password"] == password:
            session["user_email"] = email
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if logged_in():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        if not name or not email or not password:
            flash("All fields are required.", "error")
        elif email in USERS:
            flash("Account already exists. Please login.", "error")
        else:
            USERS[email] = {"password": password, "name": name}
            session["user_email"] = email
            return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))
    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("login"))
    history = SEARCH_HISTORY.get(user["email"], [])
    products = get_all_products()
    categories = list(set(p["category"] for p in products if p["category"]))
    stats = {
        "total_products": len(products),
        "total_categories": len(categories),
        "searches_done": len(history),
        "avg_match": round(sum(h.get("best_match", 0) for h in history) / max(len(history), 1) * 100, 1),
    }
    return render_template("dashboard.html", user=user, stats=stats, history=history[:5])

@app.route("/recommend")
def recommend_page():
    if not logged_in():
        return redirect(url_for("login"))
    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("login"))
    return render_template("index.html", user=user)

# ─── API ─────────────────────────────────────────────────────────────────────
@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()

        budget_min_raw = data.get("budget_min", 0)
        budget_max_raw = data.get("budget_max", 999999)
        product_type = data.get("product_type", "").strip()
        features_raw = data.get("features", "")
        use_case = data.get("use_case", "").strip()
        brand_preference = data.get("brand_preference", "")
        avoid_brands = data.get("avoid_brands", "")
        top_n = int(data.get("top_n", 5))

        try:
            budget_min = float(budget_min_raw)
        except Exception:
            budget_min = 0
        try:
            budget_max = float(budget_max_raw)
        except Exception:
            budget_max = 999999

        if isinstance(features_raw, str):
            features_list = [f.strip() for f in features_raw.replace(",", "\n").split("\n") if f.strip()]
        elif isinstance(features_raw, list):
            features_list = features_raw
        else:
            features_list = []

        if isinstance(brand_preference, str):
            brand_prefs = [b.strip() for b in brand_preference.split(",") if b.strip()]
        else:
            brand_prefs = brand_preference

        if isinstance(avoid_brands, str):
            avoid_list = [b.strip() for b in avoid_brands.split(",") if b.strip()]
        else:
            avoid_list = avoid_brands

        user_prefs = {
            "budget_min": budget_min,
            "budget_max": budget_max,
            "product_type": product_type,
            "features": features_list,
            "use_case": use_case,
            "brand_preference": brand_prefs,
            "avoid_brands": avoid_list
        }

        if product_type:
            products = get_products_by_category(product_type)
            if not products:
                products = get_all_products()
        else:
            products = get_all_products()

        if not products:
            return jsonify({"error": "No products found in database"}), 404

        results = []
        for product in products:
            product_id = product["id"]
            cached = get_product_features(product_id)
            if cached:
                try:
                    features = json.loads(cached["features"])
                    pros_cons = {
                        "pros": json.loads(cached["pros"]),
                        "cons": json.loads(cached["cons"]),
                        "overall_sentiment": "positive",
                        "sentiment_score": 0.7
                    }
                except Exception:
                    features = extract_features(product)
                    pros_cons = analyze_sentiment(product)
                    save_product_features(product_id, features, pros_cons.get("pros", []), pros_cons.get("cons", []))
            else:
                features = extract_features(product)
                pros_cons = analyze_sentiment(product)
                save_product_features(product_id, features, pros_cons.get("pros", []), pros_cons.get("cons", []))

            match_score, breakdown = compute_match_score(product, user_prefs, features, pros_cons)

            specs_raw = product.get("specifications", "{}")
            if isinstance(specs_raw, str):
                try:
                    specs = json.loads(specs_raw)
                except Exception:
                    specs = {}
            else:
                specs = specs_raw

            results.append({
                "id": product_id,
                "title": product["title"],
                "price": product["price"],
                "rating": product["rating"],
                "num_reviews": product["num_reviews"],
                "brand": product["brand"],
                "category": product["category"],
                "specs": specs,
                "image_url": product.get("image_url", ""),
                "product_url": product.get("product_url", "#"),
                "seller": product.get("seller", ""),
                "key_features": features.get("key_features", []),
                "pros": pros_cons.get("pros", []),
                "cons": pros_cons.get("cons", []),
                "match_score": match_score,
                "score_breakdown": breakdown,
                "standout_feature": features.get("standout_feature", ""),
                "performance_tier": features.get("performance_tier", ""),
                "explanation": ""
            })

        ranked = rank_products(results)
        top_results = ranked[:top_n]

        for item in top_results:
            product_obj = {
                "title": item["title"],
                "price": item["price"],
                "rating": item["rating"],
                "num_reviews": item["num_reviews"]
            }
            features_obj = {"key_features": item["key_features"]}
            sentiment_obj = {"pros": item["pros"], "cons": item["cons"]}
            item["explanation"] = generate_recommendation_explanation(
                product_obj, user_prefs, item["match_score"], features_obj, sentiment_obj
            )

        # Save search to history
        if logged_in():
            email = session.get("user_email")
            if email not in SEARCH_HISTORY:
                SEARCH_HISTORY[email] = []
            SEARCH_HISTORY[email].insert(0, {
                "product_type": product_type,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "use_case": use_case,
                "count": len(top_results),
                "best_match": top_results[0]["match_score"] if top_results else 0,
                "top_result": top_results[0]["title"] if top_results else ""
            })

        return jsonify({
            "status": "success",
            "count": len(top_results),
            "user_prefs": user_prefs,
            "recommendations": top_results
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/categories", methods=["GET"])
def get_categories():
    products = get_all_products()
    categories = list(set(p["category"] for p in products if p["category"]))
    return jsonify({"categories": sorted(categories)})

@app.route("/api/products/count", methods=["GET"])
def product_count():
    products = get_all_products()
    return jsonify({"count": len(products)})

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
    seed_sample_data()
    print("✅ Database initialized with sample products")
    print("🚀 Starting RecoAI server at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
