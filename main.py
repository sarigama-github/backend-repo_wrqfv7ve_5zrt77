import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Category, Product, BlogPost

app = FastAPI(title="Affiliate Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility

def _collection(name: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    return db[name]


def seed_if_empty():
    """Seed database with initial categories, products, and posts if empty."""
    try:
        cat_col = _collection("category")
        prod_col = _collection("product")
        blog_col = _collection("blogpost")

        if cat_col.count_documents({}) == 0:
            categories = [
                {"name": "Tech", "slug": "tech", "description": "Latest in consumer tech and gadgets", "icon": "Cpu"},
                {"name": "Gadgets", "slug": "gadgets", "description": "Smart devices and accessories", "icon": "Smartphone"},
                {"name": "Beauty", "slug": "beauty", "description": "Skincare, makeup, and wellness", "icon": "Sparkles"},
                {"name": "Fitness", "slug": "fitness", "description": "Gear for health and workouts", "icon": "Dumbbell"},
                {"name": "Home", "slug": "home", "description": "Home improvement & decor", "icon": "Home"},
                {"name": "Kitchen", "slug": "kitchen", "description": "Cookware and appliances", "icon": "Utensils"},
                {"name": "Fashion", "slug": "fashion", "description": "Style essentials and apparel", "icon": "Shirt"},
                {"name": "Personal Care", "slug": "personal-care", "description": "Daily care products", "icon": "Heart"},
                {"name": "Lifestyle", "slug": "lifestyle", "description": "Everyday carry and more", "icon": "Star"},
                {"name": "Gaming", "slug": "gaming", "description": "Consoles & accessories", "icon": "Gamepad2"},
            ]
            cat_col.insert_many(categories)

        if prod_col.count_documents({}) == 0:
            products = [
                {
                    "title": "ZenBook Pro 14 OLED",
                    "slug": "zenbook-pro-14-oled",
                    "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
                    "price": 1899.0,
                    "category": "tech",
                    "brand": "ASUS",
                    "highlights": ["14\" 3K OLED", "Intel i9", "NVIDIA RTX 4070"],
                    "review": {"pros": ["Gorgeous display", "Powerful GPU"], "cons": ["Pricey"], "rating": 4.6, "verdict": "A portable powerhouse for creators."},
                    "affiliate_url": "https://example.com/zenbook?ref=aff",
                    "alt_options": ["macbook-pro-14", "dell-xps-15"],
                    "featured": True,
                },
                {
                    "title": "HyperMix Pro Blender",
                    "slug": "hypermix-pro-blender",
                    "image_url": "https://images.unsplash.com/photo-1542444459-db63c9f1d2fa?q=80&w=1200&auto=format&fit=crop",
                    "price": 149.0,
                    "category": "kitchen",
                    "brand": "Blendify",
                    "highlights": ["1200W motor", "8 presets", "Self-clean"],
                    "review": {"pros": ["Great value", "Easy to clean"], "cons": ["Loud at max"], "rating": 4.4, "verdict": "Excellent daily blender for smoothies."},
                    "affiliate_url": "https://example.com/hypermix?ref=aff",
                    "alt_options": ["nutri-ninja-pro"],
                    "featured": True,
                },
                {
                    "title": "AeroFit Smartwatch 6",
                    "slug": "aerofit-smartwatch-6",
                    "image_url": "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?q=80&w=1200&auto=format&fit=crop",
                    "price": 229.0,
                    "category": "fitness",
                    "brand": "Aero",
                    "highlights": ["AMOLED", "GPS", "7-day battery"],
                    "review": {"pros": ["Accurate tracking", "Bright screen"], "cons": ["Limited apps"], "rating": 4.2, "verdict": "Strong fitness-first smartwatch."},
                    "affiliate_url": "https://example.com/aerofit?ref=aff",
                    "alt_options": ["fitbit-versa-3"],
                    "featured": True,
                },
            ]
            prod_col.insert_many(products)

        if blog_col.count_documents({}) == 0:
            posts = [
                {
                    "title": "Best Laptops for Creators in 2025",
                    "slug": "best-laptops-for-creators-2025",
                    "excerpt": "Our researched picks for video editors, designers, and 3D artists.",
                    "content": "# Best Laptops for Creators\nWe compared performance, displays, and thermals across top models...",
                    "category": "tech",
                    "hero_image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["laptops", "creators", "guides"],
                },
                {
                    "title": "10 Must-Have Kitchen Tools for 2025",
                    "slug": "must-have-kitchen-tools-2025",
                    "excerpt": "Make meal prep faster and easier with these editor-approved picks.",
                    "content": "# Must-Have Kitchen Tools\nFrom blenders to air fryers, here are our top choices...",
                    "category": "kitchen",
                    "hero_image": "https://images.unsplash.com/photo-1542444459-db63c9f1d2fa?q=80&w=1200&auto=format&fit=crop",
                    "tags": ["kitchen", "gear", "guides"],
                },
            ]
            blog_col.insert_many(posts)
    except Exception:
        # If seeding fails, continue without crashing
        pass


@app.on_event("startup")
async def on_startup():
    seed_if_empty()


@app.get("/")
def read_root():
    return {"message": "Affiliate Hub Backend Running"}


# Categories
@app.get("/api/categories", response_model=List[Category])
def list_categories():
    items = list(_collection("category").find({}, {"_id": 0}))
    return items


# Products
@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = Query(None), featured: Optional[bool] = Query(None)):
    q = {}
    if category:
        q["category"] = category
    if featured is not None:
        q["featured"] = featured
    items = list(_collection("product").find(q, {"_id": 0}))
    return items


@app.get("/api/product/{slug}", response_model=Product)
def get_product(slug: str):
    doc = _collection("product").find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return doc


# Blog
@app.get("/api/blog", response_model=List[BlogPost])
def list_blog(category: Optional[str] = Query(None)):
    q = {"category": category} if category else {}
    items = list(_collection("blogpost").find(q, {"_id": 0}))
    return items


@app.get("/api/blog/{slug}", response_model=BlogPost)
def get_blog_post(slug: str):
    doc = _collection("blogpost").find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return doc


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
            response["database"] = "✅ Connected & Working"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
