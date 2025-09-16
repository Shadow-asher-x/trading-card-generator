from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
import time
import logging
import os
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trading Card Generator API", version="1.0.0")

# Create directories for static files
UPLOAD_DIR = Path("static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GenerateImageRequest(BaseModel):
    prompt: str

class Attack(BaseModel):
    name: str
    damage: int
    description: str

class CardMetadata(BaseModel):
    name: Optional[str] = None
    hp: Optional[int] = None
    type: Optional[str] = None
    rarity: Optional[str] = None
    flavorText: Optional[str] = None
    attacks: Optional[List[Attack]] = None

class GenerateImageResponse(BaseModel):
    image_url: str
    metadata: Optional[CardMetadata] = None
    generation_time: float

class CardExportRequest(BaseModel):
    name: str
    hp: int
    type: str
    rarity: str
    flavorText: str
    attacks: List[Attack]
    image_url: str

class SaveCardRequest(BaseModel):
    name: str
    hp: int
    type: str
    rarity: str
    flavorText: str
    attacks: List[Attack]
    image_url: str
    user_id: Optional[str] = None

# Stub data for testing - Replace with your own image URLs
PLACEHOLDER_IMAGES = [
    "https://your-image-host.com/dragon1.jpg",
    "https://your-image-host.com/wolf1.jpg", 
    "https://your-image-host.com/phoenix1.jpg",
    "https://your-image-host.com/tiger1.jpg",
    "https://your-image-host.com/owl1.jpg",
    # Add as many as you want - the system will pick randomly
]

CREATURE_NAMES = [
    "Shadowclaw", "Flameheart", "Crystalwing", "Stormfang", "Moonwhisper",
    "Ironhide", "Mistral", "Thornback", "Frostbite", "Embercrest"
]

CREATURE_TYPES = ["Fire", "Water", "Earth", "Air", "Dark", "Light"]
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

ATTACK_TEMPLATES = [
    {"name": "Strike", "damage": 25, "description": "A basic physical attack"},
    {"name": "Flame Burst", "damage": 35, "description": "Unleashes a burst of fire damage"},
    {"name": "Ice Shard", "damage": 30, "description": "Launches sharp ice projectiles"},
    {"name": "Thunder Bolt", "damage": 40, "description": "Strikes with lightning"},
    {"name": "Heal", "damage": 0, "description": "Restores 25 HP"},
    {"name": "Shield", "damage": 0, "description": "Reduces next attack by 50%"},
]

FLAVOR_TEXTS = [
    "A legendary creature from the ancient realms.",
    "Born from the elements themselves.",
    "Guardian of the sacred forests.",
    "Master of the elemental forces.",
    "A mysterious being of immense power.",
]
# Fallback images if no local images are found
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=500&fit=crop&crop=center",  # Dragon
    "https://images.unsplash.com/photo-1520637836862-4d197d17c73a?w=400&h=500&fit=crop&crop=center",  # Wolf
    "https://images.unsplash.com/photo-1551582045-6ec9c671a834?w=400&h=500&fit=crop&crop=center",  # Phoenix
]

def get_placeholder_images():
    """Get list of available placeholder images"""
    image_files = []
    if UPLOAD_DIR.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            image_files.extend(UPLOAD_DIR.glob(ext))
    
    # Convert to URLs
    base_url = "http://localhost:8000/static/images"
    return [f"{base_url}/{img.name}" for img in image_files]

async def analyze_image_and_generate_stats(image_url: str, original_prompt: str) -> CardMetadata:
    """Use AI vision to analyze the generated image and create appropriate card stats"""
    
    # In production, this would call GPT-4 Vision or similar
    # For now, we'll simulate intelligent analysis based on the image and prompt
    
    # Download and analyze image (simulated)
    vision_analysis = await simulate_vision_analysis(image_url, original_prompt)
    
    # Generate stats based on vision analysis
    stats = generate_stats_from_analysis(vision_analysis)
    
    return stats

async def simulate_vision_analysis(image_url: str, prompt: str) -> Dict[str, any]:
    """Simulate what an AI vision model would see in the image"""
    import asyncio
    await asyncio.sleep(0.5)  # Simulate API call time
    
    # Simulate vision analysis results
    prompt_lower = prompt.lower()
    
    # Analyze apparent size/power from prompt keywords
    size_indicators = {
        "tiny": 0.3, "small": 0.5, "young": 0.6, "medium": 0.7,
        "large": 1.2, "huge": 1.5, "massive": 1.8, "giant": 2.0,
        "ancient": 1.6, "elder": 1.4, "baby": 0.4, "mighty": 1.3
    }
    
    power_multiplier = 1.0
    for indicator, multiplier in size_indicators.items():
        if indicator in prompt_lower:
            power_multiplier = multiplier
            break
    
    # Determine creature type from visual cues (simulated)
    element_keywords = {
        "fire": ["fire", "flame", "lava", "magma", "ember", "phoenix", "dragon"],
        "water": ["water", "ice", "frost", "ocean", "sea", "aquatic", "whale"],
        "earth": ["rock", "stone", "earth", "mountain", "crystal", "gem"],
        "air": ["wind", "storm", "cloud", "lightning", "thunder", "eagle"],
        "dark": ["shadow", "dark", "void", "nightmare", "demon", "evil"],
        "light": ["light", "holy", "angel", "divine", "celestial", "bright"]
    }
    
    detected_element = "Fire"  # default
    for element, keywords in element_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_element = element.title()
            break
    
    # Simulate rarity detection based on visual complexity
    complexity_score = len(prompt.split()) + (2 if any(word in prompt_lower for word in ["legendary", "ancient", "mythical"]) else 0)
    
    return {
        "apparent_power_level": power_multiplier,
        "detected_element": detected_element,
        "complexity_score": complexity_score,
        "creature_characteristics": extract_creature_characteristics(prompt),
        "original_prompt": prompt
    }

def extract_creature_characteristics(prompt: str) -> Dict[str, any]:
    """Extract creature characteristics from prompt for naming and attacks"""
    prompt_lower = prompt.lower()
    
    # Creature type detection
    creature_types = {
        "dragon": ["dragon", "drake", "wyrm"],
        "wolf": ["wolf", "dire wolf", "fenrir"],
        "bird": ["eagle", "phoenix", "hawk", "raven"],
        "beast": ["tiger", "lion", "bear", "panther"],
        "elemental": ["elemental", "spirit", "wisp"],
        "demon": ["demon", "devil", "fiend"],
        "angel": ["angel", "seraph", "cherub"],
        "undead": ["skeleton", "zombie", "lich", "ghost"]
    }
    
    detected_type = "beast"  # default
    for creature_type, keywords in creature_types.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_type = creature_type
            break
    
    # Attack style detection
    combat_styles = []
    if any(word in prompt_lower for word in ["claws", "talons", "sharp"]):
        combat_styles.append("slashing")
    if any(word in prompt_lower for word in ["fire", "flame", "burning"]):
        combat_styles.append("fire")
    if any(word in prompt_lower for word in ["magic", "spell", "enchanted"]):
        combat_styles.append("magic")
    if any(word in prompt_lower for word in ["bite", "teeth", "fangs"]):
        combat_styles.append("biting")
    
    return {
        "creature_type": detected_type,
        "combat_styles": combat_styles or ["physical"],
        "descriptors": [word for word in prompt_lower.split() if len(word) > 4]
    }

def generate_stats_from_analysis(analysis: Dict[str, any]) -> CardMetadata:
    """Generate card stats based on AI vision analysis"""
    
    # Calculate HP with proper distribution (80% under 120)
    power_level = analysis["apparent_power_level"]
    complexity = analysis["complexity_score"]
    
    # Base HP calculation with weighted distribution
    if random.random() < 0.8:  # 80% of cards
        base_hp = random.randint(40, 100)  # Lower range
    else:  # 20% of cards
        base_hp = random.randint(100, 150)  # Higher range
    
    # Apply power multiplier
    final_hp = max(20, min(150, int(base_hp * power_level)))
    
    # Determine rarity based on complexity and power
    rarity = "Common"
    rarity_score = complexity + (power_level * 2)
    if rarity_score >= 12:
        rarity = "Legendary"
    elif rarity_score >= 9:
        rarity = "Epic"  
    elif rarity_score >= 6:
        rarity = "Rare"
    elif rarity_score >= 4:
        rarity = "Uncommon"
    
    # Generate creature name based on characteristics
    name = generate_creature_name(analysis["creature_characteristics"], analysis["detected_element"])
    
    # Generate attacks based on analysis
    attacks = generate_contextual_attacks(
        analysis["creature_characteristics"],
        analysis["detected_element"], 
        final_hp,
        rarity
    )
    
    # Generate flavor text
    flavor_text = generate_flavor_text(analysis["creature_characteristics"], analysis["original_prompt"])
    
    return CardMetadata(
        name=name,
        hp=final_hp,
        type=analysis["detected_element"],
        rarity=rarity,
        flavorText=flavor_text,
        attacks=attacks
    )

def generate_creature_name(characteristics: Dict[str, any], element: str) -> str:
    """Generate contextual creature name"""
    
    creature_type = characteristics["creature_type"]
    descriptors = characteristics.get("descriptors", [])
    
    # Element prefixes
    element_prefixes = {
        "Fire": ["Flame", "Ember", "Blaze", "Inferno", "Cinder"],
        "Water": ["Frost", "Ice", "Wave", "Tide", "Storm"], 
        "Earth": ["Stone", "Rock", "Crystal", "Granite", "Iron"],
        "Air": ["Wind", "Storm", "Thunder", "Lightning", "Gale"],
        "Dark": ["Shadow", "Void", "Night", "Dread", "Gloom"],
        "Light": ["Dawn", "Radiant", "Celestial", "Divine", "Bright"]
    }
    
    # Creature suffixes based on type
    type_suffixes = {
        "dragon": ["drake", "wyrm", "wing", "scale", "claw"],
        "wolf": ["fang", "howl", "pack", "moon", "wild"],
        "bird": ["wing", "talon", "soar", "sky", "flight"],
        "beast": ["claw", "roar", "hunt", "prowl", "fierce"],
        "elemental": ["spirit", "essence", "force", "energy", "core"],
        "demon": ["spawn", "fiend", "terror", "doom", "bane"],
        "angel": ["wing", "light", "grace", "holy", "divine"],
        "undead": ["bone", "soul", "wraith", "specter", "shade"]
    }
    
    prefix = random.choice(element_prefixes.get(element, ["Ancient"]))
    suffix = random.choice(type_suffixes.get(creature_type, ["beast"]))
    
    return f"{prefix}{suffix}"

def generate_contextual_attacks(characteristics: Dict[str, any], element: str, hp: int, rarity: str) -> List[Attack]:
    """Generate attacks that make sense for the creature"""
    
    creature_type = characteristics["creature_type"]
    combat_styles = characteristics["combat_styles"]
    
    # Attack templates by element and style
    attack_templates = {
        "Fire": {
            "slashing": [("Flame Claw", 35, "Slashes with burning claws")],
            "fire": [("Inferno Blast", 45, "Unleashes a torrent of flames")],
            "magic": [("Fire Storm", 40, "Conjures a magical fire storm")],
            "biting": [("Ember Bite", 30, "Bites with flame-wreathed fangs")]
        },
        "Water": {
            "slashing": [("Ice Claw", 32, "Strikes with frozen talons")],
            "fire": [("Steam Burst", 38, "Superheated water explosion")], 
            "magic": [("Tidal Wave", 42, "Summons a crushing wave")],
            "biting": [("Frost Bite", 28, "Freezing bite that slows enemies")]
        },
        "Earth": {
            "slashing": [("Stone Claw", 38, "Cuts with razor-sharp stone")],
            "magic": [("Earthquake", 50, "Shakes the ground violently")],
            "physical": [("Boulder Throw", 45, "Hurls massive rocks")]
        },
        "Air": {
            "slashing": [("Wind Blade", 35, "Cuts with compressed air")],
            "magic": [("Lightning Strike", 48, "Calls down electric fury")],
            "physical": [("Gust Slam", 40, "Powerful wind attack")]
        },
        "Dark": {
            "slashing": [("Shadow Claw", 36, "Strikes from darkness")],
            "magic": [("Void Drain", 25, "Drains life force from enemy")],
            "physical": [("Terror Strike", 42, "Frightening physical assault")]
        },
        "Light": {
            "slashing": [("Radiant Slash", 38, "Cuts with holy light")],
            "magic": [("Divine Ray", 44, "Blasts with pure light")],
            "physical": [("Blessing Strike", 35, "Heals self while attacking")]
        }
    }
    
    # Defensive/utility attacks
    utility_attacks = {
        "heal": ("Regenerate", 0, f"Restores {hp//5} HP"),
        "shield": ("Fortify", 0, "Reduces next attack by 50%"),
        "buff": ("Power Up", 0, "Next attack deals double damage")
    }
    
    # Generate 2 attacks
    attacks = []
    
    # Primary attack based on combat style
    primary_style = combat_styles[0] if combat_styles else "physical"
    element_attacks = attack_templates.get(element, attack_templates["Fire"])
    style_attacks = element_attacks.get(primary_style, element_attacks.get("physical", [("Strike", 30, "Basic attack")]))
    
    if style_attacks:
        attack_name, base_damage, description = random.choice(style_attacks)
        # Scale damage based on rarity and HP
        damage_multiplier = {"Common": 0.9, "Uncommon": 1.0, "Rare": 1.1, "Epic": 1.2, "Legendary": 1.3}[rarity]
        final_damage = max(15, int(base_damage * damage_multiplier))
        attacks.append(Attack(name=attack_name, damage=final_damage, description=description))
    
    # Secondary attack (mix of offensive and utility)
    if random.random() < 0.7:  # 70% chance for second offensive attack
        secondary_styles = [s for s in combat_styles[1:]] if len(combat_styles) > 1 else ["magic"]
        if secondary_styles:
            secondary_style = secondary_styles[0]
            secondary_attacks = element_attacks.get(secondary_style, style_attacks)
            if secondary_attacks:
                attack_name, base_damage, description = random.choice(secondary_attacks)
                final_damage = max(10, int(base_damage * damage_multiplier * 0.8))  # Slightly weaker
                attacks.append(Attack(name=attack_name, damage=final_damage, description=description))
    else:  # 30% chance for utility attack
        utility_type = random.choice(list(utility_attacks.keys()))
        attack_name, damage, description = utility_attacks[utility_type]
        attacks.append(Attack(name=attack_name, damage=damage, description=description))
    
    # Ensure we have 2 attacks
    if len(attacks) < 2:
        attacks.append(Attack(name="Basic Strike", damage=25, description="A simple but effective attack"))
    
    return attacks[:2]  # Limit to 2 attacks

def generate_flavor_text(characteristics: Dict[str, any], original_prompt: str) -> str:
    """Generate contextual flavor text"""
    
    creature_type = characteristics["creature_type"]
    
    flavor_templates = {
        "dragon": [
            "Ancient and wise, this dragon commands respect from all who encounter it.",
            "Born from the heart of a volcano, its rage burns eternal.",
            "Legends speak of its hoard hidden deep in mountain caves."
        ],
        "wolf": [
            "A lone hunter that stalks its prey through moonlit forests.",
            "Leader of the pack, feared by all woodland creatures.",
            "Its howl echoes through the night, calling its kin to hunt."
        ],
        "bird": [
            "Soaring high above the clouds, it surveys its domain below.",
            "Its keen eyes miss nothing as it patrols the skies.",
            "Graceful in flight, deadly when it strikes."
        ],
        "beast": [
            "A fierce predator that rules its territory with strength.",
            "Its roar can be heard for miles, warning others to stay away.",
            "Perfectly adapted to survive in the harshest conditions."
        ],
        "elemental": [
            "A manifestation of pure elemental energy given form.",
            "It exists between the physical and spiritual realms.",
            "Ancient magic binds this creature to the natural world."
        ]
    }
    
    templates = flavor_templates.get(creature_type, flavor_templates["beast"])
    return random.choice(templates)

def generate_card_metadata(prompt: str) -> CardMetadata:
    """Legacy function - now just calls the async version synchronously for backwards compatibility"""
    # This would normally be replaced by the async vision analysis
    # For now, using simplified generation
    import asyncio
    
    # Create a simple analysis without actual image
    fake_analysis = {
        "apparent_power_level": random.uniform(0.7, 1.3),
        "detected_element": "Fire",
        "complexity_score": len(prompt.split()),
        "creature_characteristics": extract_creature_characteristics(prompt),
        "original_prompt": prompt
    }
    
    return generate_stats_from_analysis(fake_analysis)

@app.get("/")
async def root():
    return {"message": "Trading Card Generator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/generate", response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest):
    """Generate an AI image for a trading card with AI-analyzed stats"""
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Simulate generation time
    generation_start = time.time()
    
    # Step 1: Get available placeholder images
    available_images = get_placeholder_images()
    if not available_images:
        available_images = FALLBACK_IMAGES
        logger.warning("No local images found, using fallback images")
    
    # Select random image
    await simulate_processing_time(2.0, 4.0)  # Simulate AI image generation time
    image_url = random.choice(available_images)
    
    # Step 2: Analyze the generated image with AI vision to create stats
    # This simulates calling GPT-4 Vision or similar to "look at" the generated image
    logger.info(f"Analyzing generated image for: {request.prompt[:50]}...")
    metadata = await analyze_image_and_generate_stats(image_url, request.prompt)
    
    generation_time = time.time() - generation_start
    
    logger.info(f"Generated card: {metadata.name} ({metadata.type}) - HP: {metadata.hp} - Rarity: {metadata.rarity}")
    
    return GenerateImageResponse(
        image_url=image_url,
        metadata=metadata,
        generation_time=generation_time
    )

@app.post("/upload-placeholder")
async def upload_placeholder_image(file: UploadFile = File(...)):
    """Upload a placeholder image for testing"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    image_url = f"http://localhost:8000/static/images/{file.filename}"
    
    return {
        "message": "Image uploaded successfully",
        "image_url": image_url,
        "filename": file.filename
    }

@app.get("/placeholder-images")
async def list_placeholder_images():
    """List all available placeholder images"""
    images = get_placeholder_images()
    return {
        "images": images,
        "count": len(images),
        "message": "Available placeholder images"
    }

@app.post("/cards/export")
async def export_card(request: CardExportRequest):
    """Generate a high-resolution export of the card"""
    # This would generate a high-res PNG/PDF in the real implementation
    # For now, just return the existing image URL
    await simulate_processing_time(0.5, 1.0)
    
    return {
        "export_url": request.image_url,
        "format": "png",
        "resolution": "1200x1600",
        "message": "Card exported successfully"
    }

@app.post("/cards/save")
async def save_card(request: SaveCardRequest):
    """Save a user-created card to the database"""
    # This would save to a database in the real implementation
    await simulate_processing_time(0.2, 0.5)
    
    card_id = f"card_{int(time.time())}"
    
    return {
        "card_id": card_id,
        "message": "Card saved successfully",
        "timestamp": time.time()
    }

@app.get("/cards/{card_id}")
async def get_card(card_id: str):
    """Retrieve a saved card by ID"""
    # This would fetch from database in real implementation
    return {
        "card_id": card_id,
        "message": "Card retrieval not yet implemented",
        "status": "stub"
    }

@app.get("/models/status")
async def get_model_status():
    """Check the status of the AI image generation model"""
    return {
        "model": "stable-diffusion-v1.5",
        "status": "stubbed",
        "queue_length": 0,
        "average_generation_time": 5.2,
        "message": "AI model integration pending"
    }

async def simulate_processing_time(min_time: float = 1.0, max_time: float = 3.0):
    """Simulate realistic processing time"""
    import asyncio
    wait_time = random.uniform(min_time, max_time)
    await asyncio.sleep(wait_time)

# Future endpoints for when AI integration is complete:
"""
@app.post("/generate-real")
async def generate_image_real(request: GenerateImageRequest):
    # This will call your Stable Diffusion service
    # 1. Send prompt to AI service
    # 2. Wait for image generation
    # 3. Upload to Cloudinary/S3
    # 4. Return hosted URL + metadata
    pass

@app.post("/batch-generate")
async def batch_generate(prompts: List[str]):
    # Generate multiple images in batch
    pass
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
