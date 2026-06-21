# Foothold — Vietnam 1975 Conversion (Syria)

This branch (`Vietnam1975`) restricts the **Syria** Foothold mission to a 1975
Vietnam-era setting. The script/config side is done; the remaining work is in
the Mission Editor (`.miz`) plus installing the required mods.

## What is already done (committed)

### `Common Scripts/Foothold Config.lua`
- `Era = "Coldwar"` — activates aircraft allow-list filtering and modern-weapon stripping.
- Period SAM toggles enabled: `NoSA10AndSA11 = true`, `NoTorM2AndPantsir = true`, `NoSA15 = true`.
- `allowedPlanes` (BLUE) trimmed to period airframes: F-14A variants (no F-14B),
  F-4E, F-5E, F-86F, A-4E-C, F-100D, OV-10A, OH-6A, UH-1H, P-3C, E-2C, Hercules,
  plus the VWV mod **AI assets** (A-1/AD-4 Skyraider, A-37, RA-5C, CH-46D, EC-121,
  F-8 Crusader, H-2 Seasprite, O-1 Bird Dog, RF-101B).
- `allowedPlanesRed` (RED) trimmed to MiG-15bis, MiG-19P, MiG-21Bis, Mi-8MT, plus
  the VWV `vwv_mig17f` and `vwv_mig21mf` AI assets.

### `Setup files/footholdSyriaSetup.lua`
- `SA-13` (Strela-10) → `SA-7` (Strela-2) across random pools and downgrade swaps.
- `SA-19` (Tunguska) → `ZSU-23` (Shilka) across random pools, downgrade swaps, and
  the fixed positions (`Fixed Bravo`, `Fixed SAITE`, `Fixed Benguriondefence`).
- Period-correct holdovers kept: SA-8 (1972), SA-9 (1968); fixed SAMs fall back to
  SA-2 / SA-3 / SA-6.

## Required mods (server + all clients, identical versions)

1. **LowDigitsMANPADS** — provides the SA-7 Strela-2.
   - Types: `Soldier Strela2 LDM`, `Soldier Strela2M LDM`.
   - https://github.com/Des-mundo/LowDigitsMANPADS/releases
2. **Vietnam War Vessels (VWV)** aircraft pack — the AI airframes listed above.
3. (ZSU-23-4 Shilka is a **stock** DCS unit — no mod required.)

> Mods that add units require every connecting client to have the exact same
> version, or they will fail integrity / not see the units.

## Next steps — Mission Editor (`.miz`)

Open `Missions/Foothold_SY_extended_*.miz` in the DCS Mission Editor.

1. **Set every warehouse aircraft to `LIMITED`** (do NOT "copy to all"). The
   Cold War stock logic can only manage limited warehouses.

2. **Create the new RED SHORAD template groups** (late-activation). Easiest path:
   rename the existing modern group templates and swap the unit type inside.

   | Template group name (exact)                       | Unit to place           |
   |---------------------------------------------------|-------------------------|
   | `Red SAM SHORAD SA-7`                             | `Soldier Strela2 LDM` / `Soldier Strela2M LDM` |
   | `Red SAM SHORAD ZSU-23`                          | ZSU-23-4 Shilka (stock) |
   | `Red SAM SHORAD ZSU-23 Fixed Bravo`              | ZSU-23-4 Shilka (stock) |
   | `Red SAM SHORAD ZSU-23 Fixed SAITE`              | ZSU-23-4 Shilka (stock) |
   | `Red SAM SHORAD ZSU-23 Fixed Benguriondefence`   | ZSU-23-4 Shilka (stock) |

   If any of these named templates is missing, the corresponding random/fixed
   spawn will silently fail.

3. **VWV AI assets**: ensure the mission's spawn templates / warehouses reference
   the VWV types you want to field. These are AI-only (not player-flyable slots).

4. **Inject the updated config** into the `.miz`:
   - Use `tools/MizBatchUpdater.exe` / `tools/MizFileReplacer.exe`, or the
     Foothold Config Manager, to push `Common Scripts/Foothold Config.lua` and the
     Syria setup into the mission.

5. **Start fresh** — delete/avoid reusing the old save
   (`footholdSyria_Extended_0.1_coldwar.lua`); saved files store the previously
   spawned composition and will not pick up the new templates.

## Optional follow-ups (not yet done)

- Tighten `restrictedWeapons` / `ForbiddWeaponsInAllEra` to strip post-1975 A2A/PGM
  weapons that survive Cold War mode (e.g. AIM-9L/M/P, later Paveways). The F-14A's
  AIM-54 Phoenix (1974) is intentionally left available.
- Add fixed `Red SAM SHORAD SA-7` placements at chosen zones for guaranteed
  Strela-2 sites (currently SA-7 only appears via random SHORAD rolls).
- Review the strategic SAM belt (SA-2 / SA-3 / SA-6) placement for the desired
  Vietnam threat density.
