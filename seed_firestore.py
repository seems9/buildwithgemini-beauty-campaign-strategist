"""Seed Firestore with initial beauty campaign pitches, product catalog items, and calendar entries."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-3d5d3b45ddf7"

def seed_data():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore with project: {PROJECT_ID}")

    # 1. Seed Products Catalog
    products = [
        {
            "sku": "SKU-GLOW-01",
            "name": "Barrier Restore Milky Hydrating Toner",
            "brand": "PureBotanicals",
            "category": "Skincare",
            "price": 38.0,
            "hero_ingredients": ["Ceramides", "Hyaluronic Acid", "Centella"],
            "claims": ["Hydrates 24hr", "Soothes redness", "Skin-barrier support"],
            "status": "In Stock"
        },
        {
            "sku": "SKU-GLOW-02",
            "name": "Nectar Glow Serum Tint with SPF 30",
            "brand": "Lumière Beauté",
            "category": "Hybrid Makeup",
            "price": 46.0,
            "hero_ingredients": ["Niacinamide", "Peptides", "Mineral SPF 30"],
            "claims": ["Dewy glass-skin finish", "Sheer-to-medium coverage", "Non-comedogenic"],
            "status": "In Stock"
        },
        {
            "sku": "SKU-GLOW-03",
            "name": "Peptide Plump Peptide Lip Oil",
            "brand": "Velvet Drench",
            "category": "Lip Care",
            "price": 24.0,
            "hero_ingredients": ["Tripeptides", "Jojoba Oil", "Vitamin E"],
            "claims": ["High-shine glaze", "Instant cushion hydration", "Clean formula"],
            "status": "In Stock"
        }
    ]

    for p in products:
        db.collection("products").document(p["sku"]).set(p)
        print(f"  [+] Seeded product: {p['name']} ({p['sku']})")

    # 2. Seed Campaign Pitches & Calendar Entries
    campaigns = [
        {
            "campaign_id": "CAMP-STREAMING-01",
            "title": "Skin Streaming — Less Steps, Maximum Glow",
            "hook": "Stop layering 8 serums. Here is the 3-step formula dermatologists actually agree on.",
            "target_audience": "Gen Z & Millennial Skin-Minimalists (Ages 22-34)",
            "format": "5-Slide Educational IG Carousel + 15s TikTok",
            "platform": "Instagram, TikTok",
            "scheduled_week": "Week 1",
            "impact_score": 88,
            "impact_basis": "High save-rate on educational skincare guides + high conversion on 3-step bundle checkout.",
            "status": "Approved",
            "region": "US"
        },
        {
            "campaign_id": "CAMP-VANITY-02",
            "title": "Vanity Declutter: Keep, Toss, Upgrade",
            "hook": "A Sephora Beauty Advisor audits a 12-step shelfie down to 3 power players.",
            "target_audience": "Gen Z Routine Experimenters",
            "format": "30s Short-Form Video (ASMR / Split-screen)",
            "platform": "YouTube Shorts, TikTok",
            "scheduled_week": "Week 2",
            "impact_score": 82,
            "impact_basis": "High retention on declutter/organization formats; strong organic virality.",
            "status": "Draft",
            "region": "US"
        },
        {
            "campaign_id": "CAMP-TRIO-03",
            "title": "Shop the Trio: Beauty Insider Exclusive",
            "hook": "Hyaluronic Acid + Niacinamide + Peptide Tint: The holy trinity for dull skin.",
            "target_audience": "Beauty Insider VIB & Rouge Members",
            "format": "Interactive App Story & CRM Email Hero",
            "platform": "Sephora App, Email",
            "scheduled_week": "Week 2",
            "impact_score": 91,
            "impact_basis": "Direct push to high-LTV members with immediate Add-to-Bag integration.",
            "status": "Scheduled",
            "region": "US"
        }
    ]

    for c in campaigns:
        db.collection("campaign_pitches").document(c["campaign_id"]).set(c)
        print(f"  [+] Seeded campaign pitch: {c['title']} ({c['campaign_id']})")

    print("\n✅ Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
