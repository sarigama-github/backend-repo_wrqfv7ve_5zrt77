"""
Database Schemas for Affiliate Site

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase class name.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class Category(BaseModel):
    name: str = Field(..., description="Display name for the category")
    slug: str = Field(..., description="URL-safe identifier for the category")
    description: Optional[str] = Field(None, description="Short SEO description")
    icon: Optional[str] = Field(None, description="Icon name or URL")

class ReviewItem(BaseModel):
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    rating: float = Field(..., ge=0, le=5, description="Average rating 0-5")
    verdict: Optional[str] = None

class Product(BaseModel):
    title: str
    slug: str
    image_url: Optional[HttpUrl] = None
    price: Optional[float] = Field(None, ge=0)
    category: str = Field(..., description="Category slug")
    brand: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    review: Optional[ReviewItem] = None
    affiliate_url: Optional[HttpUrl] = None
    alt_options: List[str] = Field(default_factory=list, description="List of alternative product slugs")
    featured: bool = Field(False, description="Whether to show as trending/featured")

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: str
    content: str
    category: Optional[str] = Field(None, description="Category slug this post targets")
    hero_image: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)

# Minimal example to keep backward compatibility for other tools
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True
