
# ────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from itertools import islice
from typing import Dict, Set, List, Any, Dict

# ────────────────────────────────────────────────────────────────────────────────
# Extraction helpers (match your snippet)

import json
from pathlib import Path


def load_json_cache(cache_path: Path, company: str) -> Dict[str, Any]:
    """
    Returns the cached object for a given company name, or {} if missing/invalid.

    Expected file structure:
      { "<company-name>": { ...arbitrary nested JSON from that source... } }
    """
    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
        return raw.get(company, {}) if isinstance(raw, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}



def extract_wr_officers(WR_Data: dict) -> Dict[str, Set[str]]:
    """
    World Registry shape (typical):
      {
        "result": [
          ...,
          {
            "people": [
              {"primaryName": {"fullName": "Jane Doe"}, "title": "CFO"},
              ...
            ]
          }
        ]
      }
    """
    by_name: Dict[str, Set[str]] = {}
    if not WR_Data:
        return by_name

    recs = WR_Data.get("result", [])
    rec = recs[1] if len(recs) > 1 else (recs[0] if recs else {})
    for p in rec.get("people", []):
        name = (p.get("primaryName") or {}).get("fullName")
        title = p.get("title", "Officer")
        if name:
            by_name.setdefault(name.strip(), set()).add(title.strip())
    return by_name



def extract_pds_officers(PDS_Data: dict) -> Dict[str, Set[str]]:
    """
    PDS shape (typical):
      {
        "result": [
          {"kind": "Company",
           "directors": [
             {"primaryName": {"fullName": "Jane Doe"}, "relType": "executive_director"},
             ...
           ]
          }
        ]
      }
    """
    by_name: Dict[str, Set[str]] = {}
    if not PDS_Data:
        return by_name

    rec_pds = next((r for r in PDS_Data.get("result", []) if r.get("kind") == "Company"), {})
    for d in rec_pds.get("directors", []):
        name = ((d.get("primaryName") or {}).get("fullName")) or d.get("name")
        title = d.get("relType") or d.get("title") or "Director"
        if name:
            by_name.setdefault(name.strip(), set()).add(title.replace("_", " ").title().strip())
    return by_name




def fmt_officers(src: Dict[str, Set[str]], top_n: int = 10) -> List[dict]:
    return [
        {"name": n, "title": ", ".join(sorted(t))}
        for n, t in islice(src.items(), top_n)
    ]


def merge_officers_data(*sources: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    combined: Dict[str, Set[str]] = {}
    for src in sources:
        for name, titles in src.items():
            combined.setdefault(name, set()).update(titles)
    return combined
