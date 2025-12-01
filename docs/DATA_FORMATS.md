# Dominium — DATA FORMATS

All formats must be deterministic, endian-neutral, and forward-compatible.

---

## 1. SAVEGAME FORMAT

Binary container with:

- header (version, UUID, endian marker)
- simulation state
- world metadata
- chunk tables
- entity lists
- network graphs
- economy state
- climate state
- RNG seeds

---

## 2. MOD PACKAGE FORMAT

`*.dmod` = ZIP container:

- manifest.json
- data/
- scripts/
- textures/
- sounds/
- tech_tree.json

---

## 3. BLUEPRINT FORMAT

JSON or compact binary:

- nodes[]
- edges[]
- placement rules
- required resources

---

## 4. REPLAYS

Two modes:

### Input-only mode
- tick-by-tick input events

### Snapshot mode
- periodic snapshots + delta compression

Either mode must be deterministic.

