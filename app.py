"""
Shankar Trading Dashboard V4 Pro
Research-based Streamlit dashboard for DhanHQ.

Install once:
    py -m pip install streamlit requests pandas numpy plotly

Run:
    py -m streamlit run shankar_trading_dashboard_v4_pro.py

Important:
- This version does NOT place real-money orders.
- It uses only 5-minute entry analysis and 15-minute confirmation.
- Live values appear only when a valid Dhan Client ID, Access Token,
  Data API access, underlying Security ID, and expiry are available.
"""

from __future__ import annotations

import json
import math
import time as time_module
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

# ---------------------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------------------
APP_NAME = "Shankar Trading Dashboard"
APP_VERSION = "V10.3 Pro Terminal"
DHAN_BASE = "https://api.dhan.co/v2"
CONFIG_PATH = Path(__file__).with_name(".shankar_dashboard_config.json")
REQUEST_TIMEOUT = 10
DHAN_INSTRUMENT_MASTER = "https://images.dhan.co/api-data/api-scrip-master.csv"
TARGET_INDEX_ALIASES = {
    "NIFTY 50": ["NIFTY 50", "NIFTY"],
    "BANK NIFTY": ["NIFTY BANK", "BANKNIFTY", "BANK NIFTY"],
    "FINNIFTY": ["NIFTY FIN SERVICE", "FINNIFTY", "NIFTY FINANCIAL SERVICES"],
    "MIDCAP SELECT": ["NIFTY MID SELECT", "MIDCPNIFTY", "NIFTY MIDCAP SELECT"],
    "SENSEX": ["SENSEX", "BSE SENSEX"],
    "BANKEX": ["BANKEX", "BSE BANKEX"],
    "INDIA VIX": ["INDIA VIX"],
}

# Dhan's documentation uses Security ID 13 for NIFTY.
# Other IDs remain editable in the sidebar so the user can verify them
# against the current Dhan instrument master.
DEFAULT_MARKETS = {
    "NIFTY 50": {"security_id": 13, "segment": "IDX_I", "chart_segment": "IDX_I", "instrument": "INDEX"},
    "BANK NIFTY": {"security_id": 25, "segment": "IDX_I", "chart_segment": "IDX_I", "instrument": "INDEX"},
    "FINNIFTY": {"security_id": 27, "segment": "IDX_I", "chart_segment": "IDX_I", "instrument": "INDEX"},
    "MIDCAP SELECT": {"security_id": 442, "segment": "IDX_I", "chart_segment": "IDX_I", "instrument": "INDEX"},
}

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# STYLING
# ---------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
    --bg-1:#041124;
    --bg-2:#071d3d;
    --panel:#0b2a55;
    --panel-2:#0a2144;
    --line:rgba(151,199,255,.23);
    --text:#f7fbff;
    --muted:#abc9ec;
    --green:#2ee6a6;
    --red:#ff667c;
    --amber:#ffd166;
    --cyan:#47c9ff;
}
html, body, [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 14% 12%, rgba(26,120,255,.18), transparent 29%),
      radial-gradient(circle at 86% 5%, rgba(0,218,177,.12), transparent 25%),
      linear-gradient(135deg,var(--bg-1),var(--bg-2) 52%,#06162d);
    color:var(--text);
}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stToolbar"] {right:1rem;}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#06152c,#081e3c 56%,#06152c);
    border-right:1px solid var(--line);
}
.block-container {
    max-width:1600px;
    padding-top:.7rem !important;
    padding-bottom:2.5rem;
}
.hero {
    width:100%;
    text-align:center;
    padding:8px 10px 5px;
    margin:0 auto 10px;
}
.hero-title {
    margin:0;
    font-size:clamp(30px,4vw,52px);
    line-height:1.15;
    font-weight:900;
    letter-spacing:-1.2px;
    color:white;
    text-shadow:0 8px 28px rgba(0,0,0,.40);
}
.hero-sub {
    color:#b8d8ff;
    font-size:14px;
    margin-top:7px;
}
.status-strip {
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    align-items:center;
    justify-content:center;
    margin:4px 0 14px;
}
.status-pill {
    padding:7px 12px;
    border-radius:999px;
    background:rgba(255,255,255,.07);
    border:1px solid var(--line);
    color:#dcecff;
    font-size:12px;
}
.metric-card {
    min-height:136px;
    border-radius:18px;
    padding:18px;
    border:1px solid var(--line);
    background:linear-gradient(145deg,rgba(18,76,145,.72),rgba(7,31,67,.90));
    box-shadow:0 14px 34px rgba(0,0,0,.23);
    overflow:hidden;
}
.metric-card .label {
    color:#b8d5f7;
    font-size:13px;
    font-weight:650;
    margin-bottom:10px;
}
.metric-card .value {
    color:white;
    font-size:25px;
    font-weight:900;
    line-height:1.15;
}
.metric-card .sub {
    color:#b9cce5;
    font-size:12px;
    margin-top:11px;
}
.decision-card {
    border-radius:20px;
    padding:22px;
    border:1px solid rgba(255,209,102,.55);
    background:linear-gradient(135deg,rgba(121,83,16,.66),rgba(28,34,47,.92));
    box-shadow:0 16px 38px rgba(0,0,0,.28);
}
.decision-card.buy {
    border-color:rgba(46,230,166,.68);
    background:linear-gradient(135deg,rgba(8,101,72,.72),rgba(16,42,49,.94));
}
.decision-card.sell {
    border-color:rgba(255,102,124,.68);
    background:linear-gradient(135deg,rgba(121,27,47,.76),rgba(43,23,34,.94));
}
.decision-label {color:#cbdaf0;font-size:13px;}
.decision-value {font-size:30px;font-weight:950;margin-top:5px;}
.decision-note {color:#d3dfef;font-size:13px;margin-top:8px;}
.section-title {
    font-size:24px;
    font-weight:900;
    margin:18px 0 10px;
}
.note-box {
    border:1px solid var(--line);
    background:rgba(255,255,255,.055);
    padding:12px 14px;
    border-radius:13px;
    color:#c6d7ed;
    font-size:13px;
}
.good {color:var(--green)!important;}
.bad {color:var(--red)!important;}
.warn {color:var(--amber)!important;}
.cyan {color:var(--cyan)!important;}
div[data-testid="stDataFrame"] {
    border:1px solid var(--line);
    border-radius:14px;
    overflow:hidden;
}
.stButton > button {
    width:100%;
    border-radius:11px;
    font-weight:800;
    min-height:42px;
}
div[data-baseweb="select"] > div,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border-radius:11px !important;
}
[data-testid="stMetricValue"] {color:#fff;}

.price-pulse {
    animation: pricePulse 1.4s ease-in-out infinite;
}
@keyframes pricePulse {
    0%,100% {opacity:1;}
    50% {opacity:.66;}
}
.trade-plan {
    border:1px solid rgba(71,201,255,.35);
    background:linear-gradient(145deg,rgba(9,54,102,.86),rgba(6,27,57,.94));
    border-radius:18px;
    padding:18px;
    box-shadow:0 12px 32px rgba(0,0,0,.23);
}
.trade-plan .big {font-size:25px;font-weight:900;color:#fff;}
.trade-plan .small {font-size:12px;color:#b9cee8;margin-top:7px;}
@media (max-width: 760px) {
    .block-container {padding-left:.55rem!important;padding-right:.55rem!important;padding-top:.25rem!important;}
    .hero-title {font-size:29px!important;letter-spacing:-.5px;}
    .hero-sub {font-size:11px;}
    .status-strip {justify-content:flex-start;gap:5px;}
    .status-pill {padding:5px 8px;font-size:10px;}
    .metric-card {min-height:112px;padding:13px;border-radius:14px;}
    .metric-card .value {font-size:20px;}
    .decision-card {padding:15px;}
    .decision-value {font-size:22px;}
    .section-title {font-size:20px;}
}

.level-grid {
    display:grid;
    grid-template-columns:repeat(5,minmax(0,1fr));
    gap:14px;
    margin:8px 0 20px;
}
.level-card {
    position:relative;
    min-height:118px;
    border-radius:18px;
    padding:17px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.14);
    box-shadow:0 14px 32px rgba(0,0,0,.24);
    transition:transform .18s ease, box-shadow .18s ease;
}
.level-card:hover {
    transform:translateY(-3px);
    box-shadow:0 18px 40px rgba(0,0,0,.32);
}
.level-card::after {
    content:"";
    position:absolute;
    width:95px;
    height:95px;
    right:-28px;
    top:-28px;
    border-radius:50%;
    background:rgba(255,255,255,.10);
}
.level-icon {
    font-size:22px;
    margin-bottom:8px;
}
.level-label {
    font-size:12px;
    color:rgba(255,255,255,.78);
    font-weight:700;
    letter-spacing:.2px;
}
.level-value {
    position:relative;
    z-index:2;
    font-size:27px;
    line-height:1.15;
    color:white;
    font-weight:950;
    margin-top:6px;
}
.level-sub {
    position:relative;
    z-index:2;
    font-size:11px;
    color:rgba(255,255,255,.76);
    margin-top:8px;
}
.spot-card {
    background:linear-gradient(145deg,#087f5b,#0fbf85 54%,#075f45);
}
.atm-card {
    background:linear-gradient(145deg,#9a6500,#e4a900 54%,#805300);
}
.support-card {
    background:linear-gradient(145deg,#0759a8,#0b93e7 54%,#063e75);
}
.resistance-card {
    background:linear-gradient(145deg,#a51f3c,#ef4964 54%,#71142b);
}
.maxpain-card {
    background:linear-gradient(145deg,#6637a3,#9b63e6 54%,#472376);
}
.pivot-grid {
    display:grid;
    grid-template-columns:repeat(7,minmax(0,1fr));
    gap:11px;
    margin:8px 0 20px;
}
.pivot-card {
    border-radius:15px;
    padding:14px 12px;
    min-height:104px;
    border:1px solid rgba(255,255,255,.13);
    box-shadow:0 10px 24px rgba(0,0,0,.20);
}
.pivot-label {
    font-size:11px;
    color:rgba(255,255,255,.78);
    font-weight:750;
}
.pivot-value {
    font-size:20px;
    color:white;
    font-weight:900;
    margin-top:7px;
}
.pivot-main {
    background:linear-gradient(145deg,#9d6b00,#e5ae17);
}
.pivot-high {
    background:linear-gradient(145deg,#0855a0,#1296dc);
}
.pivot-low {
    background:linear-gradient(145deg,#b95d00,#f29426);
}
.pivot-close {
    background:linear-gradient(145deg,#4b5f77,#7d92ab);
}
.support-level {
    background:linear-gradient(145deg,#7c1731,#c12f4c);
}
.resistance-level {
    background:linear-gradient(145deg,#07663f,#14a768);
}
.liquidity-panel {
    border-radius:20px;
    padding:18px;
    border:1px solid rgba(46,230,166,.40);
    background:linear-gradient(145deg,rgba(7,99,70,.75),rgba(5,43,55,.94));
    box-shadow:0 14px 32px rgba(0,0,0,.24);
    margin-top:8px;
}
.liquidity-grid {
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:12px;
}
.liquidity-item {
    background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.10);
    border-radius:14px;
    padding:13px;
}
.liquidity-label {
    font-size:11px;
    color:#bfe7d8;
}
.liquidity-value {
    font-size:22px;
    font-weight:900;
    color:white;
    margin-top:6px;
}
@media (max-width: 1000px) {
    .level-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
    .pivot-grid {grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media (max-width: 650px) {
    .level-grid {grid-template-columns:1fr 1fr;gap:8px;}
    .level-card {min-height:102px;padding:13px;}
    .level-value {font-size:21px;}
    .pivot-grid {grid-template-columns:1fr 1fr;gap:8px;}
    .pivot-value {font-size:18px;}
    .liquidity-grid {grid-template-columns:1fr 1fr;}
}

.signal-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:13px;
    margin:9px 0 17px;
}
.signal-card {
    min-height:125px;
    border-radius:18px;
    padding:16px;
    border:1px solid rgba(255,255,255,.15);
    box-shadow:0 13px 30px rgba(0,0,0,.22);
    position:relative;
    overflow:hidden;
}
.signal-card::after {
    content:"";
    width:90px;
    height:90px;
    border-radius:50%;
    position:absolute;
    right:-24px;
    top:-28px;
    background:rgba(255,255,255,.09);
}
.signal-name {font-size:12px;color:rgba(255,255,255,.78);font-weight:750;}
.signal-reading {font-size:23px;color:white;font-weight:950;margin-top:8px;}
.signal-use {font-size:11px;color:rgba(255,255,255,.77);margin-top:8px;}
.signal-score {
    height:7px;border-radius:99px;background:rgba(0,0,0,.23);
    margin-top:10px;overflow:hidden;
}
.signal-score > span {
    display:block;height:100%;border-radius:99px;
    background:rgba(255,255,255,.83);
}
.signal-bull {background:linear-gradient(145deg,#087a52,#11b97a);}
.signal-bear {background:linear-gradient(145deg,#92213a,#e34a61);}
.signal-blue {background:linear-gradient(145deg,#075598,#0b9ddd);}
.signal-purple {background:linear-gradient(145deg,#5b3292,#9561dc);}
.signal-gold {background:linear-gradient(145deg,#926000,#dba500);}
.signal-orange {background:linear-gradient(145deg,#a84e00,#eb841e);}
.index-strip {
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:8px;
    margin:5px 0 14px;
}
.index-chip {
    border:1px solid rgba(151,199,255,.22);
    background:rgba(255,255,255,.055);
    border-radius:12px;
    padding:9px 8px;
    text-align:center;
    color:#cce4ff;
    font-size:11px;
    font-weight:750;
}
@media(max-width:900px){
    .signal-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
    .index-strip{grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media(max-width:600px){
    .signal-grid{grid-template-columns:1fr 1fr;gap:8px;}
    .signal-card{min-height:112px;padding:12px;}
    .signal-reading{font-size:19px;}
    .index-strip{grid-template-columns:repeat(2,minmax(0,1fr));}
}

/* V10.3 terminal-style additions */
[data-testid="stAppViewContainer"] .block-container {max-width:1900px;padding-left:.7rem!important;padding-right:.7rem!important;}
.pro-summary {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:8px 0 12px;}
.pro-card {background:linear-gradient(145deg,#071827,#0a2236);border:1px solid #173b55;border-radius:12px;padding:13px;min-height:108px;box-shadow:0 10px 28px rgba(0,0,0,.28);}
.pro-card .k {font-size:11px;color:#8db4d4;font-weight:800;text-transform:uppercase;}
.pro-card .v {font-size:24px;font-weight:950;color:#fff;margin-top:9px;}
.pro-card .s {font-size:11px;color:#a9c2d8;margin-top:7px;}
.pro-green .v{color:#35e67d}.pro-red .v{color:#ff5b70}.pro-amber .v{color:#ffd166}.pro-cyan .v{color:#46c9ff}
.level-strip2 {display:grid;grid-template-columns:repeat(7,minmax(0,1fr));background:#071523;border:1px solid #173b55;border-radius:12px;overflow:hidden;margin:8px 0 14px;}
.level2 {padding:11px 10px;text-align:center;border-right:1px solid #173b55}.level2:last-child{border-right:none}.level2 .k{font-size:10px;color:#91abc1;font-weight:800}.level2 .v{font-size:18px;font-weight:950;margin-top:5px}.lv-s .v{color:#35e67d}.lv-r .v{color:#ff5b70}.lv-p .v{color:#ffd166}.lv-x .v{color:#46c9ff}
.trade-strip {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:9px;margin:8px 0 14px;}
.trade-mini {background:#071827;border:1px solid #173b55;border-radius:10px;padding:10px;text-align:center}.trade-mini .k{font-size:10px;color:#8ba9c0}.trade-mini .v{font-size:18px;font-weight:950;color:white;margin-top:5px}.trade-entry .v{color:#46c9ff}.trade-sl .v{color:#ff5b70}.trade-target .v{color:#35e67d}
.option-title {display:flex;justify-content:space-between;gap:10px;align-items:center;background:#071523;border:1px solid #173b55;border-radius:10px;padding:10px 13px;margin-top:6px}.option-title b{color:#46c9ff;font-size:18px}.option-title span{color:#91abc1;font-size:11px}
@media(max-width:1100px){.pro-summary{grid-template-columns:repeat(3,1fr)}.level-strip2{grid-template-columns:repeat(4,1fr)}.trade-strip{grid-template-columns:repeat(3,1fr)}}
@media(max-width:650px){.pro-summary{grid-template-columns:repeat(2,1fr)}.pro-card{min-height:92px;padding:10px}.pro-card .v{font-size:19px}.level-strip2{grid-template-columns:repeat(2,1fr)}.trade-strip{grid-template-columns:repeat(2,1fr)}}

footer {visibility:hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------
@dataclass
class ApiResult:
    ok: bool
    data: Any = None
    message: str = ""
    status_code: int | None = None
    elapsed_ms: int | None = None


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def fmt_num(value: Any, decimals: int = 2, fallback: str = "—") -> str:
    try:
        x = float(value)
        if not math.isfinite(x):
            return fallback
        return f"{x:,.{decimals}f}"
    except (TypeError, ValueError):
        return fallback


def compact_num(value: Any) -> str:
    x = safe_float(value)
    ax = abs(x)
    if ax >= 10_000_000:
        return f"{x/10_000_000:.2f}Cr"
    if ax >= 100_000:
        return f"{x/100_000:.2f}L"
    if ax >= 1_000:
        return f"{x/1_000:.1f}K"
    return f"{x:.0f}"


def now_ist_text() -> str:
    return datetime.now().strftime("%d %b %Y, %I:%M:%S %p")


def is_market_open() -> tuple[bool, str]:
    now = datetime.now()
    weekday = now.weekday() < 5
    session = time(9, 15) <= now.time() <= time(15, 30)
    if weekday and session:
        return True, "Market Open"
    return False, "Market Closed"



def read_secret(name: str, default: str = "") -> str:
    """Read Streamlit Cloud secrets safely; returns default when unavailable."""
    try:
        value = st.secrets.get(name, default)
        return str(value) if value is not None else default
    except Exception:
        return default


def classify_api_error(result: ApiResult) -> str:
    message = str(result.message or "")
    raw = f"{message} {result.data}".upper()
    if any(code in raw for code in ("807", "TOKEN EXPIRED", "EXPIRED TOKEN")):
        return "TOKEN_EXPIRED"
    if any(code in raw for code in ("808", "809", "810", "UNAUTHORIZED", "AUTHENTICATION")):
        return "AUTH_ERROR"
    if "806" in raw or "DATA API" in raw and "SUBSCR" in raw:
        return "DATA_SUBSCRIPTION"
    if "DH-904" in raw or "TOO MANY REQUEST" in raw or result.status_code == 429:
        return "RATE_LIMIT"
    return "OTHER"



def normalize_col(name: Any) -> str:
    return str(name).strip().upper().replace(" ", "_")


@st.cache_data(ttl=43200, show_spinner=False)
def fetch_instrument_master() -> pd.DataFrame:
    """Load Dhan's official compact instrument master and normalize its columns."""
    try:
        df = pd.read_csv(DHAN_INSTRUMENT_MASTER, low_memory=False)
        df.columns = [normalize_col(c) for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()


def first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def discover_indices(master: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Resolve current index Security IDs instead of relying on stale hard-coded IDs."""
    discovered: dict[str, dict[str, Any]] = {}
    if master.empty:
        return discovered

    security_col = first_existing(
        master,
        ["SEM_SMST_SECURITY_ID", "SECURITY_ID", "SM_SECURITY_ID"],
    )
    symbol_col = first_existing(
        master,
        [
            "SEM_CUSTOM_SYMBOL",
            "SEM_TRADING_SYMBOL",
            "DISPLAY_NAME",
            "SYMBOL_NAME",
            "SYMBOL",
        ],
    )
    instrument_col = first_existing(
        master,
        ["SEM_INSTRUMENT_NAME", "INSTRUMENT", "INSTRUMENT_TYPE"],
    )
    exchange_col = first_existing(
        master,
        ["SEM_EXM_EXCH_ID", "EXCHANGE", "EXCHANGE_ID"],
    )

    if not security_col or not symbol_col:
        return discovered

    work = master.copy()
    work["_SEARCH"] = work[symbol_col].fillna("").astype(str).str.upper().str.strip()
    if instrument_col:
        instrument_text = work[instrument_col].fillna("").astype(str).str.upper()
        index_rows = work[instrument_text.str.contains("INDEX", na=False)]
        if not index_rows.empty:
            work = index_rows

    for display_name, aliases in TARGET_INDEX_ALIASES.items():
        chosen = pd.DataFrame()
        for alias in aliases:
            exact = work[work["_SEARCH"] == alias.upper()]
            if not exact.empty:
                chosen = exact
                break
        if chosen.empty:
            for alias in aliases:
                contains = work[work["_SEARCH"].str.contains(alias.upper(), regex=False, na=False)]
                if not contains.empty:
                    chosen = contains
                    break
        if chosen.empty:
            continue

        row = chosen.iloc[0]
        security_id = int(safe_float(row.get(security_col), 0))
        exchange = str(row.get(exchange_col, "NSE")).upper() if exchange_col else "NSE"
        # Dhan v2 uses IDX_I for index values, including BSE index underlyings.
        # BSE_FNO is for derivative contracts, not the underlying index value.
        segment = "IDX_I"
        if security_id > 0:
            discovered[display_name] = {
                "security_id": security_id,
                "segment": segment,
                "chart_segment": segment,
                "instrument": "INDEX",
                "master_symbol": str(row.get(symbol_col, display_name)),
            }
    return discovered


def signal_card_html(
    name: str,
    reading: str,
    use: str,
    score: float,
    css_class: str,
) -> str:
    width = max(0, min(100, safe_float(score, 0)))
    return f"""
<div class="signal-card {css_class}">
  <div class="signal-name">{name}</div>
  <div class="signal-reading">{reading}</div>
  <div class="signal-use">{use}</div>
  <div class="signal-score"><span style="width:{width:.0f}%"></span></div>
</div>
"""


def load_config() -> dict[str, Any]:
    defaults = {
        "client_id": "",
        "access_token": "",
        "market_ids": {name: data["security_id"] for name, data in DEFAULT_MARKETS.items()},
        "india_vix_security_id": 0,
        "refresh_seconds": 5,
    }
    try:
        if CONFIG_PATH.exists():
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            defaults.update(stored)
    except Exception:
        pass
    return defaults


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def make_headers(client_id: str, access_token: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "access-token": access_token.strip(),
        "client-id": client_id.strip(),
        "dhanClientId": client_id.strip(),
    }


def api_call(
    method: str,
    endpoint: str,
    client_id: str,
    access_token: str,
    payload: dict[str, Any] | None = None,
) -> ApiResult:
    if not client_id.strip() or not access_token.strip():
        return ApiResult(False, message="Client ID and Access Token are required.")

    started = time_module.perf_counter()
    try:
        response = requests.request(
            method=method,
            url=f"{DHAN_BASE}{endpoint}",
            headers=make_headers(client_id, access_token),
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        elapsed = round((time_module.perf_counter() - started) * 1000)
        try:
            body = response.json()
        except Exception:
            body = response.text

        if response.ok:
            return ApiResult(True, body, "Success", response.status_code, elapsed)

        if isinstance(body, dict):
            message = (
                body.get("errorMessage")
                or body.get("message")
                or body.get("remarks")
                or body.get("errorCode")
                or str(body)
            )
        else:
            message = str(body)[:250]
        return ApiResult(False, body, message, response.status_code, elapsed)

    except requests.Timeout:
        return ApiResult(False, message="Dhan request timed out.")
    except requests.RequestException as exc:
        return ApiResult(False, message=f"Network error: {exc}")


@st.cache_data(ttl=15, show_spinner=False)
def validate_connection(client_id: str, access_token: str) -> ApiResult:
    return api_call("GET", "/positions", client_id, access_token)


@st.cache_data(ttl=15, show_spinner=False)
def fetch_expiries(
    client_id: str,
    access_token: str,
    underlying_scrip: int,
    underlying_seg: str,
) -> ApiResult:
    payload = {
        "UnderlyingScrip": int(underlying_scrip),
        "UnderlyingSeg": underlying_seg,
    }
    return api_call("POST", "/optionchain/expirylist", client_id, access_token, payload)


@st.cache_data(ttl=4, show_spinner=False)
def fetch_option_chain(
    client_id: str,
    access_token: str,
    underlying_scrip: int,
    underlying_seg: str,
    expiry: str,
) -> ApiResult:
    payload = {
        "UnderlyingScrip": int(underlying_scrip),
        "UnderlyingSeg": underlying_seg,
        "Expiry": expiry,
    }
    return api_call("POST", "/optionchain", client_id, access_token, payload)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_intraday(
    client_id: str,
    access_token: str,
    security_id: int,
    exchange_segment: str,
    instrument: str,
    interval: str,
) -> ApiResult:
    today = date.today()
    payload = {
        "securityId": str(security_id),
        "exchangeSegment": exchange_segment,
        "instrument": instrument,
        "interval": str(interval),
        "oi": False,
        "fromDate": (today - timedelta(days=5)).isoformat(),
        "toDate": (today + timedelta(days=1)).isoformat(),
    }
    return api_call("POST", "/charts/intraday", client_id, access_token, payload)



@st.cache_data(ttl=2, show_spinner=False)
def fetch_ltp(
    client_id: str,
    access_token: str,
    security_id: int,
    exchange_segment: str = "IDX_I",
) -> ApiResult:
    payload = {exchange_segment: [int(security_id)]}
    return api_call("POST", "/marketfeed/ltp", client_id, access_token, payload)


def parse_ltp(raw: Any, security_id: int) -> float:
    if not isinstance(raw, dict):
        return np.nan
    data = raw.get("data", raw)
    if not isinstance(data, dict):
        return np.nan
    for segment_data in data.values():
        if isinstance(segment_data, dict):
            item = segment_data.get(str(security_id), segment_data.get(security_id))
            if isinstance(item, dict):
                return safe_float(item.get("last_price", item.get("ltp")), np.nan)
    return np.nan


def parse_expiries(raw: Any) -> list[str]:
    if not isinstance(raw, dict):
        return []
    data = raw.get("data", raw)
    if isinstance(data, list):
        return [str(x)[:10] for x in data if x]
    if isinstance(data, dict):
        for key in ("data", "expiryList", "expiries", "expiry"):
            value = data.get(key)
            if isinstance(value, list):
                return [str(x)[:10] for x in value if x]
    return []


def parse_candles(raw: Any) -> pd.DataFrame:
    if not isinstance(raw, dict):
        return pd.DataFrame()
    data = raw.get("data", raw)
    if not isinstance(data, dict):
        return pd.DataFrame()

    def get_array(*keys: str) -> list[Any]:
        for key in keys:
            value = data.get(key)
            if isinstance(value, list):
                return value
        return []

    opens = get_array("open", "o")
    highs = get_array("high", "h")
    lows = get_array("low", "l")
    closes = get_array("close", "c")
    volumes = get_array("volume", "v")
    timestamps = get_array("timestamp", "start_Time", "time", "t")

    lengths = [len(x) for x in (opens, highs, lows, closes, timestamps) if x]
    if not lengths:
        return pd.DataFrame()
    n = min(lengths)

    df = pd.DataFrame(
        {
            "timestamp": timestamps[:n],
            "open": opens[:n],
            "high": highs[:n],
            "low": lows[:n],
            "close": closes[:n],
            "volume": (volumes[:n] if volumes else [0] * n),
        }
    )
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Dhan commonly supplies epoch timestamps.
    numeric_ts = pd.to_numeric(df["timestamp"], errors="coerce")
    if numeric_ts.notna().mean() > 0.8:
        unit = "ms" if numeric_ts.dropna().median() > 10_000_000_000 else "s"
        df["datetime"] = pd.to_datetime(numeric_ts, unit=unit, errors="coerce")
    else:
        df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(subset=["datetime", "open", "high", "low", "close"])
    return df.sort_values("datetime").drop_duplicates("datetime").reset_index(drop=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    x = df.copy()

    # EMA
    x["ema9"] = x["close"].ewm(span=9, adjust=False).mean()
    x["ema21"] = x["close"].ewm(span=21, adjust=False).mean()

    # RSI 14
    delta = x["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    x["rsi"] = 100 - (100 / (1 + rs))

    # VWAP, reset by date
    typical = (x["high"] + x["low"] + x["close"]) / 3
    x["_date"] = x["datetime"].dt.date
    pv = typical * x["volume"].replace(0, np.nan)
    x["vwap"] = (
        pv.groupby(x["_date"]).cumsum()
        / x["volume"].replace(0, np.nan).groupby(x["_date"]).cumsum()
    )
    x["vwap"] = x["vwap"].fillna(x["close"].expanding().mean())

    # ATR 14
    prev_close = x["close"].shift(1)
    tr = pd.concat(
        [
            x["high"] - x["low"],
            (x["high"] - prev_close).abs(),
            (x["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    x["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

    # Simplified Supertrend (10, 3)
    period = 10
    multiplier = 3.0
    atr_st = tr.ewm(alpha=1 / period, adjust=False).mean()
    hl2 = (x["high"] + x["low"]) / 2
    upper = hl2 + multiplier * atr_st
    lower = hl2 - multiplier * atr_st

    final_upper = upper.copy()
    final_lower = lower.copy()
    direction = pd.Series(index=x.index, dtype=float)
    supertrend = pd.Series(index=x.index, dtype=float)

    if len(x):
        direction.iloc[0] = 1
        supertrend.iloc[0] = lower.iloc[0]

    for i in range(1, len(x)):
        final_upper.iloc[i] = (
            upper.iloc[i]
            if upper.iloc[i] < final_upper.iloc[i - 1]
            or x["close"].iloc[i - 1] > final_upper.iloc[i - 1]
            else final_upper.iloc[i - 1]
        )
        final_lower.iloc[i] = (
            lower.iloc[i]
            if lower.iloc[i] > final_lower.iloc[i - 1]
            or x["close"].iloc[i - 1] < final_lower.iloc[i - 1]
            else final_lower.iloc[i - 1]
        )

        if x["close"].iloc[i] > final_upper.iloc[i - 1]:
            direction.iloc[i] = 1
        elif x["close"].iloc[i] < final_lower.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        supertrend.iloc[i] = (
            final_lower.iloc[i] if direction.iloc[i] == 1 else final_upper.iloc[i]
        )

    x["supertrend"] = supertrend
    x["st_direction"] = direction
    return x.drop(columns=["_date"], errors="ignore")


def timeframe_signal(df: pd.DataFrame) -> dict[str, Any]:
    result = {
        "available": False,
        "trend": "Waiting",
        "score": 0,
        "rsi": np.nan,
        "vwap": np.nan,
        "supertrend": "—",
        "atr": np.nan,
        "close": np.nan,
        "reasons": [],
    }
    if df.empty or len(df) < 22:
        result["reasons"] = ["Not enough candle data"]
        return result

    row = df.iloc[-1]
    score = 50
    reasons: list[str] = []

    close = safe_float(row.get("close"), np.nan)
    ema9 = safe_float(row.get("ema9"), np.nan)
    ema21 = safe_float(row.get("ema21"), np.nan)
    rsi = safe_float(row.get("rsi"), np.nan)
    vwap = safe_float(row.get("vwap"), np.nan)
    st_dir = safe_float(row.get("st_direction"), 0)

    if close > vwap:
        score += 12
        reasons.append("Price above VWAP")
    else:
        score -= 12
        reasons.append("Price below VWAP")

    if ema9 > ema21:
        score += 12
        reasons.append("EMA 9 above EMA 21")
    else:
        score -= 12
        reasons.append("EMA 9 below EMA 21")

    if st_dir > 0:
        score += 14
        reasons.append("Supertrend bullish")
    elif st_dir < 0:
        score -= 14
        reasons.append("Supertrend bearish")

    if 55 <= rsi <= 70:
        score += 9
        reasons.append("RSI bullish zone")
    elif 30 <= rsi <= 45:
        score -= 9
        reasons.append("RSI bearish zone")
    elif rsi > 75:
        score -= 4
        reasons.append("RSI overbought")
    elif rsi < 25:
        score += 4
        reasons.append("RSI oversold")

    score = int(max(0, min(100, round(score))))
    if score >= 62:
        trend = "Bullish"
    elif score <= 38:
        trend = "Bearish"
    else:
        trend = "Sideways"

    result.update(
        {
            "available": True,
            "trend": trend,
            "score": score,
            "rsi": rsi,
            "vwap": vwap,
            "supertrend": "Bullish" if st_dir > 0 else "Bearish" if st_dir < 0 else "—",
            "atr": safe_float(row.get("atr"), np.nan),
            "close": close,
            "reasons": reasons,
        }
    )
    return result


def extract_option_side(side: Any) -> dict[str, float]:
    if not isinstance(side, dict):
        return {}
    greeks = side.get("greeks") if isinstance(side.get("greeks"), dict) else {}
    return {
        "ltp": safe_float(side.get("last_price", side.get("ltp"))),
        "change": safe_float(side.get("net_change", side.get("change"))),
        "oi": safe_float(side.get("oi")),
        "oi_change": safe_float(side.get("oi_change", side.get("change_oi"))),
        "volume": safe_float(side.get("volume")),
        "iv": safe_float(side.get("implied_volatility", side.get("iv"))),
        "bid": safe_float(side.get("top_bid_price", side.get("bid"))),
        "ask": safe_float(side.get("top_ask_price", side.get("ask"))),
        "delta": safe_float(greeks.get("delta", side.get("delta"))),
        "theta": safe_float(greeks.get("theta", side.get("theta"))),
        "gamma": safe_float(greeks.get("gamma", side.get("gamma"))),
        "vega": safe_float(greeks.get("vega", side.get("vega"))),
    }


def parse_option_chain(raw: Any) -> tuple[pd.DataFrame, float | None]:
    if not isinstance(raw, dict):
        return pd.DataFrame(), None

    data = raw.get("data", raw)
    if not isinstance(data, dict):
        return pd.DataFrame(), None

    spot = data.get("last_price", data.get("underlying_ltp", data.get("spot")))
    spot_value = safe_float(spot, np.nan)
    if not math.isfinite(spot_value):
        spot_value = None

    oc = data.get("oc", data.get("optionChain", data.get("options", {})))
    rows: list[dict[str, Any]] = []

    if isinstance(oc, dict):
        iterable = oc.items()
    elif isinstance(oc, list):
        iterable = [(item.get("strike_price", item.get("strike")), item) for item in oc if isinstance(item, dict)]
    else:
        iterable = []

    for strike_key, item in iterable:
        if not isinstance(item, dict):
            continue
        strike = safe_float(item.get("strike_price", strike_key), np.nan)
        if not math.isfinite(strike):
            continue
        ce = extract_option_side(item.get("ce", item.get("call")))
        pe = extract_option_side(item.get("pe", item.get("put")))
        row = {"Strike": strike}
        for prefix, values in (("CE", ce), ("PE", pe)):
            for key, value in values.items():
                row[f"{prefix}_{key.upper()}"] = value
        rows.append(row)

    if not rows:
        return pd.DataFrame(), spot_value

    df = pd.DataFrame(rows).sort_values("Strike").reset_index(drop=True)
    return df, spot_value


def option_metrics(df: pd.DataFrame, spot: float | None) -> dict[str, Any]:
    result = {
        "pcr": np.nan,
        "max_pain": np.nan,
        "support": np.nan,
        "resistance": np.nan,
        "atm": np.nan,
        "sentiment_score": 50,
    }
    if df.empty:
        return result

    ce_oi = pd.to_numeric(df.get("CE_OI", 0), errors="coerce").fillna(0)
    pe_oi = pd.to_numeric(df.get("PE_OI", 0), errors="coerce").fillna(0)
    total_ce = ce_oi.sum()
    total_pe = pe_oi.sum()
    pcr = total_pe / total_ce if total_ce > 0 else np.nan

    support = df.loc[pe_oi.idxmax(), "Strike"] if pe_oi.max() > 0 else np.nan
    resistance = df.loc[ce_oi.idxmax(), "Strike"] if ce_oi.max() > 0 else np.nan

    if spot is not None:
        atm_idx = (df["Strike"] - spot).abs().idxmin()
        atm = df.loc[atm_idx, "Strike"]
    else:
        atm = np.nan

    # Max pain approximation based on total intrinsic payout at each listed strike.
    strikes = pd.to_numeric(df["Strike"], errors="coerce").to_numpy(dtype=float)
    ce_arr = ce_oi.to_numpy(dtype=float)
    pe_arr = pe_oi.to_numpy(dtype=float)
    pain_values = []
    for settlement in strikes:
        call_pain = np.maximum(settlement - strikes, 0) * ce_arr
        put_pain = np.maximum(strikes - settlement, 0) * pe_arr
        pain_values.append(np.nansum(call_pain + put_pain))
    max_pain = strikes[int(np.nanargmin(pain_values))] if pain_values else np.nan

    sentiment = 50
    if math.isfinite(pcr):
        if 0.9 <= pcr <= 1.3:
            sentiment += 8
        elif 1.3 < pcr <= 1.8:
            sentiment += 14
        elif 0.55 <= pcr < 0.9:
            sentiment -= 12
        elif pcr > 1.8:
            sentiment -= 4  # possible overcrowding
        elif pcr < 0.55:
            sentiment += 4  # possible extreme

    result.update(
        {
            "pcr": pcr,
            "max_pain": max_pain,
            "support": support,
            "resistance": resistance,
            "atm": atm,
            "sentiment_score": int(max(0, min(100, sentiment))),
        }
    )
    return result


def final_decision(
    sig5: dict[str, Any],
    sig15: dict[str, Any],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    if not sig5["available"] or not sig15["available"]:
        return {
            "action": "WAIT — DATA NOT CONNECTED",
            "confidence": 0,
            "bias": "Neutral",
            "css": "",
            "reason": "Valid 5-minute and 15-minute candles are required.",
        }

    # 5m drives entry; 15m carries slightly more confirmation weight.
    technical_score = round(sig5["score"] * 0.45 + sig15["score"] * 0.45 + metrics["sentiment_score"] * 0.10)
    bearish_score = 100 - technical_score
    agreement = sig5["trend"] == sig15["trend"] and sig5["trend"] in ("Bullish", "Bearish")

    if agreement and sig5["trend"] == "Bullish":
        confidence = technical_score
        if confidence >= 80:
            action = "BUY CE SETUP"
            css = "buy"
            reason = "5m entry and 15m confirmation are aligned bullish."
        elif confidence >= 70:
            action = "WAIT FOR BULLISH CONFIRMATION"
            css = ""
            reason = "Bullish bias exists, but confidence is below the 80% entry rule."
        else:
            action = "NO TRADE"
            css = ""
            reason = "Bullish alignment is not strong enough."
        bias = "Bullish"

    elif agreement and sig5["trend"] == "Bearish":
        confidence = bearish_score
        if confidence >= 80:
            action = "BUY PE SETUP"
            css = "sell"
            reason = "5m entry and 15m confirmation are aligned bearish."
        elif confidence >= 70:
            action = "WAIT FOR BEARISH CONFIRMATION"
            css = ""
            reason = "Bearish bias exists, but confidence is below the 80% entry rule."
        else:
            action = "NO TRADE"
            css = ""
            reason = "Bearish alignment is not strong enough."
        bias = "Bearish"

    else:
        confidence = max(technical_score, bearish_score)
        action = "WAIT — TIMEFRAMES NOT ALIGNED"
        css = ""
        reason = "5-minute entry and 15-minute confirmation disagree or are sideways."
        bias = "Mixed"

    return {
        "action": action,
        "confidence": int(max(0, min(100, confidence))),
        "bias": bias,
        "css": css,
        "reason": reason,
    }





def option_flow_intelligence(df: pd.DataFrame, spot: float | None, metrics: dict[str, Any]) -> dict[str, Any]:
    """Compact option-flow readout using OI, OI change, volume, IV and ATM straddle."""
    out = {
        "call_oi": 0.0, "put_oi": 0.0, "call_chg_oi": 0.0, "put_chg_oi": 0.0,
        "call_volume": 0.0, "put_volume": 0.0, "atm_straddle": np.nan,
        "expected_move_pct": np.nan, "flow_bias": "Neutral", "flow_score": 50,
    }
    if df.empty:
        return out
    work = df.copy()
    for col in ("CE_OI", "PE_OI", "CE_OI_CHANGE", "PE_OI_CHANGE", "CE_VOLUME", "PE_VOLUME"):
        work[col] = pd.to_numeric(work.get(col, 0), errors="coerce").fillna(0)
    out["call_oi"] = float(work["CE_OI"].sum())
    out["put_oi"] = float(work["PE_OI"].sum())
    out["call_chg_oi"] = float(work["CE_OI_CHANGE"].sum())
    out["put_chg_oi"] = float(work["PE_OI_CHANGE"].sum())
    out["call_volume"] = float(work["CE_VOLUME"].sum())
    out["put_volume"] = float(work["PE_VOLUME"].sum())

    atm = safe_float(metrics.get("atm"), np.nan)
    if math.isfinite(atm):
        row = work.iloc[(pd.to_numeric(work["Strike"], errors="coerce") - atm).abs().argsort()[:1]]
        if not row.empty:
            row = row.iloc[0]
            straddle = safe_float(row.get("CE_LTP"), 0) + safe_float(row.get("PE_LTP"), 0)
            if straddle > 0:
                out["atm_straddle"] = straddle
                base = safe_float(spot, 0)
                if base > 0:
                    out["expected_move_pct"] = straddle / base * 100

    score = 50
    # Put OI / put OI addition is treated as supportive; call OI / call OI addition as overhead.
    total_oi = max(out["call_oi"] + out["put_oi"], 1.0)
    oi_edge = (out["put_oi"] - out["call_oi"]) / total_oi
    score += max(-12, min(12, oi_edge * 40))
    total_chg = max(abs(out["call_chg_oi"]) + abs(out["put_chg_oi"]), 1.0)
    chg_edge = (out["put_chg_oi"] - out["call_chg_oi"]) / total_chg
    score += max(-10, min(10, chg_edge * 25))
    total_vol = max(out["call_volume"] + out["put_volume"], 1.0)
    vol_edge = (out["put_volume"] - out["call_volume"]) / total_vol
    score += max(-8, min(8, vol_edge * 20))
    score = int(max(0, min(100, round(score))))
    out["flow_score"] = score
    out["flow_bias"] = "Bullish" if score >= 58 else "Bearish" if score <= 42 else "Neutral"
    return out


def select_best_option_contract(
    chain: pd.DataFrame,
    side: str,
    metrics: dict[str, Any],
    max_distance_steps: int = 2,
) -> dict[str, Any]:
    """Rank near-ATM contracts by tradability; avoids blindly selecting ATM."""
    empty = {"ok": False, "strike": np.nan, "entry": np.nan, "score": 0, "spread_pct": np.nan,
             "delta": np.nan, "iv": np.nan, "volume": 0.0, "oi": 0.0, "reason": "No suitable contract"}
    if chain.empty or side not in ("CE", "PE"):
        return empty
    atm = safe_float(metrics.get("atm"), np.nan)
    if not math.isfinite(atm):
        return empty
    work = chain.copy()
    work["_distance"] = (pd.to_numeric(work["Strike"], errors="coerce") - atm).abs()
    strikes = sorted(pd.to_numeric(work["Strike"], errors="coerce").dropna().unique())
    steps = [abs(strikes[i+1]-strikes[i]) for i in range(len(strikes)-1) if strikes[i+1] > strikes[i]]
    step = min(steps) if steps else max(atm * 0.002, 1.0)
    work = work[work["_distance"] <= step * max_distance_steps + 1e-9].copy()
    if work.empty:
        return empty

    best = None
    for _, row in work.iterrows():
        ltp = safe_float(row.get(f"{side}_LTP"), 0)
        bid = safe_float(row.get(f"{side}_BID"), 0)
        ask = safe_float(row.get(f"{side}_ASK"), 0)
        volume = safe_float(row.get(f"{side}_VOLUME"), 0)
        oi = safe_float(row.get(f"{side}_OI"), 0)
        iv = safe_float(row.get(f"{side}_IV"), np.nan)
        delta = abs(safe_float(row.get(f"{side}_DELTA"), np.nan))
        if ltp <= 0:
            continue
        spread = ((ask - bid) / max((ask + bid) / 2, 0.01) * 100) if ask > 0 and bid > 0 and ask >= bid else 99.0
        score = 0.0
        score += max(0, 30 - min(spread, 10) * 5)
        score += min(20, math.log10(max(volume, 1)) * 5)
        score += min(20, math.log10(max(oi, 1)) * 4)
        if math.isfinite(delta):
            score += max(0, 20 - abs(delta - 0.50) * 50)
        if math.isfinite(iv) and 5 <= iv <= 80:
            score += 5
        score += max(0, 5 - safe_float(row.get("_distance"), 0) / max(step, 1) * 2.5)
        candidate = {"ok": spread <= 4.0 and volume >= 100 and oi >= 500,
                     "strike": safe_float(row.get("Strike"), np.nan), "entry": ltp, "score": int(round(score)),
                     "spread_pct": spread, "delta": delta, "iv": iv, "volume": volume, "oi": oi,
                     "reason": f"quality {score:.0f}/100 • spread {spread:.1f}% • vol {compact_num(volume)} • OI {compact_num(oi)}"}
        if best is None or candidate["score"] > best["score"]:
            best = candidate
    return best or empty

def liquidity_filter(
    chain: pd.DataFrame,
    metrics: dict[str, Any],
    max_spread_pct: float = 3.0,
    min_volume: float = 500.0,
    min_oi: float = 1000.0,
) -> dict[str, Any]:
    result = {
        "ok": False,
        "spread_pct": np.nan,
        "volume": 0.0,
        "oi": 0.0,
        "reason": "Option chain unavailable",
    }
    if chain.empty:
        return result
    atm = safe_float(metrics.get("atm"), np.nan)
    if not math.isfinite(atm):
        result["reason"] = "ATM unavailable"
        return result
    row = chain.iloc[(pd.to_numeric(chain["Strike"], errors="coerce") - atm).abs().argsort()[:1]]
    if row.empty:
        return result
    row = row.iloc[0]

    candidates = []
    for side in ("CE", "PE"):
        bid = safe_float(row.get(f"{side}_BID"), 0)
        ask = safe_float(row.get(f"{side}_ASK"), 0)
        ltp = safe_float(row.get(f"{side}_LTP"), 0)
        volume = safe_float(row.get(f"{side}_VOLUME"), 0)
        oi = safe_float(row.get(f"{side}_OI"), 0)
        if ask > 0 and bid > 0:
            spread = (ask - bid) / max((ask + bid) / 2, 0.01) * 100
        else:
            spread = np.inf
        candidates.append((side, spread, volume, oi, ltp))

    best = min(candidates, key=lambda x: x[1]) if candidates else ("—", np.inf, 0, 0, 0)
    side, spread, volume, oi, _ = best
    ok = spread <= max_spread_pct and volume >= min_volume and oi >= min_oi
    reason_parts = []
    if spread > max_spread_pct:
        reason_parts.append(f"spread {spread:.1f}%")
    if volume < min_volume:
        reason_parts.append(f"volume {volume:.0f}")
    if oi < min_oi:
        reason_parts.append(f"OI {oi:.0f}")
    result.update(
        {
            "ok": ok,
            "side": side,
            "spread_pct": spread,
            "volume": volume,
            "oi": oi,
            "reason": "Liquidity OK" if ok else "Weak liquidity: " + ", ".join(reason_parts),
        }
    )
    return result


def simple_backtest(df5: pd.DataFrame, df15: pd.DataFrame) -> dict[str, Any]:
    """Conservative underlying-direction backtest; not an options-P&L backtest."""
    empty = {"trades": 0, "win_rate": np.nan, "avg_move": np.nan, "profit_factor": np.nan}
    if df5.empty or df15.empty or len(df5) < 60 or len(df15) < 25:
        return empty

    five = add_indicators(df5.copy()) if "rsi" not in df5 else df5.copy()
    fifteen = add_indicators(df15.copy()) if "rsi" not in df15 else df15.copy()

    fifteen = fifteen[["datetime", "close", "ema9", "ema21", "vwap", "st_direction", "rsi"]].copy()
    fifteen["trend15"] = np.where(
        (fifteen["close"] > fifteen["vwap"])
        & (fifteen["ema9"] > fifteen["ema21"])
        & (fifteen["st_direction"] > 0),
        1,
        np.where(
            (fifteen["close"] < fifteen["vwap"])
            & (fifteen["ema9"] < fifteen["ema21"])
            & (fifteen["st_direction"] < 0),
            -1,
            0,
        ),
    )

    merged = pd.merge_asof(
        five.sort_values("datetime"),
        fifteen[["datetime", "trend15"]].sort_values("datetime"),
        on="datetime",
        direction="backward",
    )
    merged["trend5"] = np.where(
        (merged["close"] > merged["vwap"])
        & (merged["ema9"] > merged["ema21"])
        & (merged["st_direction"] > 0)
        & merged["rsi"].between(52, 72),
        1,
        np.where(
            (merged["close"] < merged["vwap"])
            & (merged["ema9"] < merged["ema21"])
            & (merged["st_direction"] < 0)
            & merged["rsi"].between(28, 48),
            -1,
            0,
        ),
    )
    merged["signal"] = np.where(merged["trend5"] == merged["trend15"], merged["trend5"], 0)
    merged["future_close"] = merged["close"].shift(-3)
    merged["move"] = (merged["future_close"] - merged["close"]) / merged["close"]
    trades = merged[(merged["signal"] != 0) & merged["future_close"].notna()].copy()
    if trades.empty:
        return empty
    trades["signed_move"] = trades["move"] * trades["signal"]
    wins = trades["signed_move"] > 0
    gross_win = trades.loc[trades["signed_move"] > 0, "signed_move"].sum()
    gross_loss = abs(trades.loc[trades["signed_move"] < 0, "signed_move"].sum())
    return {
        "trades": int(len(trades)),
        "win_rate": float(wins.mean() * 100),
        "avg_move": float(trades["signed_move"].mean() * 100),
        "profit_factor": float(gross_win / gross_loss) if gross_loss > 0 else np.nan,
    }


def calculate_pivots(df: pd.DataFrame) -> dict[str, float]:
    """Classic floor pivots from the most recent completed trading day."""
    empty = {k: np.nan for k in ("P", "R1", "R2", "R3", "S1", "S2", "S3", "PDH", "PDL", "PDC")}
    if df.empty or "datetime" not in df:
        return empty
    x = df.copy()
    x["_day"] = x["datetime"].dt.date
    days = sorted(x["_day"].dropna().unique())
    if not days:
        return empty
    today = date.today()
    completed = [d for d in days if d < today]
    chosen = completed[-1] if completed else days[-1]
    day_df = x[x["_day"] == chosen]
    if day_df.empty:
        return empty
    h = safe_float(day_df["high"].max(), np.nan)
    l = safe_float(day_df["low"].min(), np.nan)
    c = safe_float(day_df.iloc[-1]["close"], np.nan)
    if not all(math.isfinite(v) for v in (h, l, c)):
        return empty
    p = (h + l + c) / 3
    return {
        "P": p,
        "R1": 2 * p - l,
        "S1": 2 * p - h,
        "R2": p + (h - l),
        "S2": p - (h - l),
        "R3": h + 2 * (p - l),
        "S3": l - 2 * (h - p),
        "PDH": h,
        "PDL": l,
        "PDC": c,
    }


def build_trade_plan(
    decision: dict[str, Any],
    chain: pd.DataFrame,
    metrics: dict[str, Any],
    sig5: dict[str, Any],
) -> dict[str, Any]:
    """Build an indicative premium-based plan; never places an order."""
    plan = {
        "side": "WAIT",
        "strike": np.nan,
        "entry": np.nan,
        "sl": np.nan,
        "t1": np.nan,
        "t2": np.nan,
        "t3": np.nan,
        "rr": "—",
        "note": "No trade plan until both timeframes align and confidence reaches 80%.",
    }
    action = str(decision.get("action", ""))
    if chain.empty or not (action.startswith("BUY CE") or action.startswith("BUY PE")):
        return plan

    side = "CE" if action.startswith("BUY CE") else "PE"
    contract = select_best_option_contract(chain, side, metrics)
    if not contract.get("ok"):
        plan["note"] = "V10.3 blocked contract: " + str(contract.get("reason", "weak liquidity/quality"))
        return plan
    entry = safe_float(contract.get("entry"), np.nan)
    if not math.isfinite(entry) or entry <= 0:
        return plan

    # Premium risk is capped near 18%, with a small ATR-sensitive adjustment.
    atr = safe_float(sig5.get("atr"), 0)
    underlying = max(safe_float(sig5.get("close"), 0), 1)
    atr_pct = min(max(atr / underlying, 0), 0.03)
    stop_pct = min(0.22, max(0.14, 0.16 + atr_pct * 2))
    risk = max(entry * stop_pct, 0.05)
    sl = max(entry - risk, 0.05)

    plan.update(
        {
            "side": side,
            "strike": safe_float(contract.get("strike"), np.nan),
            "entry": entry,
            "sl": sl,
            "t1": entry + risk,
            "t2": entry + 2 * risk,
            "t3": entry + 3 * risk,
            "rr": "1:3",
            "note": "V10.3 selected liquid near-ATM contract • " + str(contract.get("reason", "")) + ". Confirm 5m candle close before entry.",
        }
    )
    return plan


def option_chain_styler(
    display: pd.DataFrame,
    atm: float,
    support: float = np.nan,
    resistance: float = np.nan,
) -> Any:
    """High-contrast option-chain styling: green support, red resistance, amber ATM."""
    ce_cols = {c for c in display.columns if str(c).startswith("CE ")}
    pe_cols = {c for c in display.columns if str(c).startswith("PE ")}

    def style_row(row: pd.Series) -> list[str]:
        strike = safe_float(row.get("STRIKE"), np.nan)
        is_atm = math.isfinite(safe_float(atm, np.nan)) and abs(strike - atm) < 0.001
        is_support = math.isfinite(safe_float(support, np.nan)) and abs(strike - support) < 0.001
        is_resistance = math.isfinite(safe_float(resistance, np.nan)) and abs(strike - resistance) < 0.001
        styles: list[str] = []
        for col in row.index:
            if col in ce_cols:
                base = "background-color:#0b2639;color:#e8f7ff;"
            elif col in pe_cols:
                base = "background-color:#2a1721;color:#fff1f4;"
            else:
                base = "background-color:#101d2c;color:#ffffff;font-weight:800;"

            # Use solid colours because Streamlit/pandas Styler renders them more reliably than rgba overlays.
            if is_support and is_resistance:
                base = "background-color:#6f42c1;color:#ffffff;font-weight:950;border-top:2px solid #d8c4ff;border-bottom:2px solid #d8c4ff;"
            elif is_support:
                base = "background-color:#075c3b;color:#ecfff7;font-weight:950;border-top:2px solid #26e6a0;border-bottom:2px solid #26e6a0;"
            elif is_resistance:
                base = "background-color:#721b31;color:#fff2f5;font-weight:950;border-top:2px solid #ff5c78;border-bottom:2px solid #ff5c78;"

            if is_atm:
                if col == "STRIKE":
                    base = "background-color:#d49400;color:#111111;font-weight:950;border:2px solid #ffd166;"
                else:
                    base += "border-top:2px solid #ffd166;border-bottom:2px solid #ffd166;"
            styles.append(base)
        return styles

    return display.style.apply(style_row, axis=1).format(precision=2, na_rep="—")


def option_oi_levels(df: pd.DataFrame) -> dict[str, float]:
    """Return top two PE-OI supports and CE-OI resistances for terminal display."""
    result = {"support1": np.nan, "support2": np.nan, "resistance1": np.nan, "resistance2": np.nan}
    if df.empty:
        return result
    work = df.copy()
    work["CE_OI"] = pd.to_numeric(work.get("CE_OI", 0), errors="coerce").fillna(0)
    work["PE_OI"] = pd.to_numeric(work.get("PE_OI", 0), errors="coerce").fillna(0)
    pe = work.nlargest(2, "PE_OI")
    ce = work.nlargest(2, "CE_OI")
    if len(pe) > 0: result["support1"] = safe_float(pe.iloc[0]["Strike"], np.nan)
    if len(pe) > 1: result["support2"] = safe_float(pe.iloc[1]["Strike"], np.nan)
    if len(ce) > 0: result["resistance1"] = safe_float(ce.iloc[0]["Strike"], np.nan)
    if len(ce) > 1: result["resistance2"] = safe_float(ce.iloc[1]["Strike"], np.nan)
    return result

def chart_figure(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        )
    )
    if "vwap" in df:
        fig.add_trace(go.Scatter(x=df["datetime"], y=df["vwap"], name="VWAP", mode="lines"))
    if "ema9" in df:
        fig.add_trace(go.Scatter(x=df["datetime"], y=df["ema9"], name="EMA 9", mode="lines"))
    if "ema21" in df:
        fig.add_trace(go.Scatter(x=df["datetime"], y=df["ema21"], name="EMA 21", mode="lines"))
    if "supertrend" in df:
        fig.add_trace(go.Scatter(x=df["datetime"], y=df["supertrend"], name="Supertrend", mode="lines"))

    fig.update_layout(
        title=title,
        height=470,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4,17,36,.55)",
        font=dict(color="#eaf4ff"),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    return fig



def colorful_level_card(
    label: str,
    value: str,
    sub: str,
    icon: str,
    css_class: str,
) -> str:
    return f"""
<div class="level-card {css_class}">
  <div class="level-icon">{icon}</div>
  <div class="level-label">{label}</div>
  <div class="level-value">{value}</div>
  <div class="level-sub">{sub}</div>
</div>
"""


def pivot_level_card(label: str, value: str, css_class: str) -> str:
    return f"""
<div class="pivot-card {css_class}">
  <div class="pivot-label">{label}</div>
  <div class="pivot-value">{value}</div>
</div>
"""


def metric_card(label: str, value: str, sub: str, value_class: str = "") -> None:
    st.markdown(
        f"""
<div class="metric-card">
  <div class="label">{label}</div>
  <div class="value {value_class}">{value}</div>
  <div class="sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
config = load_config()

# Persistent state fixes the V4 problem where clicking Validate connected
# successfully but the next Streamlit rerun returned to FAST START/OFFLINE.
if "live_enabled" not in st.session_state:
    st.session_state.live_enabled = False
if "last_validation_message" not in st.session_state:
    st.session_state.last_validation_message = ""
if "market_selector" not in st.session_state:
    st.session_state.market_selector = "NIFTY 50"

def select_market_from_button(name: str) -> None:
    """Synchronize the top index buttons with the sidebar selector."""
    st.session_state.market_selector = name

instrument_master = fetch_instrument_master()
discovered_indices = discover_indices(instrument_master)
AVAILABLE_MARKETS = {
    name: discovered_indices.get(name, data)
    for name, data in DEFAULT_MARKETS.items()
}
for extra_name in ("SENSEX", "BANKEX"):
    if extra_name in discovered_indices:
        AVAILABLE_MARKETS[extra_name] = discovered_indices[extra_name]

# Compact Dhan login popup for desktop + mobile.
# Credentials are intentionally kept out of the main dashboard until the lock icon is opened.
client_id = read_secret("DHAN_CLIENT_ID", str(config.get("client_id", "")))
access_token = read_secret("DHAN_ACCESS_TOKEN", str(config.get("access_token", "")))
validate_clicked = False

login_col, _login_spacer = st.columns([1, 12])
with login_col:
    with st.popover("🔐", help="Open Dhan Client ID / Access Token"):
        st.markdown("### Dhan Connection")
        client_id = st.text_input(
            "Dhan Client ID",
            value=client_id,
            placeholder="Example: 1100xxxxxx",
            key="popup_dhan_client_id",
        )
        access_token = st.text_area(
            "Dhan Access Token",
            value=access_token,
            height=150,
            placeholder="Paste the current Dhan access token",
            key="popup_dhan_access_token",
        )
        p1, p2 = st.columns(2)
        with p1:
            save_clicked = st.button("💾 Save", use_container_width=True, key="popup_save_dhan")
        with p2:
            validate_clicked = st.button("✅ Connect", use_container_width=True, key="popup_connect_dhan")

        if save_clicked:
            if client_id.strip() and access_token.strip():
                config["client_id"] = client_id.strip()
                config["access_token"] = access_token.strip()
                save_config(config)
                st.success("Credentials saved.")
            else:
                st.warning("Enter Client ID and Access Token.")

        if validate_clicked:
            if client_id.strip() and access_token.strip():
                config["client_id"] = client_id.strip()
                config["access_token"] = access_token.strip()
                save_config(config)
                st.session_state.live_enabled = True
                st.cache_data.clear()
            else:
                st.session_state.live_enabled = False
                st.warning("Enter Client ID and Access Token.")

        if st.button("🗑 Clear Token", use_container_width=True, key="popup_clear_dhan"):
            config["client_id"] = ""
            config["access_token"] = ""
            save_config(config)
            st.session_state.live_enabled = False
            st.cache_data.clear()
            st.success("Token cleared.")

with st.sidebar:
    st.header("⚙️ Market Setup")
    if discovered_indices:
        st.caption(f"Official Dhan master: {len(discovered_indices)} index mappings resolved.")
    else:
        st.warning("Instrument master unavailable; fallback IDs are being used.")
    if st.session_state.market_selector not in AVAILABLE_MARKETS:
        st.session_state.market_selector = next(iter(AVAILABLE_MARKETS))
    selected_market = st.selectbox(
        "Market",
        list(AVAILABLE_MARKETS.keys()),
        key="market_selector",
    )
    market_info = AVAILABLE_MARKETS[selected_market]

    stored_ids = config.get("market_ids", {})
    security_id = int(
        st.number_input(
            "Underlying Security ID",
            min_value=1,
            step=1,
            value=int(stored_ids.get(selected_market, market_info["security_id"])),
            help="Verify this ID from Dhan's current instrument master.",
        )
    )

    if st.button("Save Market ID", use_container_width=True):
        config.setdefault("market_ids", {})[selected_market] = security_id
        save_config(config)
        st.success("Market ID saved.")

    auto_load = st.toggle(
        "Keep Live Data ON",
        value=bool(st.session_state.live_enabled),
        help="After Connect Live succeeds, this remains ON across dropdown and tab reruns.",
    )
    st.session_state.live_enabled = bool(auto_load)

    refresh_seconds = st.select_slider(
        "Live refresh interval",
        options=[3, 5, 10, 15, 30, 60],
        value=int(config.get("refresh_seconds", 5)),
        help="Option chain is never requested faster than Dhan's 3-second limit.",
    )
    config["refresh_seconds"] = int(refresh_seconds)

    auto_refresh = st.toggle(
        "Auto Refresh",
        value=False,
        help="Requires streamlit-autorefresh. Manual Refresh still works without it.",
    )
    refresh_clicked = st.button("🔄 Refresh Now", use_container_width=True)
    if refresh_clicked:
        st.session_state.live_enabled = True
        st.cache_data.clear()

    st.subheader("🇮🇳 India VIX Setup")
    auto_vix_id = int(discovered_indices.get("INDIA VIX", {}).get("security_id", 0))
    india_vix_security_id = int(
        st.number_input(
            "India VIX Security ID",
            min_value=0,
            step=1,
            value=int(auto_vix_id or config.get("india_vix_security_id", 0)),
            help="V9 resolves this automatically from Dhan's official instrument master. Manual override remains available.",
        )
    )
    if auto_vix_id > 0:
        st.caption(f"✅ India VIX auto-detected: Security ID {auto_vix_id}")
    config["india_vix_security_id"] = india_vix_security_id
    if st.button("Save V7 Settings", use_container_width=True):
        save_config(config)
        st.success("Refresh and VIX settings saved.")

    st.divider()
    st.caption(
        "Security: On Streamlit Cloud, use Secrets named DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN. "
        "Local Save writes a hidden JSON beside this file; never upload that JSON to GitHub."
    )

# ---------------------------------------------------------------------
# CONNECTION & FETCH
# ---------------------------------------------------------------------
credentials_present = bool(client_id.strip() and access_token.strip())
should_check_connection = credentials_present and (
    validate_clicked or refresh_clicked or st.session_state.live_enabled
)
connection = (
    validate_connection(client_id.strip(), access_token.strip())
    if should_check_connection
    else ApiResult(False, message="Not checked")
)

if validate_clicked:
    if connection.ok:
        st.session_state.live_enabled = True
        st.session_state.last_validation_message = (
            f"Dhan API connected successfully ({connection.elapsed_ms or 0} ms)."
        )
    else:
        st.session_state.live_enabled = False
        st.session_state.last_validation_message = f"Connection failed: {connection.message}"

load_live = credentials_present and connection.ok and st.session_state.live_enabled

if auto_refresh and load_live:
    if st_autorefresh is not None:
        st_autorefresh(
            interval=max(int(refresh_seconds), 3) * 1000,
            key="v7_live_refresh",
        )
    else:
        st.sidebar.warning(
            "Auto Refresh requires: py -m pip install streamlit-autorefresh"
        )

expiries: list[str] = []
expiry_result = ApiResult(False, message="Not loaded")
if load_live:
    expiry_result = fetch_expiries(
        client_id.strip(),
        access_token.strip(),
        security_id,
        market_info["segment"],
    )
    if expiry_result.ok:
        expiries = parse_expiries(expiry_result.data)

# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------
market_open, market_label = is_market_open()
connection_label = "Dhan Connected" if connection.ok else "Dhan Not Connected"
connection_class = "good" if connection.ok else "warn"
market_class = "good" if market_open else "bad"

st.markdown(
    f"""
<div class="hero">
  <div class="hero-title">📈 {APP_NAME}</div>
  <div class="hero-sub">5-minute Entry / Exit / SL / Targets • 15-minute Trend Confirmation only • Live Multi-Index Option Terminal</div>
</div>
<div class="status-strip">
  <div class="status-pill {market_class}">● {market_label}</div>
  <div class="status-pill {connection_class}">● {connection_label}</div>
  <div class="status-pill">🕒 {now_ist_text()}</div>
  <div class="status-pill">⚡ Fast-load mode</div>
</div>
""",
    unsafe_allow_html=True,
)

# Real clickable index selector. V9 used decorative HTML chips, which could never
# change the selected market. Button callbacks update Session State before rerun.
market_names = list(AVAILABLE_MARKETS.keys())
market_cols = st.columns(len(market_names))
for col, name in zip(market_cols, market_names):
    with col:
        st.button(
            name,
            key=f"market_btn_{name}",
            type="primary" if name == selected_market else "secondary",
            use_container_width=True,
            on_click=select_market_from_button,
            args=(name,),
        )

if st.session_state.last_validation_message:
    if connection.ok and st.session_state.live_enabled:
        st.success(st.session_state.last_validation_message)
    elif validate_clicked:
        st.error(st.session_state.last_validation_message)

if should_check_connection and not connection.ok:
    error_kind = classify_api_error(connection)
    if error_kind == "TOKEN_EXPIRED":
        st.error("🔑 Dhan Access Token expired — generate and paste a new token.")
    elif error_kind == "AUTH_ERROR":
        st.error("🔐 Authentication failed — check Client ID and Access Token.")
    elif error_kind == "DATA_SUBSCRIPTION":
        st.error("📡 Dhan Data API subscription/access is unavailable for this account.")
    elif error_kind == "RATE_LIMIT":
        st.warning("⏳ Dhan API rate limit reached — wait a few seconds before refreshing.")

# Expiry selector appears in main area, avoiding a blank top-right box.
selector_col1, selector_col2, selector_col3 = st.columns([2.2, 1.5, 1])
with selector_col1:
    st.markdown(f"### {selected_market}")
    st.caption(f"Security ID: {security_id} • Segment: {market_info['segment']} • {market_info.get('master_symbol', 'Index')}")
with selector_col2:
    selected_expiry = st.selectbox(
        "Expiry",
        options=expiries if expiries else ["Expiry not loaded — see API Log"],
        disabled=not bool(expiries),
    )
with selector_col3:
    st.markdown("### Data Status")
    st.caption("LIVE DATA ON" if load_live else "OFFLINE — CLICK CONNECT LIVE")

if load_live and not expiries:
    detail = expiry_result.message or "Unknown expiry-list error"
    st.error(
        "Dhan account is connected, but expiry data did not load. "
        f"API response: {detail}. Open the API Log tab for HTTP details."
    )

chain_result = ApiResult(False, message="Not loaded")
df_chain = pd.DataFrame()
spot = None
df5 = pd.DataFrame()
df15 = pd.DataFrame()

if load_live and expiries:
    chain_result = fetch_option_chain(
        client_id.strip(),
        access_token.strip(),
        security_id,
        market_info["segment"],
        selected_expiry,
    )
    if chain_result.ok:
        df_chain, spot = parse_option_chain(chain_result.data)

    result5 = fetch_intraday(
        client_id.strip(),
        access_token.strip(),
        security_id,
        market_info["chart_segment"],
        market_info["instrument"],
        "5",
    )
    result15 = fetch_intraday(
        client_id.strip(),
        access_token.strip(),
        security_id,
        market_info["chart_segment"],
        market_info["instrument"],
        "15",
    )
    if result5.ok:
        df5 = add_indicators(parse_candles(result5.data))
    if result15.ok:
        df15 = add_indicators(parse_candles(result15.data))
else:
    result5 = ApiResult(False, message="Live load disabled")
    result15 = ApiResult(False, message="Live load disabled")

vix_result = ApiResult(False, message="VIX disabled")
india_vix = np.nan
if load_live and india_vix_security_id > 0:
    vix_result = fetch_ltp(
        client_id.strip(),
        access_token.strip(),
        india_vix_security_id,
        discovered_indices.get("INDIA VIX", {}).get("segment", "IDX_I"),
    )
    if vix_result.ok:
        india_vix = parse_ltp(vix_result.data, india_vix_security_id)

sig5 = timeframe_signal(df5)
sig15 = timeframe_signal(df15)
metrics = option_metrics(df_chain, spot)
flow = option_flow_intelligence(df_chain, spot, metrics)
oi_levels = option_oi_levels(df_chain)
decision = final_decision(sig5, sig15, metrics)
# V10.3 confirmation veto: strong opposite option-flow prevents a fresh BUY setup.
if decision["action"].startswith("BUY CE") and flow["flow_score"] <= 38:
    decision.update({"action": "WAIT — OPTION FLOW CONFLICT", "css": "", "reason": "Technical setup is bullish, but option-chain flow is strongly bearish."})
elif decision["action"].startswith("BUY PE") and flow["flow_score"] >= 62:
    decision.update({"action": "WAIT — OPTION FLOW CONFLICT", "css": "", "reason": "Technical setup is bearish, but option-chain flow is strongly bullish."})
pivots = calculate_pivots(df15 if not df15.empty else df5)
liquidity = liquidity_filter(df_chain, metrics)
backtest = simple_backtest(df5, df15)
trade_plan = build_trade_plan(decision, df_chain, metrics, sig5)

if trade_plan["side"] != "WAIT" and not liquidity["ok"]:
    trade_plan["side"] = "WAIT"
    trade_plan["note"] = liquidity["reason"] + ". Trade blocked by V10.3 liquidity/data-quality filter."

if not market_open and decision["action"].startswith("BUY"):
    decision["action"] = "MARKET CLOSED — LAST DATA ONLY"
    decision["css"] = ""
    decision["reason"] = "Signals are historical snapshots. New live entry is disabled outside market hours."

# ---------------------------------------------------------------------
# V10.3 PRO TERMINAL SUMMARY — ONLY 5m EXECUTION + 15m TREND
# ---------------------------------------------------------------------
aligned = sig5["trend"] == sig15["trend"] and sig5["trend"] in ("Bullish", "Bearish")
alignment_text = sig5["trend"] if aligned else "Mixed"
alignment_class = "pro-green" if alignment_text == "Bullish" else "pro-red" if alignment_text == "Bearish" else "pro-amber"
final_class = "pro-green" if "BUY CE" in decision["action"] else "pro-red" if "BUY PE" in decision["action"] else "pro-amber"
vix_text = fmt_num(india_vix, 2) if math.isfinite(safe_float(india_vix, np.nan)) else "—"

st.markdown(
    f"""
<div class="pro-summary">
  <div class="pro-card {'pro-green' if sig5['trend']=='Bullish' else 'pro-red' if sig5['trend']=='Bearish' else 'pro-amber'}"><div class="k">5-Minute Execution</div><div class="v">{sig5['trend']}</div><div class="s">Entry/Exit/SL/Targets • Score {sig5['score']}%</div></div>
  <div class="pro-card {'pro-green' if sig15['trend']=='Bullish' else 'pro-red' if sig15['trend']=='Bearish' else 'pro-amber'}"><div class="k">15-Minute Trend Only</div><div class="v">{sig15['trend']}</div><div class="s">Trend confirmation only • RSI {fmt_num(sig15['rsi'],1)}</div></div>
  <div class="pro-card {alignment_class}"><div class="k">Trend Alignment</div><div class="v">{alignment_text}</div><div class="s">5m execution + 15m trend</div></div>
  <div class="pro-card pro-cyan"><div class="k">AI Confidence</div><div class="v">{decision['confidence']}%</div><div class="s">80%+ setup • 70–79 wait • below 70 no trade</div></div>
  <div class="pro-card {final_class}"><div class="k">Final Bias</div><div class="v">{decision['action']}</div><div class="s">{decision['reason']}</div></div>
  <div class="pro-card pro-cyan"><div class="k">India VIX</div><div class="v">{vix_text}</div><div class="s">PCR {fmt_num(metrics['pcr'],2)} • Flow {flow['flow_bias']} {flow['flow_score']}%</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"""
<div class="level-strip2">
 <div class="level2 lv-s"><div class="k">SUPPORT 1</div><div class="v">{fmt_num(oi_levels['support1'],0)}</div></div>
 <div class="level2 lv-s"><div class="k">SUPPORT 2</div><div class="v">{fmt_num(oi_levels['support2'],0)}</div></div>
 <div class="level2 lv-p"><div class="k">PIVOT</div><div class="v">{fmt_num(pivots['P'],0)}</div></div>
 <div class="level2 lv-r"><div class="k">RESISTANCE 1</div><div class="v">{fmt_num(oi_levels['resistance1'],0)}</div></div>
 <div class="level2 lv-r"><div class="k">RESISTANCE 2</div><div class="v">{fmt_num(oi_levels['resistance2'],0)}</div></div>
 <div class="level2 lv-x"><div class="k">SPOT</div><div class="v">{fmt_num(spot,2)}</div></div>
 <div class="level2 lv-p"><div class="k">ATM</div><div class="v">{fmt_num(metrics['atm'],0)}</div></div>
</div>
""", unsafe_allow_html=True)

# Entry/SL/Targets are calculated strictly from 5-minute ATR and live option premium.
if trade_plan["side"] != "WAIT":
    st.markdown(f"""
<div class="trade-strip">
 <div class="trade-mini"><div class="k">CONTRACT</div><div class="v">{trade_plan['strike']:.0f} {trade_plan['side']}</div></div>
 <div class="trade-mini trade-entry"><div class="k">5m ENTRY</div><div class="v">₹{trade_plan['entry']:.2f}</div></div>
 <div class="trade-mini trade-sl"><div class="k">5m STOP-LOSS</div><div class="v">₹{trade_plan['sl']:.2f}</div></div>
 <div class="trade-mini trade-target"><div class="k">TARGET 1</div><div class="v">₹{trade_plan['t1']:.2f}</div></div>
 <div class="trade-mini trade-target"><div class="k">TARGET 2</div><div class="v">₹{trade_plan['t2']:.2f}</div></div>
 <div class="trade-mini trade-target"><div class="k">TARGET 3</div><div class="v">₹{trade_plan['t3']:.2f}</div></div>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f'<div class="note-box"><b>5m Trade Plan:</b> WAIT — {trade_plan["note"]} &nbsp; <b>15m is used only for trend confirmation.</b></div>', unsafe_allow_html=True)

st.markdown(
    f"""
<div class="note-box"><b>V10.3 Option Intelligence:</b> Flow <b>{flow['flow_bias']} ({flow['flow_score']}%)</b> • ATM Straddle <b>₹{fmt_num(flow['atm_straddle'],2)}</b> • Premium-implied move <b>{fmt_num(flow['expected_move_pct'],2)}%</b> • Put Vol {compact_num(flow['put_volume'])} vs Call Vol {compact_num(flow['call_volume'])}. Contract selection now ranks near-ATM strikes by spread, volume, OI, Delta and IV.</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------
overview_tab, trade_tab, chart_tab, chain_tab, backtest_tab, risk_tab, log_tab = st.tabs(
    ["🏠 Overview", "🎯 Trade Plan", "📊 5m & 15m Charts", "⛓ Option Chain", "🧪 Backtest", "🛡 Risk Calculator", "🧾 API Log"]
)

with overview_tab:
    st.markdown("### 🌈 Key Levels")
    st.markdown(
        f"""
<div class="level-grid">
{colorful_level_card("SPOT PRICE", fmt_num(spot, 2), "Current underlying value", "📍", "spot-card")}
{colorful_level_card("ATM STRIKE", fmt_num(metrics["atm"], 0), "Nearest active strike", "🎯", "atm-card")}
{colorful_level_card("SUPPORT", fmt_num(metrics["support"], 0), "Highest Put OI", "🛡️", "support-card")}
{colorful_level_card("RESISTANCE", fmt_num(metrics["resistance"], 0), "Highest Call OI", "🚧", "resistance-card")}
{colorful_level_card("MAX PAIN", fmt_num(metrics["max_pain"], 0), "OI-based settlement zone", "🧲", "maxpain-card")}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 🎨 Previous-Day Levels & Classic Pivots")
    st.markdown(
        f"""
<div class="pivot-grid">
{pivot_level_card("PREVIOUS HIGH", fmt_num(pivots["PDH"], 2), "pivot-high")}
{pivot_level_card("PIVOT", fmt_num(pivots["P"], 2), "pivot-main")}
{pivot_level_card("PREVIOUS LOW", fmt_num(pivots["PDL"], 2), "pivot-low")}
{pivot_level_card("PREVIOUS CLOSE", fmt_num(pivots["PDC"], 2), "pivot-close")}
{pivot_level_card("S1", fmt_num(pivots["S1"], 2), "support-level")}
{pivot_level_card("S2", fmt_num(pivots["S2"], 2), "support-level")}
{pivot_level_card("S3", fmt_num(pivots["S3"], 2), "support-level")}
{pivot_level_card("R1", fmt_num(pivots["R1"], 2), "resistance-level")}
{pivot_level_card("R2", fmt_num(pivots["R2"], 2), "resistance-level")}
{pivot_level_card("R3", fmt_num(pivots["R3"], 2), "resistance-level")}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 💧 Liquidity Gate")
    liquidity_status = "PASS" if liquidity["ok"] else "BLOCK"
    status_icon = "✅" if liquidity["ok"] else "⛔"
    st.markdown(
        f"""
<div class="liquidity-panel">
  <div class="liquidity-grid">
    <div class="liquidity-item">
      <div class="liquidity-label">STATUS</div>
      <div class="liquidity-value">{status_icon} {liquidity_status}</div>
    </div>
    <div class="liquidity-item">
      <div class="liquidity-label">BEST SPREAD</div>
      <div class="liquidity-value">{fmt_num(liquidity["spread_pct"], 2)}%</div>
    </div>
    <div class="liquidity-item">
      <div class="liquidity-label">VOLUME</div>
      <div class="liquidity-value">{compact_num(liquidity["volume"])}</div>
    </div>
    <div class="liquidity-item">
      <div class="liquidity-label">OPEN INTEREST</div>
      <div class="liquidity-value">{compact_num(liquidity["oi"])}</div>
    </div>
  </div>
  <div class="level-sub" style="margin-top:12px;">{liquidity["reason"]}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Signal Checklist")
    trend5_class = "signal-bull" if sig5["trend"] == "Bullish" else "signal-bear" if sig5["trend"] == "Bearish" else "signal-gold"
    trend15_class = "signal-bull" if sig15["trend"] == "Bullish" else "signal-bear" if sig15["trend"] == "Bearish" else "signal-gold"
    st.markdown(
        f"""
<div class="signal-grid">
{signal_card_html("5-MINUTE TREND", sig5["trend"], f'Entry score {sig5["score"]}%', sig5["score"], trend5_class)}
{signal_card_html("5-MINUTE VWAP", fmt_num(sig5["vwap"], 2), "Price relationship filter", sig5["score"], "signal-blue")}
{signal_card_html("5-MINUTE SUPERTREND", sig5["supertrend"], "Primary entry direction", sig5["score"], "signal-purple")}
{signal_card_html("15-MINUTE TREND", sig15["trend"], f'Confirmation score {sig15["score"]}%', sig15["score"], trend15_class)}
{signal_card_html("15-MINUTE SUPERTREND", sig15["supertrend"], "Higher-timeframe confirmation", sig15["score"], "signal-gold")}
{signal_card_html("OPTION PCR", fmt_num(metrics["pcr"], 2), f'Sentiment score {metrics["sentiment_score"]}%', metrics["sentiment_score"], "signal-orange")}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="note-box">
<b>Decision rules:</b> 80% and above = eligible BUY CE/BUY PE setup;
70–79% = WAIT for confirmation; below 70% = NO TRADE.
A signal is blocked when 5-minute and 15-minute trends do not agree.
</div>
""",
        unsafe_allow_html=True,
    )


with trade_tab:
    st.markdown("### Indicative Entry, Stop-Loss & Targets")
    if trade_plan["side"] == "WAIT":
        st.warning(trade_plan["note"])
        st.markdown(
            """
<div class="note-box">
The dashboard intentionally blocks a trade when 5-minute and 15-minute signals disagree,
when confidence is below 80%, or when live premium data is unavailable.
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        side_text = f"{trade_plan['strike']:.0f} {trade_plan['side']}"
        st.markdown(
            f"""
<div class="trade-plan">
  <div class="small">SELECTED ATM CONTRACT</div>
  <div class="big">{side_text}</div>
  <div class="small">{trade_plan['note']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        t1, t2, t3, t4, t5, t6 = st.columns(6)
        t1.metric("Entry", f"₹{trade_plan['entry']:.2f}")
        t2.metric("Stop-Loss", f"₹{trade_plan['sl']:.2f}")
        t3.metric("Target 1", f"₹{trade_plan['t1']:.2f}")
        t4.metric("Target 2", f"₹{trade_plan['t2']:.2f}")
        t5.metric("Target 3", f"₹{trade_plan['t3']:.2f}")
        t6.metric("Max R:R", trade_plan["rr"])
        st.error(
            "This is an indicative decision-support plan, not a guaranteed call. "
            "Do not enter without checking bid–ask spread, liquidity and candle confirmation."
        )

with chart_tab:
    if df5.empty and df15.empty:
        st.info("Turn on live data or press Refresh Live Data after validating Dhan credentials.")
    else:
        if not df5.empty:
            st.plotly_chart(chart_figure(df5.tail(120), f"{selected_market} — 5-Minute Entry Chart"), use_container_width=True)
        else:
            st.warning(f"5-minute chart unavailable: {result5.message}")

        if not df15.empty:
            st.plotly_chart(chart_figure(df15.tail(120), f"{selected_market} — 15-Minute Confirmation Chart"), use_container_width=True)
        else:
            st.warning(f"15-minute chart unavailable: {result15.message}")

with chain_tab:
    st.markdown(f'<div class="option-title"><b>OPTION CHAIN — {selected_market}</b><span>🟢 Support • 🔴 Resistance • 🟡 ATM • 5m execution / 15m trend</span></div>', unsafe_allow_html=True)
    mobile_compact = st.toggle("📱 Compact mobile option chain", value=False)
    strike_count = 7 if mobile_compact else 21
    if df_chain.empty:
        st.info("No live option-chain data loaded. Validate Dhan, load expiries, then refresh.")
        if chain_result.message not in ("Not loaded", ""):
            st.caption(chain_result.message)
    else:
        display = df_chain.copy()

        # Show strikes nearest spot first while keeping a clean CE | Strike | PE layout.
        if spot is not None:
            display["_distance"] = (display["Strike"] - spot).abs()
            display = display.nsmallest(strike_count, "_distance").sort_values("Strike").drop(columns="_distance")
        else:
            display = display.head(strike_count)

        wanted = [
            "CE_OI", "CE_OI_CHANGE", "CE_VOLUME", "CE_IV", "CE_DELTA",
            "CE_THETA", "CE_LTP", "CE_BID", "CE_ASK",
            "Strike",
            "PE_BID", "PE_ASK", "PE_LTP", "PE_THETA", "PE_DELTA",
            "PE_IV", "PE_VOLUME", "PE_OI_CHANGE", "PE_OI",
        ]
        if not mobile_compact:
            wanted = [
                "CE_OI", "CE_OI_CHANGE", "CE_VOLUME", "CE_IV", "CE_DELTA", "CE_GAMMA", "CE_VEGA",
                "CE_THETA", "CE_LTP", "CE_BID", "CE_ASK",
                "Strike",
                "PE_BID", "PE_ASK", "PE_LTP", "PE_THETA", "PE_DELTA", "PE_GAMMA", "PE_VEGA",
                "PE_IV", "PE_VOLUME", "PE_OI_CHANGE", "PE_OI",
            ]
        for col in wanted:
            if col not in display:
                display[col] = 0.0

        rename = {
            "CE_OI": "CE OI", "CE_OI_CHANGE": "CE Chg OI", "CE_VOLUME": "CE Vol",
            "CE_IV": "CE IV", "CE_DELTA": "CE Δ", "CE_GAMMA": "CE Γ",
            "CE_VEGA": "CE Vega", "CE_THETA": "CE Θ",
            "CE_LTP": "CE LTP", "CE_BID": "CE Bid", "CE_ASK": "CE Ask",
            "PE_BID": "PE Bid", "PE_ASK": "PE Ask", "PE_LTP": "PE LTP",
            "PE_THETA": "PE Θ", "PE_DELTA": "PE Δ", "PE_GAMMA": "PE Γ",
            "PE_VEGA": "PE Vega", "PE_IV": "PE IV",
            "PE_VOLUME": "PE Vol", "PE_OI_CHANGE": "PE Chg OI", "PE_OI": "PE OI",
        }
        display = display[wanted].rename(columns=rename)

        display = display.rename(columns={"Strike": "STRIKE"})
        st.dataframe(
            option_chain_styler(
                display,
                safe_float(metrics["atm"], np.nan),
                safe_float(metrics["support"], np.nan),
                safe_float(metrics["resistance"], np.nan),
            ),
            use_container_width=True,
            hide_index=True,
            height=650,
        )
        st.caption(
            "🟢 Support = highest Put OI • 🔴 Resistance = highest Call OI • 🟡 ATM strike. "
            "CE/PE columns are lightly separated by colour; expanded mode also shows Gamma and Vega. "
            "Max Pain is an approximation from available OI."
        )


with backtest_tab:
    st.markdown("### 5m Entry + 15m Confirmation Backtest")
    st.caption(
        "This is an underlying-direction test using the next three 5-minute candles. "
        "It is not an options premium P&L backtest and excludes slippage, spread, brokerage and taxes."
    )
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Signals Tested", str(backtest["trades"]))
    b2.metric("Directional Win Rate", fmt_num(backtest["win_rate"], 1) + "%")
    b3.metric("Average Signed Move", fmt_num(backtest["avg_move"], 3) + "%")
    b4.metric("Profit Factor", fmt_num(backtest["profit_factor"], 2))
    if backtest["trades"] < 30:
        st.warning("Sample is too small for a reliable conclusion. Test at least 30–60 trading days.")
    else:
        st.info("Use this only for validation. Past performance does not guarantee future results.")

with risk_tab:
    st.markdown("### Position Size & Risk")
    r1, r2, r3 = st.columns(3)
    with r1:
        capital = st.number_input("Trading Capital (₹)", min_value=1000.0, value=100000.0, step=5000.0)
    with r2:
        risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    with r3:
        lot_size = st.number_input("Lot Size", min_value=1, value=75, step=1)

    p1, p2, p3 = st.columns(3)
    with p1:
        entry_price = st.number_input("Option Entry Price (₹)", min_value=0.05, value=100.0, step=1.0)
    with p2:
        stop_price = st.number_input("Stop-Loss Price (₹)", min_value=0.0, value=80.0, step=1.0)
    with p3:
        target_rr = st.number_input("Target R multiple", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

    risk_budget = capital * risk_percent / 100
    risk_per_unit = max(entry_price - stop_price, 0)
    risk_per_lot = risk_per_unit * lot_size
    lots = math.floor(risk_budget / risk_per_lot) if risk_per_lot > 0 else 0
    quantity = lots * lot_size
    target = entry_price + risk_per_unit * target_rr

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Maximum Risk", f"₹{risk_budget:,.0f}")
    q2.metric("Suggested Lots", str(lots))
    q3.metric("Quantity", str(quantity))
    q4.metric("Calculated Target", f"₹{target:,.2f}")

    if stop_price >= entry_price:
        st.error("For a long option setup, Stop-Loss must be below Entry Price.")
    elif lots < 1:
        st.warning("Risk budget is too small for one lot at this stop distance.")
    else:
        st.success(
            f"At {risk_percent:.1f}% risk, {lots} lot(s) risk approximately "
            f"₹{risk_per_lot * lots:,.0f} before slippage and charges."
        )

with log_tab:
    logs = pd.DataFrame(
        [
            ["Connection", connection.ok, connection.status_code, connection.elapsed_ms, connection.message],
            ["Expiry List", expiry_result.ok, expiry_result.status_code, expiry_result.elapsed_ms, expiry_result.message],
            ["Option Chain", chain_result.ok, chain_result.status_code, chain_result.elapsed_ms, chain_result.message],
            ["5m Candles", result5.ok, result5.status_code, result5.elapsed_ms, result5.message],
            ["15m Candles", result15.ok, result15.status_code, result15.elapsed_ms, result15.message],
            ["India VIX", vix_result.ok, vix_result.status_code, vix_result.elapsed_ms, vix_result.message],
        ],
        columns=["Request", "Success", "HTTP", "Time ms", "Message"],
    )
    st.dataframe(logs, use_container_width=True, hide_index=True)
    st.caption(
        "Dhan codes: 806 = Data API not subscribed; 807 = token expired; "
        "808/809/810 = authentication, token, or Client ID problem; "
        "811 = invalid expiry; 813 = invalid Security ID."
    )

st.markdown("---")
st.caption(
    "V10.2 Pro Terminal is a decision-support dashboard only. No dashboard can guarantee profit, and this app does not place real-money orders. "
    "Verify the instrument ID, expiry, liquidity, bid–ask spread, charges, and risk before any trade."
)
