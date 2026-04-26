from __future__ import annotations

import csv
import io
import json
import re
import textwrap
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MODS_DIR = ROOT / "mods"
OUT_DIR = ROOT / "notes" / "mod_thumbnail_cards"
CARDS_DIR = OUT_DIR / "cards"
SHEETS_DIR = OUT_DIR / "category_sheets"


THEME = {
    "Core Progression": ("#4C6FFF", "#EAF0FF"),
    "Skyblock Foundation": ("#2B9ED8", "#E7F7FF"),
    "Systems & Automation": ("#60707B", "#EEF3F5"),
    "Grounding & Routine": ("#4F9D68", "#ECF8EF"),
    "Magic & Intuition": ("#8B5CF6", "#F3EEFF"),
    "Challenge & Chaos": ("#B23A48", "#FFF0F1"),
    "Exploration & Movement": ("#D1872A", "#FFF5E8"),
    "Quality of Life": ("#2F7D75", "#EAF8F6"),
    "Inventory & Load Management": ("#7E6A4D", "#F6F1E8"),
    "Comfort & Expression": ("#C25C8A", "#FFF0F7"),
    "Performance & Optimization": ("#59636E", "#F2F4F6"),
    "Libraries & Dependencies": ("#5E6AD2", "#F0F1FF"),
}


ENTRIES = [
    ("Core Progression", "FTB Quests", "Quest book framework for chapters, tasks, rewards, dependencies, and party progression.", "Make it the emotional spine: diagnosis, routines, rebuilding, duality, and ascension chapters that teach the pack gently.", ["ftb-quests"]),
    ("Core Progression", "FTB Teams", "Team system that lets players share progress and ownership.", "Tie skyblock islands, quest progress, and shared base milestones to a chosen support network instead of a solo grind.", ["ftb-teams"]),
    ("Core Progression", "FTB Essentials", "Server and utility commands for homes, warps, nicknames, and quality server management.", "Use homes/warps as safe return rituals so players can explore intensity without losing their center.", ["ftb-essentials"]),
    ("Core Progression", "Quest Kill Task", "Adds kill-count tasks for FTB Quests.", "Turn combat into contained challenge gates, with clear boss or mob tasks instead of vague danger spikes.", ["Quest Kill Task"]),
    ("Core Progression", "Starter Kit", "Gives configured starter items on first join.", "Deliver the first comfort objects and practical tools as a deliberate landing ritual before the void opens up.", ["starterkit"]),

    ("Skyblock Foundation", "Skyblock Builder", "Creates the skyblock start flow, island templates, spawn behavior, and team islands.", "Keep this as the literal rebirth system: chakra islands, safe spawn, starter routing, and controlled first steps.", ["SkyblockBuilder"]),
    ("Skyblock Foundation", "Skyblock Resources", "Adds resource progression designed for skyblock play.", "Use it to replace missing overworld loops with intentional, quest-taught resource routines.", ["skyblock_resources"]),
    ("Skyblock Foundation", "Sky Islands", "Adds floating island content and sky exploration targets.", "Let nearby islands represent reachable pieces of self: small, themed recoveries rather than endless terrain.", ["sky_isles"]),
    ("Skyblock Foundation", "Skylands", "Adds skyland terrain or support for skyland-style worlds.", "Use it for larger transitional spaces once the player has learned how to survive the first platform.", ["SkyLands", "skylands"]),
    ("Skyblock Foundation", "Sky Structures", "Adds premade sky structures to discover.", "Place structure discoveries as confidence checks after early routine quests.", ["Sky Structures"]),
    ("Skyblock Foundation", "Sky Villages", "Adds villages or village-like life to sky worlds.", "Make social spaces optional sanctuaries where players trade, recover, and gather direction.", ["SkyVillages"]),
    ("Skyblock Foundation", "Feur Skyland", "Adds themed skyland content for floating-world exploration.", "Use it as a midgame discovery layer after the first islands stop feeling impossible.", ["feur_skyland"]),
    ("Skyblock Foundation", "Skyfall", "Adds skyblock-focused progression and rewards.", "Use drops or events as measured interruptions: novelty without overwhelming the starting routine.", ["skyfall-"]),
    ("Skyblock Foundation", "Skyfall Crates", "Adds crate-style rewards for Skyfall.", "Reserve crates for celebratory quest rewards, not core progression, so the pack stays predictable.", ["skyfall_crates"]),
    ("Skyblock Foundation", "SkyGUIs", "Adds GUIs for skyblock workflows.", "Use it to reduce friction around island choices, teams, and skyblock management.", ["SkyGUIs"]),
    ("Skyblock Foundation", "CobbleGen Randomizer", "Randomizes or expands cobblestone generator outputs.", "Make the first generator a regulated resource engine that grows from basic stone into modded possibility.", ["cobblegenrandomizer"]),

    ("Systems & Automation", "Applied Energistics 2", "Digital storage, autocrafting, channels, networks, and spatially organized logistics.", "Frame AE2 as externalized memory: naming, storing, retrieving, and automating what the player cannot hold in working memory.", ["appliedenergistics2"]),
    ("Systems & Automation", "AE2 Addons", "Addon set for AE2 cooking, Mekanism, Botania, and utility integration.", "Let addons bridge special interests into one organized system without forcing the player to abandon their preferred branch.", ["AE2-Things", "applied-botanics", "Applied-Mekanistics", "appliedcooking"]),
    ("Systems & Automation", "Mekanism", "Large tech progression with machines, gases, ore processing, and high-end production chains.", "Use it as the structured systems branch: stepwise upgrades, clean processing lines, and big satisfying machines.", ["Mekanism-"]),
    ("Systems & Automation", "Mekanism Generators", "Power generation for Mekanism systems.", "Make power a visible regulation loop: fuel, buffer, output, and recovery.", ["MekanismGenerators"]),
    ("Systems & Automation", "Mekanism Tools", "Tools and armor that pair with Mekanism progression.", "Reward steady tech milestones with practical gear upgrades rather than random power jumps.", ["MekanismTools"]),
    ("Systems & Automation", "Mekanism Weapons", "Combat gear extension for Mekanism.", "Use as a late challenge-prep route for players who prefer engineered safety.", ["MekanismWeapons"]),
    ("Systems & Automation", "Thermal Series", "Thermal Foundation, Cultivation, Innovation, and related machinery/resources.", "Use Thermal as the calm workshop branch: understandable machines, farming support, and low-drama automation.", ["thermal_"]),
    ("Systems & Automation", "Ender IO", "Conduits, machines, and compact tech logistics.", "Make it the tidy-base option for players who want clean routing and hidden complexity.", ["EnderIO"]),
    ("Systems & Automation", "Industrial Foregoing", "Automation for farming, mobs, resources, and machines.", "Use it to turn repetitive chores into reliable routines once the player proves the manual loop.", ["industrial-foregoing"]),
    ("Systems & Automation", "Powah", "Power generation, storage, and wireless energy progression.", "Let Powah become the approachable energy ladder before extreme reactors and deep automation.", ["Powah"]),
    ("Systems & Automation", "Flux Networks", "Wireless energy transfer and storage.", "Use it to reduce cable stress and support distant sky islands without visual clutter.", ["FluxNetworks"]),
    ("Systems & Automation", "LaserIO", "Compact item/fluid/energy routing with laser nodes.", "Present LaserIO as precise executive-function wiring: small nodes, clear filters, big relief.", ["laserio"]),
    ("Systems & Automation", "Extreme Reactors", "Large multiblock reactors and turbines.", "Make it a late-game commitment quest about building a stable core instead of chasing constant emergency power.", ["ExtremeReactors"]),

    ("Grounding & Routine", "Cooking for Blockheads", "Kitchen blocks, cooking interfaces, and food management.", "Use kitchens as comfort hubs: routine meals, buffs, and a softer reason to care for the base.", ["cookingforblockheads"]),
    ("Grounding & Routine", "Bonsai Trees", "Compact tree growing and harvesting.", "Make early wood production feel dependable: one tiny tree, one repeatable promise.", ["BonsaiTrees"]),
    ("Grounding & Routine", "Botany Pots", "Potted crop automation and compact farming.", "Use pots for low-pressure routines that produce food, dye, and resources without sprawling farms.", ["BotanyPots"]),
    ("Grounding & Routine", "Botany Trees", "Tree support for Botany Pots.", "Give players quiet, compact orchards that fit skyblock bases.", ["BotanyTrees"]),
    ("Grounding & Routine", "Productive Bees", "Bee breeding and resource production.", "Make bees a curiosity branch: gentle observation, patience, genetics, and resource growth.", ["productivebees"]),
    ("Grounding & Routine", "Productive Trees", "Tree breeding and resource trees.", "Use tree breeding as a slow progress loop for players who enjoy nurturing systems.", ["productivetrees"]),
    ("Grounding & Routine", "Mystical Agriculture", "Resource crops and essence-based crafting.", "Frame essence farming as grounding repetition: tend, harvest, upgrade, breathe.", ["MysticalAgriculture"]),
    ("Grounding & Routine", "Mystical Agriculture Addons", "Additions and customization for Mystical Agriculture.", "Use addons for optional specialization after the basic farm loop feels safe.", ["MysticalAgradditions", "MysticalCustomization", "MysticalExpansion", "Mystical-Garden"]),
    ("Grounding & Routine", "Ceramics", "Clay barrels, tanks, channels, and early utility blocks.", "Use clay tech as the tactile first craft: simple materials, useful containment, visible progress.", ["Ceramics"]),
    ("Grounding & Routine", "Hearth & Home", "Cozy building, home, and decor additions.", "Make homebuilding an actual progression reward, not just cosmetics after the work is done.", ["hearth_and_home"]),
    ("Grounding & Routine", "Stardew Fishing", "Fishing mechanics inspired by cozy life-sim rhythms.", "Use fishing as a regulation minigame: pause the rush, gather food, and let the base breathe.", ["stardew_fishing"]),

    ("Magic & Intuition", "Botania", "Mana-based natural magic built around flowers, automation, and elegant systems.", "Use Botania as nonlinear engineering: beauty, pattern recognition, and automation through living systems.", ["Botania-"]),
    ("Magic & Intuition", "Botania Addons", "Additional Botania tools, machines, and cross-mod integrations.", "Let addon quests become optional deep-focus routes for players who fall in love with mana logic.", ["BotanicAdditions", "BotanicalMachinery", "aiotbotania"]),
    ("Magic & Intuition", "Ars Nouveau", "Spellcrafting, magical automation, familiars, and glyph-based progression.", "Use glyph discovery as language acquisition: naming needs, shaping tools, and building agency.", ["ars_nouveau"]),
    ("Magic & Intuition", "Blood Magic", "Ritual magic, sacrifice, will, and altar progression.", "Handle as a consent-and-cost branch: power that asks what the player is willing to spend and why.", ["bloodmagic"]),
    ("Magic & Intuition", "Malum", "Soul magic, spirits, runework, and occult progression.", "Use Malum for shadow-work quests about integrating difficult feelings instead of banishing them.", ["malum"]),
    ("Magic & Intuition", "Thaumon", "Thaumcraft-inspired magical research and discovery.", "Make it the wonder/research branch: curiosity, notes, experiments, and strange new categories.", ["thaumon"]),
    ("Magic & Intuition", "Relics", "Powerful discoverable artifacts and curios.", "Use relics sparingly as identity objects: tools the player earns by becoming more themselves.", ["relics"]),
    ("Magic & Intuition", "Apotheosis", "Bosses, affixes, spawners, enchantment expansion, and progression loot.", "Use it to turn gear growth into readable milestones while keeping difficulty spikes quest-gated.", ["Apotheosis"]),

    ("Challenge & Chaos", "Born in Chaos", "Hostile mobs, encounters, and danger-focused content.", "Use as controlled overwhelm: opt-in combat chapters that teach preparation and exits.", ["born_in_chaos"]),
    ("Challenge & Chaos", "L_Ender's Cataclysm", "Large bosses, dungeons, and high-pressure combat encounters.", "Make each boss a named threshold, with preparation quests before the fight and recovery after.", ["L_Enders_Cataclysm"]),
    ("Challenge & Chaos", "Infernal Mobs", "Randomly empowered mobs with special modifiers.", "Use carefully so chaos feels like texture, not punishment; pair with better rewards and escape tools.", ["infernalmobs"]),
    ("Challenge & Chaos", "Mutant Monsters", "Stronger mutant versions of familiar mobs.", "Use as recognizable fear made bigger: clear, dramatic, and mechanically legible.", ["MutantMonsters"]),
    ("Challenge & Chaos", "Dungeon Crawl", "Generated dungeons for exploration and combat.", "Make dungeon entry a preparedness milestone, not an early accident.", ["Dungeon Crawl"]),
    ("Challenge & Chaos", "When Dungeons Arise", "Large structures and adventure dungeons.", "Use as major sky/land expedition targets with Waystone return routes.", ["DungeonsArise"]),
    ("Challenge & Chaos", "Gateways to Eternity", "Wave-based gateway fights and mob arenas.", "Use gateways as contained pressure sessions with clear starts, endings, and rewards.", ["GatewaysToEternity"]),
    ("Challenge & Chaos", "Alex's Mobs", "Adds many animals and creatures with unique behavior and drops.", "Use it to make the world feel alive, with quests that notice ecology instead of only loot.", ["alexsmobs"]),
    ("Challenge & Chaos", "Creeper Overhaul", "Biome-themed creeper variants.", "Use variants as environmental awareness lessons, with sensory-safe warning and prep quests.", ["creeperoverhaul"]),

    ("Exploration & Movement", "Waystones", "Teleportation stones for travel networks.", "Make waystones the pack's chosen-route system: name places, return safely, and reduce travel fatigue.", ["waystones"]),
    ("Exploration & Movement", "Twilight Forest", "A full adventure dimension with bosses, biomes, and progression.", "Use it as a mythic chapter after the base is stable: the inner forest beyond survival.", ["twilightforest"]),
    ("Exploration & Movement", "Paraglider", "Stamina-based gliding and movement tools.", "Give the void a gentler relationship: falling becomes navigation once the player earns it.", ["Paraglider"]),

    ("Quality of Life", "JEI", "Recipe and usage viewer for items, fluids, and crafting systems.", "Make JEI a quest-taught research tool: search, bookmark, compare, and reduce uncertainty.", ["jei-"]),
    ("Quality of Life", "Jade", "In-world information overlay for blocks, entities, fluids, and machines.", "Use Jade as environmental literacy: the world tells the player what they are looking at.", ["Jade"]),
    ("Quality of Life", "Mouse Tweaks", "Inventory drag and click improvements.", "Keep repetitive inventory actions lighter so the pack's complexity costs less energy.", ["MouseTweaks"]),
    ("Quality of Life", "Controlling", "Keybind search and conflict management.", "Point players here early so modded controls do not become an invisible wall.", ["Controlling"]),
    ("Quality of Life", "Inventory HUD", "HUD overlays for inventory, armor, and effects.", "Use as optional self-monitoring for players who like visible state and fewer surprises.", ["inventoryhud"]),
    ("Quality of Life", "Item Zoom", "Lets players inspect item models closely.", "Support delight and recognition: inspect artifacts, plushies, tools, and strange items.", ["itemzoom"]),
    ("Quality of Life", "Searchables", "Search support library used by UI mods.", "Treat as behind-the-scenes cognitive load reduction for menus and keybinds.", ["Searchables"]),

    ("Inventory & Load Management", "Cloud Storage", "Portable/cloud-like storage with item management.", "Use as a midgame relief valve when inventories start feeling impossible to hold mentally.", ["cloudstorage"]),
    ("Inventory & Load Management", "Baubley Heart Canisters", "Health upgrades through wearable or crafted canisters.", "Make health growth a body-care arc: sturdier, safer, and earned through preparation.", ["baubley-heart-canisters"]),
    ("Inventory & Load Management", "Inventory Pets", "Collectible pets that grant utilities and playful effects.", "Use as expressive helper companions that soften utility progression.", ["inventorypets"]),

    ("Comfort & Expression", "Plushies", "Collectible plush decorations.", "Use plushies as comfort rewards for emotional milestones and cozy base corners.", ["plushies"]),
    ("Comfort & Expression", "Decorative Blocks", "Decorative building blocks and props.", "Reward base personalization as progress, not procrastination.", ["decorative_blocks"]),
    ("Comfort & Expression", "Night Lights", "Small lighting and ambience blocks.", "Use night lights as sensory-safety objects in early shelters and recovery rooms.", ["nightlights"]),
    ("Comfort & Expression", "Dimensional Paintings", "Paintings or portals with dimensional/visual flair.", "Use as memory walls: visual anchors for places, chapters, and identity shifts.", ["Dimensional-Paintings"]),
    ("Comfort & Expression", "Display Case", "Display blocks for showcasing items.", "Let players preserve milestones physically: first tool, first relic, first hard-won trophy.", ["Display Case"]),
    ("Comfort & Expression", "Simple Hats", "Cosmetic hats and wearable expression.", "Use hats as low-stakes identity play and celebration rewards.", ["simplehats"]),

    ("Performance & Optimization", "Embeddium", "Rendering performance optimization for Forge.", "Keep the pack more comfortable for lower-end systems and reduce visual strain from lag.", ["embeddium"]),
    ("Performance & Optimization", "Oculus", "Shader support for Forge.", "Offer optional beauty while keeping shaders out of required progression.", ["oculus"]),
    ("Performance & Optimization", "FerriteCore", "Memory usage optimization.", "Quietly improves stability so large mod systems feel less fragile.", ["ferritecore"]),
    ("Performance & Optimization", "ModernFix", "Performance, loading, and memory fixes.", "Use as a baseline stability layer for a large, emotionally dense pack.", ["modernfix"]),
    ("Performance & Optimization", "Clumps", "Combines XP orbs to reduce lag.", "Make XP collection less noisy and less performance-heavy after farms or fights.", ["Clumps"]),
    ("Performance & Optimization", "Toast Control", "Controls pop-up toast notifications.", "Reduce sensory interruption by limiting noisy notifications during play.", ["ToastControl"]),

    ("Libraries & Dependencies", "Architectury", "Cross-loader API library used by many mods.", "Keep documented as a required backend piece, not player-facing progression.", ["architectury"]),
    ("Libraries & Dependencies", "Curios", "Accessory slot API for trinkets, relics, and wearable upgrades.", "Use as the equipment backbone for identity objects and practical supports.", ["curios"]),
    ("Libraries & Dependencies", "GeckoLib", "Animation library for entity and item animations.", "Supports animated mobs, magic, and expressive mod content behind the scenes.", ["geckolib"]),
    ("Libraries & Dependencies", "Bookshelf", "Shared library for mod features and utilities.", "Document as part of the pack's dependency base so updates stay understandable.", ["Bookshelf"]),
    ("Libraries & Dependencies", "Placebo", "Library required by Apotheosis and related mods.", "Keep tied to Apotheosis in maintenance notes so updates are not separated accidentally.", ["Placebo"]),
    ("Libraries & Dependencies", "Balm", "Shared library used by BlayTheNinth mods such as Cooking for Blockheads.", "Supports comfort/routine mods quietly in the background.", ["balm"]),
    ("Libraries & Dependencies", "LibX", "Library for mods that need common helper systems.", "Track as backend plumbing, especially around Botania-adjacent mods.", ["LibX"]),
    ("Libraries & Dependencies", "ResourcefulLib", "Library used by several modern mods for assets and common utilities.", "Keep as shared infrastructure for UI/data-heavy mods.", ["resourcefullib"]),
    ("Libraries & Dependencies", "Citadel", "Library powering Alex's Mobs and other entity-heavy mods.", "Track with creature and challenge content so dependency updates stay paired.", ["citadel"]),
    ("Libraries & Dependencies", "Patchouli", "In-game guidebook framework.", "Use for future written lore, chapter guides, and gentle explanations outside FTB Quests.", ["Patchouli"]),
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def slug(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return s or "card"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_TITLE = font(40, True)
FONT_SUB = font(23, True)
FONT_BODY = font(22)
FONT_SMALL = font(17)
FONT_TINY = font(14)


def load_jar_info() -> list[dict]:
    infos = []
    for jar in sorted(MODS_DIR.glob("*.jar")):
        info = {"jar": jar, "name": jar.stem, "modid": "", "description": "", "logo": None}
        try:
            with zipfile.ZipFile(jar) as zf:
                names = zf.namelist()
                tomls = [n for n in names if n.endswith("META-INF/mods.toml") or n.endswith("META-INF/neoforge.mods.toml")]
                if tomls:
                    text = zf.read(tomls[0]).decode("utf-8", "ignore")
                    m_name = re.search(r"displayName\s*=\s*\"([^\"]+)\"", text)
                    m_id = re.search(r"modId\s*=\s*\"([^\"]+)\"", text)
                    m_desc = re.search(r"description\s*=\s*'''(.*?)'''", text, re.S) or re.search(r"description\s*=\s*\"([^\"]+)\"", text, re.S)
                    m_logo = re.search(r"logoFile\s*=\s*\"([^\"]+)\"", text)
                    if m_name:
                        info["name"] = m_name.group(1).strip()
                    if m_id:
                        info["modid"] = m_id.group(1).strip()
                    if m_desc:
                        info["description"] = " ".join(m_desc.group(1).split())
                    if m_logo:
                        info["logo"] = extract_image(zf, m_logo.group(1), names)
                if info["logo"] is None:
                    for pattern in ("logo", "icon"):
                        found = next((n for n in names if pattern in n.lower() and n.lower().endswith(".png")), None)
                        if found:
                            info["logo"] = extract_image(zf, found, names)
                            break
        except Exception:
            pass
        info["search"] = normalize(" ".join([jar.name, info["name"], info["modid"]]))
        infos.append(info)
    return infos


def extract_image(zf: zipfile.ZipFile, requested: str, names: list[str]) -> Image.Image | None:
    variants = [requested, requested.lstrip("/"), f"assets/{requested.lstrip('/')}"]
    variants += [n for n in names if n.lower().endswith(requested.lower().lstrip("/"))]
    for item in variants:
        if item in names and item.lower().endswith(".png"):
            try:
                return Image.open(io.BytesIO(zf.read(item))).convert("RGBA")
            except Exception:
                return None
    return None


def find_match(infos: list[dict], keywords: list[str]) -> dict | None:
    for keyword in keywords:
        key = normalize(keyword)
        for info in infos:
            if key and key in info["search"]:
                return info
    return None


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, fnt, fill: str, line_spacing: int = 6) -> int:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), line, font=fnt)[3] + line_spacing
    return y


def make_fallback_icon(title: str, color: str) -> Image.Image:
    img = Image.new("RGBA", (180, 180), color)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, 179, 179), radius=34, fill=color)
    letters = "".join(part[0] for part in re.findall(r"[A-Za-z0-9]+", title)[:2]).upper() or "M"
    f = font(68, True)
    box = draw.textbbox((0, 0), letters, font=f)
    draw.text(((180 - (box[2] - box[0])) / 2, (180 - (box[3] - box[1])) / 2 - 6), letters, font=f, fill="#FFFFFF")
    return img


def fit_icon(icon: Image.Image, color: str) -> Image.Image:
    canvas = Image.new("RGBA", (190, 190), (255, 255, 255, 0))
    icon = ImageOps.contain(icon.convert("RGBA"), (150, 150))
    bg = Image.new("RGBA", (180, 180), "#FFFFFF")
    mask = Image.new("L", (180, 180), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 179, 179), radius=32, fill=255)
    bg.putalpha(mask)
    canvas.alpha_composite(bg, (5, 5))
    canvas.alpha_composite(icon, (5 + (180 - icon.width) // 2, 5 + (180 - icon.height) // 2))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((5, 5, 184, 184), radius=32, outline=color, width=4)
    return canvas


def make_card(entry: tuple, info: dict | None, index: int) -> dict:
    category, title, desc, integration, keywords = entry
    color, pale = THEME[category]
    img = Image.new("RGB", (1200, 675), "#F9FAF7")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1200, 675), fill=pale)
    draw.rectangle((0, 0, 1200, 96), fill=color)
    draw.rectangle((0, 96, 28, 675), fill=color)
    draw.text((42, 26), category.upper(), font=FONT_SUB, fill="#FFFFFF")
    draw.text((42, 128), title, font=FONT_TITLE, fill="#1F2933")
    icon = (info or {}).get("logo") or make_fallback_icon(title, color)
    icon = fit_icon(icon, color)
    img.paste(icon, (56, 220), icon)
    source = "Installed jar: " + info["jar"].name if info else "No exact installed jar matched; visual placeholder used."
    draw_wrapped(draw, source, (52, 430), 235, FONT_TINY, "#47515A", 3)
    draw.text((330, 216), "What it does", font=FONT_SUB, fill=color)
    y = draw_wrapped(draw, desc, (330, 254), 790, FONT_BODY, "#1F2933", 8)
    draw.text((330, max(y + 24, 365)), "AuADHD integration idea", font=FONT_SUB, fill=color)
    draw_wrapped(draw, integration, (330, max(y + 62, 403)), 790, FONT_BODY, "#1F2933", 8)
    draw.text((1095, 627), f"{index:02d}", font=FONT_SMALL, fill="#66727C")
    filename = f"{index:02d}-{slug(category)}-{slug(title)}.png"
    path = CARDS_DIR / filename
    img.save(path)
    return {
        "category": category,
        "mod": title,
        "description": desc,
        "integration": integration,
        "png": path.relative_to(ROOT).as_posix(),
        "matched_jar": info["jar"].name if info else "",
        "matched_name": info["name"] if info else "",
    }


def make_sheets(records: list[dict]) -> None:
    for category in THEME:
        category_records = [r for r in records if r["category"] == category]
        if not category_records:
            continue
        thumbs = []
        for record in category_records:
            card = Image.open(ROOT / record["png"]).convert("RGB")
            thumbs.append(ImageOps.contain(card, (360, 203)))
        cols = 3
        rows = (len(thumbs) + cols - 1) // cols
        color, pale = THEME[category]
        sheet = Image.new("RGB", (cols * 390 + 30, rows * 250 + 120), pale)
        draw = ImageDraw.Draw(sheet)
        draw.rectangle((0, 0, sheet.width, 80), fill=color)
        draw.text((28, 22), category, font=FONT_TITLE, fill="#FFFFFF")
        for i, thumb in enumerate(thumbs):
            x = 30 + (i % cols) * 390
            y = 105 + (i // cols) * 250
            sheet.paste(thumb, (x, y))
            draw.rounded_rectangle((x, y, x + 360, y + 203), radius=8, outline="#C6CED6", width=2)
            draw.text((x, y + 210), category_records[i]["mod"][:42], font=FONT_SMALL, fill="#1F2933")
        sheet.save(SHEETS_DIR / f"{slug(category)}.png")


def write_indexes(records: list[dict]) -> None:
    with (OUT_DIR / "mod_thumbnail_index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "mod", "description", "integration", "png", "matched_jar", "matched_name"])
        writer.writeheader()
        writer.writerows(records)
    (OUT_DIR / "mod_thumbnail_index.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    lines = [
        "# AuADHD Mod Thumbnail Cards",
        "",
        "Generated from the requested progression categories. Each entry has a PNG card, a short mod description, and one possible integration idea for the pack.",
        "",
    ]
    for category in THEME:
        rows = [r for r in records if r["category"] == category]
        if not rows:
            continue
        lines += [f"## {category}", ""]
        sheet = f"category_sheets/{slug(category)}.png"
        lines += [f"![{category}]({sheet})", ""]
        for row in rows:
            lines += [
                f"### {row['mod']}",
                f"- PNG: `{row['png']}`",
                f"- Description: {row['description']}",
                f"- Integration: {row['integration']}",
                f"- Matched jar: `{row['matched_jar'] or 'not matched'}`",
                "",
            ]
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    infos = load_jar_info()
    records = []
    for index, entry in enumerate(ENTRIES, 1):
        records.append(make_card(entry, find_match(infos, entry[4]), index))
    make_sheets(records)
    write_indexes(records)
    print(f"Generated {len(records)} cards in {CARDS_DIR}")
    print(f"Generated {len(list(SHEETS_DIR.glob('*.png')))} category sheets in {SHEETS_DIR}")
    unmatched = [r["mod"] for r in records if not r["matched_jar"]]
    print(f"Unmatched placeholders: {len(unmatched)}")
    if unmatched:
        print(", ".join(unmatched))


if __name__ == "__main__":
    main()
