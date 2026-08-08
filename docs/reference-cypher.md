# V1 reference Cypher

These queries target the graph created by `scripts/seed_neo4j.py`. Every domain node has the
base label `Entity`, one domain label, and a unique `id` property. They are intentionally
read-only and can be rerun after every seed.

## Counts by domain label

```cypher
MATCH (n:Entity)
UNWIND [label IN labels(n) WHERE label <> 'Entity'] AS domainLabel
RETURN domainLabel, count(*) AS nodes
ORDER BY domainLabel;
```

Expected V1 total: 164 nodes. Expected domain counts: Character 59, Concept 2, Event 10,
Power 17, Team 8, Universe 18, Work 50.

## Counts by relationship type

```cypher
MATCH (:Entity)-[r]->(:Entity)
RETURN type(r) AS relationshipType, count(*) AS relationships
ORDER BY relationshipType;
```

Expected V1 total across all rows: 574 relationships.

## Search a character by name or alias

```cypher
WITH toLower('Spider-Man 2099') AS needle
MATCH (character:Entity:Character)
WHERE toLower(character.label) CONTAINS needle
   OR any(alias IN coalesce(character.aliases, []) WHERE toLower(alias) CONTAINS needle)
RETURN character.id, character.label, character.aliases, character.universe_id
ORDER BY character.label, character.id;
```

## Neighborhood of Miles Morales

```cypher
MATCH (miles:Entity:Character {id: 'miles-1610'})-[r]-(neighbor:Entity)
RETURN miles.id AS focusId,
       type(r) AS relationshipType,
       r.id AS relationshipId,
       neighbor.id AS neighborId,
       neighbor.label AS neighborLabel,
       [label IN labels(neighbor) WHERE label <> 'Entity'][0] AS neighborType
ORDER BY relationshipType, neighborLabel, relationshipId;
```

## Spider-Man variants

```cypher
MATCH (variant:Entity:Character)-[:VARIANT_OF]->(:Entity:Concept {id: 'identity-spider-man'})
RETURN variant.id, variant.label, variant.aliases, variant.universe_id
ORDER BY variant.label, variant.id;
```

## Characters in one universe

```cypher
MATCH (character:Entity:Character)-[:BELONGS_TO_UNIVERSE]->(
  universe:Entity:Universe {id: 'earth-1610'}
)
RETURN character.id, character.label, universe.label AS universe
ORDER BY character.label, character.id;
```

## Shortest narrative path

```cypher
MATCH (start:Entity:Character {id: 'miles-1610'}),
      (finish:Entity:Character {id: 'daredevil-616'}),
      path = shortestPath((start)-[*..12]-(finish))
WHERE all(
  relation IN relationships(path)
  WHERE NOT type(relation) IN [
    'APPEARS_IN', 'HAS_POWER', 'SET_IN_UNIVERSE', 'DEPICTS_EVENT',
    'OCCURRED_IN', 'BELONGS_TO_UNIVERSE'
  ]
)
RETURN [node IN nodes(path) | node.id] AS nodeIds,
       [relation IN relationships(path) | type(relation)] AS relationshipTypes,
       length(path) AS hops;
```

## Relationships with invalid endpoints

Neo4j cannot store a relationship without two endpoint nodes. This check detects endpoints
that escaped the seeded `Entity` domain.

```cypher
MATCH (source)-[r]->(target)
WHERE NOT source:Entity OR NOT target:Entity
RETURN r.id, type(r), source.id, target.id;
```

Expected result: no rows.

## Duplicate entity IDs

```cypher
MATCH (node:Entity)
WITH node.id AS id, count(*) AS occurrences
WHERE id IS NULL OR occurrences > 1
RETURN id, occurrences
ORDER BY id;
```

Expected result: no rows. The seed also creates a uniqueness constraint named by Neo4j for
`(:Entity).id`.
