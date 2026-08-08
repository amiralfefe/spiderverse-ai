from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "graph.json"


UNIVERSES = [
    ("earth-616", "Earth-616", "616", "The primary Marvel Comics continuity."),
    ("earth-1610", "Earth-1610", "1610", "The original Ultimate Marvel continuity."),
    ("earth-65", "Earth-65", "65", "The home universe of Ghost-Spider."),
    ("earth-928", "Earth-928", "928", "The future setting associated with 2099."),
    ("mcu-199999", "Marvel Cinematic Universe", "199999", "The live-action MCU continuity."),
    ("raimi-96283", "Raimi Universe", "96283", "The continuity of the Raimi Spider-Man films."),
    ("webb-120703", "Webb Universe", "120703", "The Amazing Spider-Man film continuity."),
    ("earth-982", "Earth-982", "982", "The MC2 continuity and home of Spider-Girl."),
    ("earth-14512", "Earth-14512", "14512", "The home universe of Peni Parker and SP//dr."),
    ("earth-90214", "Earth-90214", "90214", "The Marvel Noir continuity."),
    ("earth-8311", "Earth-8311", "8311", "The anthropomorphic home of Spider-Ham."),
    ("earth-138", "Earth-138", "138", "The punk-rock home universe of Hobie Brown."),
    ("earth-50101", "Earth-50101", "50101", "The home universe of Pavitr Prabhakar."),
    ("earth-332", "Earth-332", "332", "A Spider-Verse reality represented by Spider-Woman."),
    ("earth-22191", "Earth-22191", "22191", "The virtual reality associated with Spider-Byte."),
    ("earth-833", "Earth-833", "833", "The home universe of Spider-UK."),
    ("earth-51778", "Earth-51778", "51778", "A tokusatsu-inspired Spider-Man reality."),
    ("earth-616b", "Earth-616B", "616B", "The film universe of Peter B. Parker."),
]


CHARACTERS = [
    (
        "peter-616",
        "Peter Parker",
        "earth-616",
        ["Spider-Man"],
        "spider",
        "A science-minded hero balancing responsibility and ordinary life.",
    ),
    (
        "miles-1610",
        "Miles Morales",
        "earth-1610",
        ["Spider-Man"],
        "miles",
        "A young Spider-Man with bio-electric and camouflage abilities.",
    ),
    (
        "gwen-65",
        "Gwen Stacy",
        "earth-65",
        ["Ghost-Spider", "Spider-Woman"],
        "spider",
        "A drummer and web-slinging protector of Earth-65.",
    ),
    (
        "miguel-928",
        "Miguel O'Hara",
        "earth-928",
        ["Spider-Man 2099"],
        "miguel",
        "A geneticist and Spider-Man of the year 2099.",
    ),
    (
        "peter-mcu",
        "Peter Parker",
        "mcu-199999",
        ["Spider-Man"],
        "spider",
        "A young hero active in the Marvel Cinematic Universe.",
    ),
    (
        "peter-raimi",
        "Peter Parker",
        "raimi-96283",
        ["Spider-Man"],
        "spider",
        "The Spider-Man of the Raimi film continuity.",
    ),
    (
        "peter-webb",
        "Peter Parker",
        "webb-120703",
        ["Spider-Man"],
        "spider",
        "The Spider-Man of the Webb film continuity.",
    ),
    (
        "peter-1610",
        "Peter Parker",
        "earth-1610",
        ["Spider-Man"],
        "spider",
        "The original Spider-Man of Earth-1610.",
    ),
    (
        "mayday-982",
        "May Parker",
        "earth-982",
        ["Spider-Girl"],
        "spider",
        "The daughter of Peter and Mary Jane in the MC2 continuity.",
    ),
    (
        "ben-reilly-616",
        "Ben Reilly",
        "earth-616",
        ["Scarlet Spider", "Spider-Man"],
        "spider",
        "A clone of Peter Parker who forged his own heroic identity.",
    ),
    (
        "kaine-616",
        "Kaine Parker",
        "earth-616",
        ["Scarlet Spider"],
        "spider",
        "A clone who became a fierce protector.",
    ),
    (
        "otto-spider-616",
        "Otto Octavius",
        "earth-616",
        ["Superior Spider-Man", "Doctor Octopus"],
        "tech",
        "A brilliant scientist who once operated as the Superior Spider-Man.",
    ),
    (
        "jessica-drew-616",
        "Jessica Drew",
        "earth-616",
        ["Spider-Woman"],
        "bio",
        "A super-powered investigator and Avenger.",
    ),
    (
        "cindy-moon-616",
        "Cindy Moon",
        "earth-616",
        ["Silk"],
        "spider",
        "A web-slinging hero with an exceptionally sensitive spider-sense.",
    ),
    (
        "anya-corazon-616",
        "Anya Corazon",
        "earth-616",
        ["Araña", "Spider-Girl"],
        "spider",
        "A young hero tied to the Spider Society.",
    ),
    (
        "pavitr-50101",
        "Pavitr Prabhakar",
        "earth-50101",
        ["Spider-Man India"],
        "spider",
        "The Spider-Man of Mumbattan.",
    ),
    (
        "peni-14512",
        "Peni Parker",
        "earth-14512",
        ["SP//dr"],
        "pilot",
        "A pilot psychically linked to a spider-powered mech.",
    ),
    (
        "hobie-138",
        "Hobie Brown",
        "earth-138",
        ["Spider-Punk"],
        "spider",
        "A rebellious Spider-Man fighting oppressive systems.",
    ),
    (
        "noir-90214",
        "Peter Parker",
        "earth-90214",
        ["Spider-Man Noir"],
        "spider",
        "A hard-boiled vigilante from a noir reality.",
    ),
    (
        "ham-8311",
        "Peter Porker",
        "earth-8311",
        ["Spider-Ham"],
        "toon",
        "An anthropomorphic spider-hero with cartoon resilience.",
    ),
    (
        "peter-b-616b",
        "Peter B. Parker",
        "earth-616b",
        ["Spider-Man"],
        "spider",
        "An experienced Spider-Man who mentors Miles Morales.",
    ),
    (
        "spider-woman-332",
        "Jessica Drew",
        "earth-332",
        ["Spider-Woman"],
        "spider",
        "A motorcycle-riding Spider-Woman active across the multiverse.",
    ),
    (
        "spider-byte-22191",
        "Margo Kess",
        "earth-22191",
        ["Spider-Byte"],
        "digital",
        "A digital Spider-hero who operates through virtual reality.",
    ),
    (
        "spider-uk-833",
        "Billy Braddock",
        "earth-833",
        ["Spider-UK"],
        "spider",
        "A multiversal protector with Spider-Man abilities.",
    ),
    (
        "takuya-51778",
        "Takuya Yamashiro",
        "earth-51778",
        ["Spider-Man"],
        "tech",
        "A tokusatsu Spider-Man who pilots Leopardon.",
    ),
    (
        "norman-616",
        "Norman Osborn",
        "earth-616",
        ["Green Goblin"],
        "goblin",
        "An industrialist and one of Peter Parker's defining enemies.",
    ),
    (
        "harry-616",
        "Harry Osborn",
        "earth-616",
        ["Green Goblin"],
        "goblin",
        "Peter Parker's friend and Norman Osborn's son.",
    ),
    (
        "mary-jane-616",
        "Mary Jane Watson",
        "earth-616",
        ["MJ"],
        "human",
        "An actor and central member of Peter Parker's family.",
    ),
    (
        "aunt-may-616",
        "May Parker",
        "earth-616",
        ["Aunt May"],
        "human",
        "Peter Parker's aunt and moral anchor.",
    ),
    (
        "jonah-616",
        "J. Jonah Jameson",
        "earth-616",
        ["J.J.J."],
        "human",
        "A publisher famous for his public criticism of Spider-Man.",
    ),
    (
        "daredevil-616",
        "Matt Murdock",
        "earth-616",
        ["Daredevil"],
        "enhanced",
        "A lawyer and street-level vigilante allied with Spider-Man.",
    ),
    (
        "black-cat-616",
        "Felicia Hardy",
        "earth-616",
        ["Black Cat"],
        "enhanced",
        "A skilled thief, adventurer, and complicated ally.",
    ),
    (
        "torch-616",
        "Johnny Storm",
        "earth-616",
        ["Human Torch"],
        "cosmic",
        "A member of the Fantastic Four and Peter Parker's friend.",
    ),
    (
        "venom-616",
        "Eddie Brock",
        "earth-616",
        ["Venom"],
        "symbiote",
        "A journalist bonded to the Venom symbiote.",
    ),
    (
        "carnage-616",
        "Cletus Kasady",
        "earth-616",
        ["Carnage"],
        "symbiote",
        "A violent criminal bonded to the Carnage symbiote.",
    ),
    (
        "doc-ock-616",
        "Otto Octavius",
        "earth-616",
        ["Doctor Octopus"],
        "tech",
        "A scientist who commands four mechanical arms.",
    ),
    (
        "vulture-616",
        "Adrian Toomes",
        "earth-616",
        ["Vulture"],
        "tech",
        "An inventor who uses an advanced flight harness.",
    ),
    (
        "mysterio-616",
        "Quentin Beck",
        "earth-616",
        ["Mysterio"],
        "tech",
        "A special-effects expert who weaponizes illusion.",
    ),
    (
        "electro-616",
        "Max Dillon",
        "earth-616",
        ["Electro"],
        "electric",
        "A superhuman able to generate and manipulate electricity.",
    ),
    (
        "sandman-616",
        "Flint Marko",
        "earth-616",
        ["Sandman"],
        "sand",
        "A shape-shifting criminal whose body behaves like sand.",
    ),
    (
        "kraven-616",
        "Sergei Kravinoff",
        "earth-616",
        ["Kraven the Hunter"],
        "enhanced",
        "A hunter obsessed with proving himself against Spider-Man.",
    ),
    (
        "kingpin-616",
        "Wilson Fisk",
        "earth-616",
        ["Kingpin"],
        "human",
        "A criminal strategist who dominates New York's underworld.",
    ),
    (
        "lizard-616",
        "Curt Connors",
        "earth-616",
        ["Lizard"],
        "lizard",
        "A scientist whose regeneration experiment transformed him.",
    ),
    (
        "rhino-616",
        "Aleksei Sytsevich",
        "earth-616",
        ["Rhino"],
        "strength",
        "A powerful criminal encased in a durable suit.",
    ),
    (
        "scorpion-616",
        "Mac Gargan",
        "earth-616",
        ["Scorpion"],
        "tech",
        "A private investigator transformed into a superhuman adversary.",
    ),
    (
        "shocker-616",
        "Herman Schultz",
        "earth-616",
        ["Shocker"],
        "tech",
        "An engineer who built vibration-projecting gauntlets.",
    ),
    (
        "chameleon-616",
        "Dmitri Smerdyakov",
        "earth-616",
        ["Chameleon"],
        "human",
        "A master of disguise and one of Spider-Man's earliest enemies.",
    ),
    (
        "tombstone-616",
        "Lonnie Lincoln",
        "earth-616",
        ["Tombstone"],
        "strength",
        "A durable enforcer and organized-crime figure.",
    ),
    (
        "morbius-616",
        "Michael Morbius",
        "earth-616",
        ["Morbius"],
        "vampire",
        "A biochemist transformed into a living vampire.",
    ),
    (
        "spot-616",
        "Jonathan Ohnn",
        "earth-616",
        ["Spot"],
        "portal",
        "A scientist able to create interdimensional portals.",
    ),
    (
        "prowler-1610",
        "Aaron Davis",
        "earth-1610",
        ["Prowler"],
        "tech",
        "Miles Morales' uncle and a technologically equipped thief.",
    ),
    (
        "rio-1610",
        "Rio Morales",
        "earth-1610",
        ["Rio"],
        "human",
        "Miles Morales' mother and a healthcare professional.",
    ),
    (
        "jefferson-1610",
        "Jefferson Davis",
        "earth-1610",
        ["Jeff"],
        "human",
        "Miles Morales' father and a law-enforcement officer.",
    ),
    (
        "ganke-1610",
        "Ganke Lee",
        "earth-1610",
        ["Ganke"],
        "human",
        "Miles Morales' closest friend and confidant.",
    ),
    (
        "kingpin-1610",
        "Wilson Fisk",
        "earth-1610",
        ["Kingpin"],
        "human",
        "The Kingpin of Earth-1610.",
    ),
    (
        "george-65",
        "George Stacy",
        "earth-65",
        ["Captain Stacy"],
        "human",
        "Gwen Stacy's father and a police captain.",
    ),
    (
        "matt-65",
        "Matt Murdock",
        "earth-65",
        ["Kingpin"],
        "enhanced",
        "A morally inverted Matt Murdock of Earth-65.",
    ),
    (
        "goblin-65",
        "Peter Parker",
        "earth-65",
        ["Lizard"],
        "lizard",
        "Gwen Stacy's friend whose transformation ended in tragedy.",
    ),
    ("vulture-65", "Adrian Toomes", "earth-65", ["Vulture"], "tech", "The Vulture of Earth-65."),
]


WORK_TITLES = [
    "Amazing Fantasy #15",
    "The Amazing Spider-Man #1",
    "The Amazing Spider-Man #14",
    "The Amazing Spider-Man #31",
    "The Amazing Spider-Man #39",
    "The Amazing Spider-Man #50",
    "The Amazing Spider-Man #90",
    "The Amazing Spider-Man #121",
    "The Amazing Spider-Man #122",
    "The Amazing Spider-Man #129",
    "The Amazing Spider-Man #194",
    "The Amazing Spider-Man #238",
    "The Amazing Spider-Man #252",
    "The Amazing Spider-Man #300",
    "The Amazing Spider-Man #361",
    "Ultimate Spider-Man #1",
    "Ultimate Spider-Man #4",
    "Ultimate Spider-Man #42",
    "Ultimate Spider-Man #160",
    "Ultimate Fallout #4",
    "Miles Morales: Ultimate Spider-Man #1",
    "Spider-Man 2099 #1",
    "Edge of Spider-Verse #2",
    "Spider-Verse #1",
    "Spider-Verse #2",
    "Spider-Verse #3",
    "Spider-Verse #4",
    "Spider-Verse #5",
    "Spider-Geddon #1",
    "Spider-Geddon #2",
    "Spider-Geddon #3",
    "Spider-Geddon #4",
    "Spider-Geddon #5",
    "Secret Wars #8",
    "Civil War #2",
    "Superior Spider-Man #1",
    "Venom: Lethal Protector #1",
    "Maximum Carnage Alpha",
    "Kraven's Last Hunt",
    "Spider-Man: Blue #1",
    "Spider-Gwen #1",
    "Silk #1",
    "Scarlet Spider #1",
    "Spider-Man: Into the Spider-Verse",
    "Spider-Man: Across the Spider-Verse",
    "Spider-Man: No Way Home",
    "Spider-Man (2002)",
    "The Amazing Spider-Man (2012)",
    "Spider-Man: The Animated Series",
    "Marvel's Spider-Man (2018)",
]


EVENTS = [
    ("spider-verse-event", "Spider-Verse"),
    ("spider-geddon-event", "Spider-Geddon"),
    ("clone-saga-event", "Clone Saga"),
    ("maximum-carnage-event", "Maximum Carnage"),
    ("civil-war-event", "Civil War"),
    ("secret-wars-event", "Secret Wars"),
    ("sinister-six-event", "Sinister Six"),
    ("kravens-last-hunt-event", "Kraven's Last Hunt"),
    ("goblin-legacy-event", "Goblin Legacy"),
    ("collider-crisis-event", "Collider Crisis"),
]


TEAMS = [
    ("avengers", "Avengers"),
    ("fantastic-four", "Fantastic Four"),
    ("sinister-six", "Sinister Six"),
    ("defenders", "Defenders"),
    ("spider-society", "Spider-Society"),
    ("daily-bugle", "Daily Bugle"),
    ("symbiotes", "Symbiotes"),
    ("spider-family", "Spider-Family"),
]


POWERS = {
    "spider-sense": "Spider-Sense",
    "wall-crawling": "Wall Crawling",
    "super-strength": "Superhuman Strength",
    "agility": "Enhanced Agility",
    "venom-blast": "Venom Blast",
    "camouflage": "Camouflage",
    "organic-webbing": "Organic Webbing",
    "regeneration": "Regeneration",
    "electricity": "Electricity Manipulation",
    "shapeshifting": "Shapeshifting",
    "flight": "Flight",
    "portals": "Portal Generation",
    "illusions": "Illusions",
    "tech": "Advanced Technology",
    "vibration": "Vibration Projection",
    "digital-avatar": "Digital Avatar",
    "toon-force": "Cartoon Physics",
}


POWER_PROFILES = {
    "spider": ["spider-sense", "wall-crawling", "super-strength", "agility"],
    "miles": ["spider-sense", "wall-crawling", "venom-blast", "camouflage"],
    "miguel": ["wall-crawling", "super-strength", "agility", "organic-webbing"],
    "symbiote": ["super-strength", "regeneration", "shapeshifting", "organic-webbing"],
    "goblin": ["super-strength", "regeneration", "tech"],
    "tech": ["tech"],
    "pilot": ["tech", "spider-sense"],
    "bio": ["super-strength", "agility", "flight"],
    "digital": ["digital-avatar", "tech"],
    "toon": ["toon-force", "agility"],
    "enhanced": ["agility", "super-strength"],
    "cosmic": ["flight", "super-strength"],
    "electric": ["electricity"],
    "sand": ["shapeshifting", "super-strength"],
    "lizard": ["regeneration", "super-strength"],
    "strength": ["super-strength"],
    "vampire": ["flight", "regeneration", "super-strength"],
    "portal": ["portals"],
    "human": [],
}


CORE_RELATIONS = [
    ("miles-1610", "peter-b-616b", "MENTORED_BY", "Spider-Man: Into the Spider-Verse"),
    ("miles-1610", "gwen-65", "ALLY_OF", "Spider-Man: Into the Spider-Verse"),
    ("miles-1610", "miguel-928", "CONFLICT_WITH", "Spider-Man: Across the Spider-Verse"),
    ("miles-1610", "spider-verse-event", "PARTICIPATED_IN", "Spider-Verse #2"),
    ("miles-1610", "avengers", "MEMBER_OF", "All-New, All-Different Avengers #1"),
    ("miles-1610", "peter-1610", "INSPIRED_BY", "Ultimate Fallout #4"),
    ("miles-1610", "rio-1610", "CHILD_OF", "Ultimate Spider-Man #1"),
    ("miles-1610", "jefferson-1610", "CHILD_OF", "Ultimate Spider-Man #1"),
    ("miles-1610", "prowler-1610", "FAMILY_OF", "Ultimate Spider-Man #42"),
    ("miles-1610", "ganke-1610", "FRIEND_OF", "Ultimate Spider-Man #1"),
    ("peter-616", "daredevil-616", "ALLY_OF", "The Amazing Spider-Man #16"),
    ("peter-616", "torch-616", "FRIEND_OF", "The Amazing Spider-Man #1"),
    ("peter-616", "mary-jane-616", "ROMANTIC_RELATIONSHIP_WITH", "The Amazing Spider-Man #42"),
    ("peter-616", "aunt-may-616", "FAMILY_OF", "Amazing Fantasy #15"),
    ("peter-616", "norman-616", "ENEMY_OF", "The Amazing Spider-Man #39"),
    ("peter-616", "doc-ock-616", "ENEMY_OF", "The Amazing Spider-Man #3"),
    ("peter-616", "venom-616", "ENEMY_OF", "The Amazing Spider-Man #300"),
    ("venom-616", "carnage-616", "ENEMY_OF", "The Amazing Spider-Man #361"),
    ("norman-616", "harry-616", "PARENT_OF", "The Amazing Spider-Man #31"),
    ("gwen-65", "george-65", "CHILD_OF", "Edge of Spider-Verse #2"),
    ("gwen-65", "goblin-65", "FRIEND_OF", "Edge of Spider-Verse #2"),
    ("peter-616", "ben-reilly-616", "VARIANT_OF", "Clone Saga"),
    ("ben-reilly-616", "kaine-616", "SIBLING_OF", "Clone Saga"),
    ("peter-616", "black-cat-616", "ALLY_OF", "The Amazing Spider-Man #194"),
    ("kingpin-616", "daredevil-616", "ENEMY_OF", "Daredevil #170"),
    ("peter-616", "kingpin-616", "ENEMY_OF", "The Amazing Spider-Man #50"),
    ("peter-616", "jonah-616", "WORKS_FOR", "The Amazing Spider-Man #1"),
]


def slug(value: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-").replace("--", "-")


def source(title: str, verified: bool = False, source_type: str = "demo") -> dict[str, Any]:
    return {
        "source_title": title,
        "source_type": source_type,
        "source_url": "",
        "verified": verified,
    }


def build_dataset() -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def add_node(node_id: str, label: str, node_type: str, **properties: Any) -> None:
        nodes.append({"id": node_id, "label": label, "type": node_type, **properties})

    def add_edge(
        start: str,
        end: str,
        relation: str,
        provenance: dict[str, Any],
        **properties: Any,
    ) -> None:
        key = (start, end, relation)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append(
            {
                "id": f"rel-{len(edges) + 1:04d}",
                "source": start,
                "target": end,
                "type": relation,
                "properties": {**provenance, **properties},
            }
        )

    for uid, name, designation, description in UNIVERSES:
        add_node(uid, name, "Universe", designation=designation, description=description)

    add_node(
        "identity-spider-man",
        "Spider-Man",
        "Concept",
        description="The shared heroic identity across realities.",
    )
    add_node(
        "identity-spider-woman",
        "Spider-Woman",
        "Concept",
        description="A family of related spider-hero identities.",
    )

    for pid, label in POWERS.items():
        add_node(f"power-{pid}", label, "Power", description=f"Power or capability: {label}.")

    for tid, label in TEAMS:
        add_node(tid, label, "Team", description=f"Team or organization: {label}.")

    for eid, label in EVENTS:
        add_node(eid, label, "Event", description=f"Major event: {label}.")
        add_edge(eid, "earth-616", "OCCURRED_IN", source("SpiderVerse AI demonstration seed"))

    for index, title in enumerate(WORK_TITLES):
        work_id = f"work-{index + 1:02d}-{slug(title)[:32]}"
        universe_id = "earth-616"
        if "Ultimate" in title or "Into the" in title or "Across the" in title:
            universe_id = "earth-1610"
        elif "2099" in title:
            universe_id = "earth-928"
        elif title == "Spider-Man: No Way Home":
            universe_id = "mcu-199999"
        elif title == "Spider-Man (2002)":
            universe_id = "raimi-96283"
        elif title == "The Amazing Spider-Man (2012)":
            universe_id = "webb-120703"
        add_node(
            work_id,
            title,
            "Work",
            work_type="Movie" if "Spider-Man:" in title or title.endswith(")") else "Comic",
            universe_id=universe_id,
            description=f"A work represented in the SpiderVerse AI demonstration catalog: {title}.",
        )
        add_edge(work_id, universe_id, "SET_IN_UNIVERSE", source(title, source_type="catalog"))

    character_ids: list[str] = []
    spider_ids: list[str] = []
    by_universe: dict[str, list[str]] = defaultdict(list)
    for cid, name, universe_id, aliases, profile, description in CHARACTERS:
        character_ids.append(cid)
        by_universe[universe_id].append(cid)
        is_spider = any(
            "Spider" in alias or alias in {"Silk", "Araña", "Ghost-Spider"} for alias in aliases
        )
        if is_spider:
            spider_ids.append(cid)
        add_node(
            cid,
            name,
            "Character",
            universe_id=universe_id,
            aliases=aliases,
            description=description,
            status="Active",
            power_profile=profile,
        )
        add_edge(
            cid, universe_id, "BELONGS_TO_UNIVERSE", source("SpiderVerse AI demonstration seed")
        )
        if is_spider:
            concept = (
                "identity-spider-woman" if "Spider-Woman" in aliases else "identity-spider-man"
            )
            add_edge(
                cid,
                concept,
                "VARIANT_OF",
                source("Spider-Verse identity mapping", source_type="curated"),
            )
        for power_id in POWER_PROFILES[profile]:
            add_edge(
                cid, f"power-{power_id}", "HAS_POWER", source("SpiderVerse AI capability profile")
            )

    for start, end, relation, title in CORE_RELATIONS:
        add_edge(start, end, relation, source(title, verified=True, source_type="work"))

    # Reproducible demo associations create useful density while remaining explicitly unverified.
    work_nodes = [node for node in nodes if node["type"] == "Work"]
    for index, cid in enumerate(character_ids):
        first = work_nodes[index % len(work_nodes)]
        second = work_nodes[(index * 7 + 13) % len(work_nodes)]
        add_edge(cid, first["id"], "APPEARS_IN", source(first["label"]))
        add_edge(cid, second["id"], "APPEARS_IN", source(second["label"]))

    for index, cid in enumerate(spider_ids):
        add_edge(cid, "spider-family", "MEMBER_OF", source("Spider-Verse identity mapping"))
        if index % 2 == 0:
            add_edge(
                cid, "spider-verse-event", "PARTICIPATED_IN", source("Spider-Verse event mapping")
            )
        if index % 3 == 0:
            add_edge(
                cid, "spider-society", "MEMBER_OF", source("Spider-Verse demonstration mapping")
            )

    sinister_ids = [
        "doc-ock-616",
        "vulture-616",
        "mysterio-616",
        "electro-616",
        "sandman-616",
        "kraven-616",
    ]
    for cid in sinister_ids:
        add_edge(
            cid,
            "sinister-six",
            "MEMBER_OF",
            source("The Amazing Spider-Man Annual #1", source_type="work"),
        )
        add_edge(cid, "peter-616", "ENEMY_OF", source("SpiderVerse AI curated enemy mapping"))

    for cid in ["peter-616", "jessica-drew-616", "daredevil-616"]:
        add_edge(cid, "avengers", "MEMBER_OF", source("SpiderVerse AI team mapping"))
    for cid in ["venom-616", "carnage-616"]:
        add_edge(cid, "symbiotes", "MEMBER_OF", source("SpiderVerse AI symbiote mapping"))

    # Connect nearby characters within the same reality for navigable local neighborhoods.
    for universe_id, members in by_universe.items():
        if len(members) < 2:
            continue
        for index, cid in enumerate(members):
            other = members[(index + 1) % len(members)]
            add_edge(cid, other, "RELATED_TO", source(f"{universe_id} demonstration neighborhood"))

    for index, work in enumerate(work_nodes):
        event_id = EVENTS[index % len(EVENTS)][0]
        add_edge(
            work["id"], event_id, "DEPICTS_EVENT", source(work["label"], source_type="catalog")
        )

    return {
        "meta": {
            "name": "SpiderVerse AI demonstration seed",
            "version": "1.0.0",
            "generated_by": "scripts/generate_dataset.py",
            "authoritative": False,
        },
        "nodes": nodes,
        "edges": edges,
    }


def main() -> None:
    dataset = build_dataset()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = defaultdict(int)
    for node in dataset["nodes"]:
        counts[node["type"]] += 1
    print(f"Wrote {OUTPUT}")
    print(f"Nodes: {len(dataset['nodes'])} | Edges: {len(dataset['edges'])}")
    print("Node types:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
