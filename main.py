import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Chenarae – Handmade Pipe-Cleaner Bouquets API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def seed_products_on_startup():
    try:
        if db is None:
            return
        # If there are already products, skip seeding
        if db["product"].count_documents({}) > 0:
            return
        seed_items = [
            {
                "title": "Blush Baby’s-Breath — Mini",
                "description": "Tiny clustered blush blooms — airy, charming, gift-ready. Size 20–25 cm • Mini stems • Perfect for desks • Pastel blush",
                "price": 18.0,
                "category": "Bestsellers",
                "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=2000&auto=format&fit=crop",
                "tags": ["baby's breath", "mini", "blush", "gift", "pipe-cleaner"],
                "in_stock": True,
                "sku": "CH-MINI-BLUSH",
                "stock_qty": 25,
            },
            {
                "title": "Pastel Meadow — Mixed Bouquet",
                "description": "Pastel roses, buds & greenery — full and soft. Size 30–40 cm • 7 stems • Ribbon wrap included",
                "price": 48.0,
                "category": "Bestsellers",
                "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?q=80&w=2000&auto=format&fit=crop",
                "tags": ["pastel", "mixed", "bouquet", "roses", "pipe-cleaner"],
                "in_stock": True,
                "sku": "CH-PASTEL-MEADOW",
                "stock_qty": 12,
            },
            {
                "title": "Lavender Dream — Tall Spray",
                "description": "Elegant tall lavender-style stems for vases. Height 40–50 cm • 5 stems • Great for tall vases",
                "price": 32.0,
                "category": "Tall Sprays",
                "image_url": "https://images.unsplash.com/photo-1491002052546-bf38f186af56?q=80&w=2000&auto=format&fit=crop",
                "tags": ["lavender", "tall", "spray", "vase", "pipe-cleaner"],
                "in_stock": True,
                "sku": "CH-LAVENDER-DREAM",
                "stock_qty": 18,
            },
            {
                "title": "Peach Blossom — Bridal Posy",
                "description": "Warm-toned bridal bouquet wrapped for ceremonies. Size 20–30 cm • Custom ribbon • Bulk wedding orders",
                "price": 65.0,
                "category": "Wedding & Events",
                "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=2000&auto=format&fit=crop",
                "tags": ["peach", "bridal", "wedding", "posy", "pipe-cleaner"],
                "in_stock": True,
                "sku": "CH-PEACH-BLOSSOM",
                "stock_qty": 8,
            },
            {
                "title": "Custom Color Mix — Design Your Own",
                "description": "Choose up to 3 colors — your bouquet, your way. Lead time 3–7 days • Ribbon wrap • Gift note option",
                "price": 55.0,
                "category": "Custom Colors",
                "image_url": "https://images.unsplash.com/photo-1460634844282-68ad86a38133?q=80&w=2000&auto=format&fit=crop",
                "tags": ["custom", "colors", "personalized", "gift"],
                "in_stock": True,
                "sku": "CH-CUSTOM-MIX",
                "stock_qty": 100,
            },
            {
                "title": "Gift Box Add-on — Wrap + Note",
                "description": "Premium matte wrap + handwritten note. Protection wrap • Satin ribbon • Gift-ready",
                "price": 8.0,
                "category": "Add-ons",
                "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=2000&auto=format&fit=crop",
                "tags": ["gift", "wrap", "note", "add-on"],
                "in_stock": True,
                "sku": "CH-GIFT-BOX",
                "stock_qty": 50,
            },
        ]
        for item in seed_items:
            try:
                create_document("product", Product(**item))
            except Exception:
                pass
    except Exception:
        pass


@app.get("/")
def read_root():
    return {"message": "Chenarae Backend Running"}


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
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------- Product Endpoints ----------
@app.post("/api/products", response_model=dict)
async def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products", response_model=List[dict])
async def list_products(category: Optional[str] = None, q: Optional[str] = None, limit: int = 100):
    try:
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if q:
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}}
            ]
        docs = get_documents("product", filter_dict, limit)
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Order Endpoints ----------
@app.post("/api/orders", response_model=dict)
async def create_order(order: Order):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders", response_model=List[dict])
async def list_orders(limit: int = 50):
    try:
        docs = get_documents("order", {}, limit)
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
