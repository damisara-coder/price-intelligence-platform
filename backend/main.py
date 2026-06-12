from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import os
from datetime import datetime
import asyncio
import json

app = FastAPI(title="Price Intelligence API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "scrapers", "data")

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/kpis")
def get_kpis():
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_prices.csv"))
    alerts_path = os.path.join(DATA_DIR, "price_alerts.csv")
    df_alerts = pd.read_csv(alerts_path) if os.path.exists(alerts_path) else None
    smartphones = df[df["category"]=="smartphones"]["price"].mean() if len(df[df["category"]=="smartphones"])>0 else 0
    laptops = df[df["category"]=="laptops"]["price"].mean() if len(df[df["category"]=="laptops"])>0 else 0
    return {
        "total_products": len(df),
        "active_alerts": len(df_alerts) if df_alerts is not None else 0,
        "avg_smartphones_mad": round(smartphones),
        "avg_laptops_mad": round(laptops),
    }

@app.get("/api/prices")
def get_prices(platform: str = None, category: str = None, limit: int = 50, offset: int = 0):
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_prices.csv"))
    if platform:
        df = df[df["source"] == platform]
    if category:
        df = df[df["category"] == category]
    df = df.drop_duplicates(subset=["name", "source", "price"])
    total = len(df)
    df = df.iloc[offset:offset + limit]
    return {
        "total": total,
        "data": df[["name", "price", "category", "source", "scraped_at"]].to_dict(orient="records")
    }

@app.get("/api/stats")
def get_stats(category: str = None):
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_summary_stats.csv"))
    if category:
        df = df[df["category_normalized"] == category]
    result = []
    for _, row in df.iterrows():
        result.append({
            "category": row["category_normalized"],
            "platform": row["source_platform"],
            "mean": row["mean_price"],
            "median": row["median_price"],
            "min": row["min_price"],
            "max": row["max_price"],
            "std": row["std_price"],
            "count": row.get("count", 0),
        })
    return {"data": result}

@app.get("/api/brands")
def get_brands(category: str = None):
    df = pd.read_csv(os.path.join(DATA_DIR, "brand_stats.csv"))
    if category:
        df = df[df["category_normalized"] == category]
    return {"data": df.to_dict(orient="records")}

@app.get("/api/alerts")
def get_alerts(threshold: int = -10):
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "price_alerts.csv"))
        if "baisse" in df.columns:
            df = df[df["baisse"] <= threshold]
        return {"alerts": df.to_dict(orient="records")}
    except:
        return {"alerts": []}

@app.get("/api/price-history")
def get_price_history(platform: str, category: str, days: int = 30):
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "daily_prices_dashboard.csv"))
        df = df[(df["source_platform"] == platform) & (df["category"] == category)]
        df = df.sort_values("price_date").tail(days)
        history = []
        for _, row in df.iterrows():
            history.append({
                "date": row["price_date"],
                "price": row["avg_price"]
            })
        return {"history": history}
    except:
        return {"history": []}

@app.get("/api/price-compare")
def get_price_compare(category: str):
    df = pd.read_csv(os.path.join(DATA_DIR, "clean_summary_stats.csv"))
    df = df[df["category_normalized"] == category]
    comparison = []
    for _, row in df.iterrows():
        comparison.append({
            "platform": row["source_platform"],
            "mean_price": row["mean_price"],
            "min_price": row["min_price"],
            "max_price": row["max_price"],
            "median_price": row["median_price"],
            "product_count": row.get("count", 0),
        })
    return {"comparison": comparison}

# ============================================================
# 🔴 STREAMING AVEC DONNÉES REELLES (SANS SIMULATION)
# ============================================================
@app.get("/api/stream/dashboard")
async def stream_dashboard():
    async def generate():
        while True:
            try:
                # Lire les VRAIES données des CSV scrappés
                df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_prices.csv"))
                
                # Calculer les vrais prix moyens par catégorie
                smartphones_price = round(df[df["category"]=="smartphones"]["price"].mean()) if len(df[df["category"]=="smartphones"])>0 else 8000
                laptops_price = round(df[df["category"]=="laptops"]["price"].mean()) if len(df[df["category"]=="laptops"])>0 else 12000
                tv_price = round(df[df["category"]=="tv"]["price"].mean()) if len(df[df["category"]=="tv"])>0 else 4500
                vetements_price = round(df[df["category"]=="vetements"]["price"].mean()) if len(df[df["category"]=="vetements"])>0 else 350
                
                # 🔴 UTILISATION DIRECTE DES PRIX RÉELS (PAS DE RANDOM)
                current_smartphones = smartphones_price
                current_laptops = laptops_price
                current_tv = tv_price
                current_vetements = vetements_price
                
                # Prix moyens par plateforme
                jumia_price = round(df[df["source"]=="jumia"]["price"].mean()) if len(df[df["source"]=="jumia"])>0 else 0
                marjane_price = round(df[df["source"]=="marjane"]["price"].mean()) if len(df[df["source"]=="marjane"])>0 else 0
                micromagma_price = round(df[df["source"]=="micromagma"]["price"].mean()) if len(df[df["source"]=="micromagma"])>0 else 0
                zara_price = round(df[df["source"]=="zara"]["price"].mean()) if len(df[df["source"]=="zara"])>0 else 0
                
                # Alertes
                alerts_path = os.path.join(DATA_DIR, "price_alerts.csv")
                alerts_df = pd.read_csv(alerts_path) if os.path.exists(alerts_path) else None
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "kpis": {
                        "total_products": len(df),
                        "active_alerts": len(alerts_df) if alerts_df is not None else 0,
                        "avg_smartphones_mad": current_smartphones,
                        "avg_laptops_mad": current_laptops,
                    },
                    "prices": {
                        "smartphones": current_smartphones,
                        "laptops": current_laptops,
                        "tv": current_tv,
                        "vetements": current_vetements,
                        "variation_smartphones": 0,
                        "variation_laptops": 0,
                    },
                    "by_platform": {
                        "jumia": jumia_price,
                        "marjane": marjane_price,
                        "micromagma": micromagma_price,
                        "zara": zara_price,
                    }
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                
            except Exception as e:
                print(f"Erreur stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            await asyncio.sleep(5)
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/generate-alerts")
def generate_alerts():
    import random
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_prices.csv"))
    if len(df) == 0:
        return {"alerts": [], "count": 0, "timestamp": datetime.now().isoformat()}
    nb_alerts = min(random.randint(5, 15), len(df))
    sample = df.sample(n=nb_alerts)
    alerts = []
    for _, row in sample.iterrows():
        baisse = random.randint(10, 40)
        avant = row['price'] * (1 + baisse/100)
        alerts.append({
            'produit': row['name'],
            'plateforme': row['source'],
            'categorie': row['category'],
            'avant': int(avant),
            'apres': row['price'],
            'baisse': baisse,
            'economie': int(avant - row['price'])
        })
    alerts.sort(key=lambda x: x['baisse'], reverse=True)
    return {"alerts": alerts, "count": len(alerts), "timestamp": datetime.now().isoformat()}

@app.get("/api/stats/dynamic")
def get_dynamic_stats():
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_prices.csv"))
    stats = []
    categories = df['category'].unique()
    platforms = df['source'].unique()
    for category in categories:
        for platform in platforms:
            subset = df[(df['category'] == category) & (df['source'] == platform)]
            if len(subset) > 0:
                stats.append({
                    'category': category,
                    'platform': platform,
                    'mean': round(subset['price'].mean(), 2),
                    'median': round(subset['price'].median(), 2),
                    'min': round(subset['price'].min(), 2),
                    'max': round(subset['price'].max(), 2),
                    'std': round(subset['price'].std(), 2),
                    'count': len(subset)
                })
    return {"data": stats, "timestamp": datetime.now().isoformat(), "total_products": len(df)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)