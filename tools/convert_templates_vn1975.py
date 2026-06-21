"""
Convert the Foothold Syria spawn-template groups to Vietnam-1975 airframes.

- Reads the .miz (zip) raw, parses the `mission` lua table with pydcs's generic
  lua parser (works regardless of terrain/AI-option version mismatches).
- For each Foothold spawn-template group (matched by exact group name), swaps the
  unit `type`, assigns a period-correct STOCK loadout (pulled from the installed
  DCS UnitPayloads), or leaves pylons empty for VWV mod (AI-only) airframes.
- Group names, group/unit IDs, routes/waypoints, skill and lateActivation are
  preserved. Writes a NEW .miz so the original is untouched.

Run:
  set PYTHONPATH=E:\git\pydcs
  py -3.13 -W ignore tools\convert_templates_vn1975.py
"""
import os
import sys
import zipfile

# --- point pydcs at the local DCS install so payloads/liveries resolve ---
import dcs.installation as inst
INSTALL = r"E:\Eagle Dynamics\DCS World OpenBeta"
SAVED = r"C:\Users\spindler\Saved Games\DCS.openbeta"
inst.get_dcs_install_directory = lambda: INSTALL + os.sep
inst.get_dcs_saved_games_directory = lambda: SAVED

from dcs import lua
from dcs import task as task_mod
from dcs.payloads import PayloadDirectories

SRC = r"E:\git\Lekas-Foothold-TeTeT\Missions\Foothold_SY_extended_4.1.7_Multi_Language_Coldwar-Modern-Vietnam_TeTeT.miz"
DST = r"E:\git\Lekas-Foothold-TeTeT\Missions\Foothold_SY_extended_4.1.7_Multi_Language_Coldwar-Modern-Vietnam_TeTeT_VN1975.miz"

# task internal_name -> id  (CAP=11, Intercept=10, CAS=31, GroundAttack=32,
# SEAD=29, AntishipStrike=30, RunwayAttack=34, Transport=35, ...)
TASK = {v.internal_name: v.id for v in task_mod.MainTask.map.values()}

# Per-template conversion. Value = (new_type, [task-id priority] or None for empty pylons)
# Groups NOT listed are intentionally left unchanged (already period-correct: keep).
CAP = [TASK["CAP"], TASK["Intercept"]]
INT = [TASK["Intercept"], TASK["CAP"]]
CAS = [TASK["CAS"], TASK["GroundAttack"]]
SEAD = [TASK["SEAD"], TASK["CAS"], TASK["GroundAttack"]]
ANTI = [TASK["AntishipStrike"], TASK["CAS"], TASK["GroundAttack"]]
RWY = [TASK["RunwayAttack"], TASK["GroundAttack"], TASK["CAS"]]
TRANS = [TASK["Transport"], TASK["CAS"]]

# Exact period-correct payloads for airframes where the generic task-pick is wrong
# (would be unarmed or anachronistic for 1975). Keyed by group name.
PAYLOAD_NAME_OVERRIDE = {
    "BLUE_HORNET_CW":  "A2A MEDIUM RANGE: Aim-7E*4, Aim-9J*4, ALE-40 (30-60)*1, Sargent Fletcher Fuel Tank 370 GAL*2",
    "BLUE_F15C_CW":    "AIM-54A-MK47*6, AIM-9L*2, XT*2",
    "BLUE_F4E_Load1":  "Mk-82 *6, Fuel 150G *2",
    "BLUE_F14_SEAD":   "SEAD: AGM-45A*4, Aim-7E2*3, Aim-9L*4, ALQ-131*1, ALE-40 (30-60)*1, Sargent Fl. Fuel Tank 600 Gal*1",
    "Hornet_Anti_Ship":"IRON: Mk-82 (LD)*12, Aim-7E2*3, Aim-9L*4, ALQ-131 ECM*1, ALE-40 (30-60)*1, Sargent Fletcher Fuel Tank 600 GAL*1",
}

MAPPING = {
    # ---- BLUE ----
    "BLUE_HORNET_CW":             ("F-4E-45MC",      CAP),
    "BLUE_F15C_CW":               ("F-14A-135-GR",   CAP),
    "BLUE_F4E_Load1":             ("A-4E-C",         CAS),
    "BLUE_F4E_Load2":             ("vwv_a1_skyraider", None),   # VWV (arm in ME)
    "BLUE_F14_SEAD":              ("F-4E-45MC",      SEAD),
    "Hornet_Anti_Ship":           ("F-4E-45MC",      ANTI),
    "BLUE_AH-64D_OneShip_Load2":  ("UH-1H",          CAS),
    "BLUE_AH-64D_TwoShip_Load2":  ("UH-1H",          CAS),
    "OH_58D":                     ("UH-1H",          CAS),
    "OH_58D_TwoShip":             ("UH-1H",          CAS),
    "BLUE_CH-47":                 ("vwv_ch46d",      None),      # VWV (transport)
    "BLUE_CH-47_2":               ("vwv_ch46d",      None),      # VWV (transport)
    "BLUE_UH-60A":                ("UH-1H",          TRANS),
    "C-130J-30":                  ("Hercules",       None),      # transport, no payload file
    # ---- RED ----
    "RED_MIG29A_Load1":           ("MiG-21Bis",      CAP),
    "RED_MIG29A_Load2":           ("MiG-21Bis",      CAP),
    "RED_SU27_EW":                ("MiG-21Bis",      CAP),
    "RED_MIG23MLD":               ("vwv_mig21mf",    None),      # VWV (arm in ME)
    "RED_MIG25PD":                ("MiG-21Bis",      INT),
    "RED_SU25_OneShip_Load1":     ("vwv_mig17f",     None),      # VWV (arm in ME)
    "RED_SU25_OneShip_Load2":     ("vwv_mig17f",     None),      # VWV
    "RED_SU25_OneShip_Load3":     ("vwv_mig17f",     None),      # VWV
    "RED_SU25_TwoShip_Load1":     ("MiG-21Bis",      CAS),
    "RED_SU25_TwoShip_Load2":     ("MiG-21Bis",      CAS),
    "RED_SU25_TwoShip_Load3":     ("MiG-21Bis",      CAS),
    "RED_Mirage_F1BQ_Load1":      ("vwv_mig17f",     None),      # VWV (arm in ME)
    "RED_Mirage_F1BQ_Load2":      ("vwv_mig17f",     None),      # VWV
    "RED_SU-24M_TWOSHIP":         ("MiG-21Bis",      CAS),
    "RED_SU-24M_ONESHIP":         ("MiG-21Bis",      CAS),
    "RED_MIG-27K_RUNWAY":         ("MiG-21Bis",      RWY),
    "RED_MIRAGE_F1_RUNWAY":       ("MiG-21Bis",      RWY),
}


def build_payload_index():
    """unitType -> list of {name, pylons(dict num->CLSID), tasks(set of ids)}."""
    globals_ = {v.internal_name: v.id for v in task_mod.MainTask.map.values()}
    index = {}
    for d in PayloadDirectories.payload_dirs():
        if not d.exists():
            continue
        for f in d.glob("*.lua"):
            try:
                data = lua.loads(f.read_text(encoding="utf-8", errors="replace"),
                                 _globals=globals_)
            except Exception:
                continue
            up = data.get("unitPayloads") if isinstance(data, dict) else None
            if not up:
                continue
            utype = up.get("unitType")
            if not utype:
                continue
            lst = index.setdefault(utype, [])
            for pl in up.get("payloads", {}).values():
                if not isinstance(pl, dict):
                    continue
                pylons = {}
                for ent in pl.get("pylons", {}).values():
                    if isinstance(ent, dict) and ent.get("num") is not None:
                        pylons[ent["num"]] = ent.get("CLSID", "")
                tasks = pl.get("tasks", {})
                tids = set(tasks.values() if isinstance(tasks, dict) else tasks)
                lst.append({"name": pl.get("name"), "pylons": pylons, "tasks": tids})
    return index


def pick_payload(index, utype, task_priority, name_override=None):
    pays = index.get(utype, [])
    if not pays:
        return None
    if name_override:
        for p in pays:
            if p["name"] == name_override:
                return p
        print(f"  !! override payload not found for {utype}: {name_override!r}")
    for t in task_priority:
        for p in pays:
            if t in p["tasks"] and p["pylons"]:
                return p
    return max(pays, key=lambda p: len(p["pylons"]))  # fallback: most-armed


def detect_clsid_key(mission):
    """Find whether existing unit pylons use 'CLSID' or 'clsid'."""
    for coa in mission.get("coalition", {}).values():
        for c in coa.get("country", {}).values():
            for cat in ("plane", "helicopter"):
                for g in c.get(cat, {}).get("group", {}).values():
                    for u in g.get("units", {}).values():
                        py = u.get("payload", {}).get("pylons", {})
                        for ent in py.values():
                            if isinstance(ent, dict):
                                for k in ent.keys():
                                    if k.upper() == "CLSID":
                                        return k
    return "CLSID"


def main():
    with zipfile.ZipFile(SRC, "r") as z:
        names = z.namelist()
        infos = {n: z.getinfo(n) for n in names}
        blobs = {n: z.read(n) for n in names}

    mission = lua.loads(blobs["mission"].decode("utf-8", errors="replace"))["mission"]
    index = build_payload_index()
    clsid_key = detect_clsid_key(mission)
    print(f"payload index types={len(index)}  clsid key in mission='{clsid_key}'\n")

    report = []
    seen = set()
    for coa_name, coa in mission.get("coalition", {}).items():
        for c in coa.get("country", {}).values():
            for cat in ("plane", "helicopter"):
                for g in c.get(cat, {}).get("group", {}).values():
                    gname = g.get("name")
                    if gname not in MAPPING:
                        continue
                    seen.add(gname)
                    new_type, task_priority = MAPPING[gname]
                    if task_priority is None:
                        payload = None
                        ldesc = "EMPTY (VWV - arm in ME)"
                    else:
                        payload = pick_payload(index, new_type, task_priority,
                                               PAYLOAD_NAME_OVERRIDE.get(gname))
                        ldesc = payload["name"] if payload else "NO PAYLOAD FOUND -> empty"

                    units = g.get("units", {})
                    for u in units.values():
                        old_type = u.get("type")
                        u["type"] = new_type
                        u["livery_id"] = ""
                        pl = u.setdefault("payload", {})
                        if payload and payload["pylons"]:
                            pl["pylons"] = {num: {clsid_key: cls}
                                            for num, cls in payload["pylons"].items()}
                        else:
                            pl["pylons"] = {}
                    report.append((coa_name, gname, old_type, new_type,
                                   len(units), ldesc))

    # serialize + repack: replace only the 'mission' entry, keep everything else
    new_mission = lua.dumps(mission, "mission", 1)
    with zipfile.ZipFile(DST, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for n in names:
            if n == "mission":
                z.writestr("mission", new_mission)
            else:
                # preserve original compression type per entry
                zi = zipfile.ZipInfo(n, date_time=infos[n].date_time[:6])
                zi.compress_type = infos[n].compress_type
                zi.external_attr = infos[n].external_attr
                z.writestr(zi, blobs[n])

    # report
    print(f"converted {len(report)} groups  (mapping entries={len(MAPPING)}, "
          f"matched={len(seen)})")
    missing = set(MAPPING) - seen
    if missing:
        print("  !! NOT FOUND in mission:", sorted(missing))
    print()
    for coa_name, gname, old, new, n, ldesc in sorted(report):
        print(f"  [{coa_name:7s}] {gname:30s} {old:16s} -> {new:18s} x{n}  | {ldesc}")

    # verify re-parse of the new miz
    with zipfile.ZipFile(DST, "r") as z:
        reparsed = lua.loads(z.read("mission").decode("utf-8", errors="replace"))
    assert "mission" in reparsed, "re-parse failed!"
    print(f"\nOK wrote and re-parsed: {DST}")
    print(f"entries in new miz: {len(zipfile.ZipFile(DST).namelist())} (orig {len(names)})")


if __name__ == "__main__":
    main()
