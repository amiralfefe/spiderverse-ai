# Data model

## Nodes

The seed contains `Character`, `Universe`, `Work`, `Event`, `Team`, `Power`, and `Concept` nodes.

Every node has:

- `id`: stable slug, unique across the dataset;
- `label`: display name;
- `type`: graph category.

Character nodes additionally carry their own `universe_id`, aliases, status, description, and a seed-only power profile. The same civilian name in different realities therefore produces separate IDs.

## Relationships

The V1 covers identity, multiverse, narrative, participation, appearance, and capability edges. Examples include:

- `BELONGS_TO_UNIVERSE`
- `VARIANT_OF`
- `ALLY_OF`, `ENEMY_OF`, `FRIEND_OF`, `MENTORED_BY`
- `FAMILY_OF`, `PARENT_OF`, `CHILD_OF`, `SIBLING_OF`
- `MEMBER_OF`, `PARTICIPATED_IN`
- `APPEARS_IN`, `DEPICTS_EVENT`
- `HAS_POWER`

Every relationship has a stable ID and the provenance properties:

```json
{
  "source_title": "Ultimate Fallout #4",
  "source_type": "work",
  "source_url": "",
  "verified": true
}
```

`verified` means reviewed as a curated seed assertion; it does not make the dataset an authoritative canon reference. Automatically scale-building demo associations are `false` and are labeled accordingly by the UI.

## Validation contract

`scripts/validate_graph.py` rejects:

- missing or duplicate node/edge IDs;
- dangling relationship endpoints;
- characters that reference an unknown universe;
- incomplete relationship provenance;
- Spider identities without `VARIANT_OF` mapping;
- fewer than 50 characters or 500 relationships.

The JSON shape is also documented by `data/schemas/graph.schema.json`.
