from __future__ import annotations

from datetime import datetime

from pathlib import Path


from mcp.server.fastmcp import FastMCP

from pathlib import Path
from mcp_project.utils.utils import (
    load_json_cache, merge_officers_data, fmt_officers,
    extract_pds_officers, extract_wr_officers,
)
from time import perf_counter

import logging, os, sys
level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    stream=sys.stderr,  # <— ensure logs go to stderr
    format="%(levelname)s | %(message)s",
)

log = logging.getLogger("key_officers_agent")

# Path relative to this file's location
ROOT = Path(__file__).resolve().parents[1]
pds_path = ROOT / "cache" / "json" / "PDS_Data.json"
wr_path = ROOT / "cache" / "json" / "WR_Data.json"


# ────────────────────────────────────────────────────────────────────────────────
# Server
# ────────────────────────────────────────────────────────────────────────────────
mcp = FastMCP("key_officers_agent")


# ────────────────────────────────────────────────────────────────────────────────
# Tools
# ────────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_key_officers(company_name: str, top_n: int = 10) -> dict:
    """
    Merge key-officer info from WR + PDS caches.

    Args:
      company_name: The company key used to look up cached JSON.
      top_n:        Max rows per section to return.

    Returns:
      {
        "company": ...,
        "key_officers": {
          "World Registry": [...],
          "PDS": [...],
          "combined": [...]
        },
        "counts": {"wr": int, "pds": int, "combined": int},
        "timing_ms": {"load_caches": float}
      }
    """
    start_time_load_json = datetime.now()
    log.info("company=%s", company_name)
    t0 = perf_counter()
    # Load the JSON data
    
    WR_Data = load_json_cache(wr_path, company_name)
    PDS_Data = load_json_cache(pds_path, company_name)


    print("Length of pds data :",len(PDS_Data))
    print("Length of wr data :",len(WR_Data))
    
    elapsed_ms = (datetime.now() - start_time_load_json).total_seconds() * 1000.0
    log.info("loaded caches in %.1f ms", (perf_counter() - t0) * 1000)

    wr = extract_wr_officers(WR_Data)
    pds = extract_pds_officers(PDS_Data)
    combined = merge_officers_data(wr, pds)
    log.info("merged combined=%d", len(combined))
    payload = {
        "company": company_name,
        "key_officers": {
            "World Registry": fmt_officers(wr, top_n=top_n),
            "PDS": fmt_officers(pds, top_n=top_n),
            "combined": fmt_officers(combined, top_n=top_n * 2),
        },
        "counts": {"wr": len(wr), "pds": len(pds), "combined": len(combined)},
        "timing_ms": {"load_caches": round(elapsed_ms, 2)},
    }
    return payload


@mcp.tool()
async def ping() -> str:
    """Simple health check (handy in MCP Inspector)."""
    return "key_officers_agent ok"


# ────────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run with:  uv run key_officers_agent.py   (or)   python key_officers_agent.py
    mcp.run()
