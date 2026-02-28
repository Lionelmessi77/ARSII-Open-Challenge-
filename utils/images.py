"""
Tourism Images Service
Provides images for Tunisian destinations using reliable image sources
"""

from typing import List, Dict

# Destination images - using working Unsplash photo IDs
DESTINATION_IMAGES = {
    "sidi bou said": {
        "urls": [
            "https://images.unsplash.com/photo-1590059391249-1a56b8e64553?w=800&auto=format&fit=crop&q=80",  # Similar to Sidi Bou Said
            "https://images.unsplash.com/photo-1579612263439-2fd4f481052f?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1604394851211-3842cf965181?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Sidi Bou Said, Tunisia"
    },
    "carthage": {
        "urls": [
            "https://images.unsplash.com/photo-1568608862965-c2a7e6ddd8a8?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1555992828-ca4dbe41d294?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Ancient Carthage, Tunisia"
    },
    "el jem": {
        "urls": [
            "https://images.unsplash.com/photo-1555992828-ca4dbe41d294?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1568608862965-c2a7e6ddd8a8?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1533427274577-10d3e2990048?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "El Jem Colosseum, Tunisia"
    },
    "sahara": {
        "urls": [
            "https://images.unsplash.com/photo-1547231601-95d8c65c7c0d?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542401886-65d6c61db217?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1534234828563-02511c759c68?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Sahara Desert, Tunisia"
    },
    "douz": {
        "urls": [
            "https://images.unsplash.com/photo-1547231601-95d8c65c7c0d?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542401886-65d6c61db217?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Douz, Gateway to Sahara"
    },
    "djerba": {
        "urls": [
            "https://images.unsplash.com/photo-1570845179322-47d5d3f5c84c?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1580619305218-8423a7ef79b4?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1534167885842-4b8b7647ee9b?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Djerba Island, Tunisia"
    },
    "kairouan": {
        "urls": [
            "https://images.unsplash.com/photo-1564769625905-50e93615e769?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542383160-3b2ec1a29b7a?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Kairouan, Holy City"
    },
    "medina": {
        "urls": [
            "https://images.unsplash.com/photo-1549141940-23f269f42a37?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1575318019540-954e29557a0e?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1549147421-d631a8d7886c?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Medina of Tunis"
    },
    "tunis": {
        "urls": [
            "https://images.unsplash.com/photo-1579612263439-2fd4f481052f?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1590059391249-1a56b8e64553?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1549141940-23f269f42a37?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Tunis, Tunisia"
    },
    "hammamet": {
        "urls": [
            "https://images.unsplash.com/photo-1570845179322-47d5d3f5c84c?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1580619305218-8423a7ef79b4?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Hammamet, Tunisia"
    },
    "sousse": {
        "urls": [
            "https://images.unsplash.com/photo-1570845179322-47d5d3f5c84c?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1580619305218-8423a7ef79b4?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Sousse, Tunisia"
    },
    "matmata": {
        "urls": [
            "https://images.unsplash.com/photo-1547231601-95d8c65c7c0d?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542401886-65d6c61db217?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Matmata, Underground Homes"
    },
    "ichkeul": {
        "urls": [
            "https://images.unsplash.com/photo-1445047172401-2f2743f1a932?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Lake Ichkeul National Park"
    },
    "bizerte": {
        "urls": [
            "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Bizerte, Tunisia"
    },
    "tabarka": {
        "urls": [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Tabarka, Tunisia"
    },
    "monastir": {
        "urls": [
            "https://images.unsplash.com/photo-1570845179322-47d5d3f5c84c?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Monastir, Tunisia"
    },
    # Generic Tunisia images (fallback)
    "tunisia": {
        "urls": [
            "https://images.unsplash.com/photo-1579612263439-2fd4f481052f?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1590059391249-1a56b8e64553?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1568608862965-c2a7e6ddd8a8?w=800&auto=format&fit=crop&q=80",
        ],
        "attribution": "Tunisia"
    },
}

# Attraction type images
ATTRACTION_IMAGES = {
    "bardo": ["https://images.unsplash.com/photo-1579612263439-2fd4f481052f?w=800&auto=format&fit=crop&q=80"],
    "mosque": ["https://images.unsplash.com/photo-1564769625905-50e93615e769?w=800&auto=format&fit=crop&q=80"],
    "beach": ["https://images.unsplash.com/photo-1570845179322-47d5d3f5c84c?w=800&auto=format&fit=crop&q=80"],
    "desert": ["https://images.unsplash.com/photo-1547231601-95d8c65c7c0d?w=800&auto=format&fit=crop&q=80"],
    "roman": ["https://images.unsplash.com/photo-1555992828-ca4dbe41d294?w=800&auto=format&fit=crop&q=80"],
    "ruins": ["https://images.unsplash.com/photo-1568608862965-c2a7e6ddd8a8?w=800&auto=format&fit=crop&q=80"],
    "medina": ["https://images.unsplash.com/photo-1549141940-23f269f42a37?w=800&auto=format&fit=crop&q=80"],
    "fort": ["https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800&auto=format&fit=crop&q=80"],
}


def get_destination_images(destination: str, limit: int = 3) -> List[Dict[str, str]]:
    """
    Get images for a destination

    Args:
        destination: Destination name (case-insensitive)
        limit: Max number of images to return

    Returns:
        List of dicts with 'url' and 'attribution' keys
    """
    dest_lower = destination.lower()

    # Direct match
    if dest_lower in DESTINATION_IMAGES:
        data = DESTINATION_IMAGES[dest_lower]
        return [
            {"url": url, "attribution": data["attribution"]}
            for url in data["urls"][:limit]
        ]

    # Partial match
    for key, data in DESTINATION_IMAGES.items():
        if key in dest_lower or dest_lower in key:
            return [
                {"url": url, "attribution": data["attribution"]}
                for url in data["urls"][:limit]
            ]

    # Fallback to Tunisia images
    return [
        {"url": url, "attribution": "Tunisia"}
        for url in DESTINATION_IMAGES["tunisia"]["urls"][:limit]
    ]


def get_attraction_images(attraction: str, limit: int = 2) -> List[str]:
    """Get images for an attraction type"""
    attraction_lower = attraction.lower()

    for key, urls in ATTRACTION_IMAGES.items():
        if key in attraction_lower:
            return urls[:limit]

    # Try destination images
    return get_destination_images(attraction, limit)


def find_images_in_text(text: str) -> List[Dict[str, str]]:
    """
    Find relevant images based on text content
    Searches for destination names in the text

    Args:
        text: Text to search through

    Returns:
        List of image dicts
    """
    text_lower = text.lower()
    found_images = []

    # Check each destination
    for dest_key, data in DESTINATION_IMAGES.items():
        if dest_key in text_lower:
            for url in data["urls"][:1]:  # One image per destination
                found_images.append({
                    "url": url,
                    "attribution": data["attribution"],
                    "destination": dest_key
                })

    return found_images[:5]  # Max 5 images
