import base64
import calendar
import io
import math
import csv
import os
import re
import struct
import time
import wave
import textwrap
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dhanhq import DhanContext, dhanhq


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Shankar Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: clamp(1.7rem, 2.7vw, 2.45rem);
        font-weight: 850;
        line-height: 1.18;
        margin-top: 0.7rem;
        margin-bottom: 0.25rem;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .sub-title {
        color: #6b7280;
        margin-bottom: 0.9rem;
        font-size: clamp(0.82rem, 1vw, 1rem);
        line-height: 1.35;
        white-space: normal;
        overflow-wrap: anywhere;
    }

    .ce-heading {
        background: #ffe5e5;
        color: #a00000;
        padding: 9px;
        border-radius: 8px;
        text-align: center;
        font-weight: 800;
    }

    .pe-heading {
        background: #e6ffeb;
        color: #006b22;
        padding: 9px;
        border-radius: 8px;
        text-align: center;
        font-weight: 800;
    }

    .strike-heading {
        background: #fff3bf;
        color: #664d03;
        padding: 9px;
        border-radius: 8px;
        text-align: center;
        font-weight: 800;
    }

    .signal-bullish {
        background: #dcfce7;
        border: 2px solid #22c55e;
        color: #166534;
        padding: 18px;
        border-radius: 14px;
        font-weight: 900;
        text-align: center;
        font-size: 28px;
    }

    .signal-bearish {
        background: #fee2e2;
        border: 2px solid #ef4444;
        color: #991b1b;
        padding: 18px;
        border-radius: 14px;
        font-weight: 900;
        text-align: center;
        font-size: 28px;
    }

    .signal-neutral {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        color: #92400e;
        padding: 18px;
        border-radius: 14px;
        font-weight: 900;
        text-align: center;
        font-size: 28px;
    }

    .status-open {
        background: #dcfce7;
        border-left: 6px solid #16a34a;
        padding: 10px;
        border-radius: 8px;
        font-weight: 750;
    }

    .status-closed {
        background: #fef3c7;
        border-left: 6px solid #d97706;
        padding: 10px;
        border-radius: 8px;
        font-weight: 750;
    }

    .alert-breakout {
        background: #dcfce7;
        border-left: 6px solid #16a34a;
        padding: 12px;
        border-radius: 8px;
        font-weight: 750;
    }

    .alert-breakdown {
        background: #fee2e2;
        border-left: 6px solid #dc2626;
        padding: 12px;
        border-radius: 8px;
        font-weight: 750;
    }

    .alert-range {
        background: #fef3c7;
        border-left: 6px solid #d97706;
        padding: 12px;
        border-radius: 8px;
        font-weight: 750;
    }

    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    div[data-testid="stMetricValue"] {
        font-size: clamp(1.05rem, 1.7vw, 1.65rem) !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.2 !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        white-space: normal !important;
    }

    div[data-testid="stMetric"] {
        min-height: 118px;
    }

    @media (max-width: 1100px) {
        div[data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
        }
    }


    .terminal-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
        gap: 0.55rem;
        margin: 0.4rem 0 0.6rem 0;
        width: 100%;
    }

    .terminal-pill {
        background: #0f172a;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 999px;
        padding: 0.58rem 0.7rem;
        font-size: clamp(0.72rem, 0.9vw, 0.86rem);
        font-weight: 700;
        text-align: center;
        white-space: normal;
        overflow-wrap: anywhere;
        box-sizing: border-box;
    }

    .mtf-bullish {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border: 1px solid #22c55e;
        color: #14532d;
        padding: 14px;
        border-radius: 12px;
        font-weight: 850;
        text-align: center;
    }

    .mtf-bearish {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 1px solid #ef4444;
        color: #7f1d1d;
        padding: 14px;
        border-radius: 12px;
        font-weight: 850;
        text-align: center;
    }

    .mtf-neutral {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 1px solid #f59e0b;
        color: #78350f;
        padding: 14px;
        border-radius: 12px;
        font-weight: 850;
        text-align: center;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #e2e8f0;
    }

    


    .grade-strong-buy {
        background: linear-gradient(135deg, #dcfce7, #86efac);
        border: 2px solid #16a34a;
        color: #14532d;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 900;
        font-size: clamp(1.25rem, 2vw, 1.9rem);
    }

    .grade-moderate-buy {
        background: linear-gradient(135deg, #ecfccb, #bef264);
        border: 2px solid #65a30d;
        color: #365314;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 900;
        font-size: clamp(1.2rem, 1.8vw, 1.7rem);
    }

    .grade-wait {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 2px solid #d97706;
        color: #78350f;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 900;
        font-size: clamp(1.2rem, 1.8vw, 1.7rem);
    }

    .grade-avoid {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 2px solid #dc2626;
        color: #7f1d1d;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        font-weight: 900;
        font-size: clamp(1.2rem, 1.8vw, 1.7rem);
    }

    .professional-note {
        background: #0f172a;
        color: #f8fafc;
        border-radius: 12px;
        padding: 12px 14px;
        margin-top: 10px;
        font-size: 0.9rem;
    }


    html, body, [data-testid="stAppViewContainer"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: clip !important;
    }

    [data-testid="stAppViewBlockContainer"],
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding-top: 0.7rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        padding-bottom: 2rem !important;
        box-sizing: border-box !important;
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.7rem !important;
        align-items: stretch !important;
    }

    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 210px !important;
        width: auto !important;
    }

    div[data-testid="stMetric"] {
        width: 100% !important;
        min-width: 0 !important;
        min-height: 112px !important;
        padding: 0.78rem !important;
        box-sizing: border-box !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: clamp(1rem, 1.35vw, 1.55rem) !important;
        line-height: 1.18 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: clamp(0.72rem, 0.85vw, 0.9rem) !important;
        line-height: 1.2 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }

    .main-title {
        font-size: clamp(1.7rem, 2.7vw, 2.45rem) !important;
        line-height: 1.18 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        margin-top: 0.65rem !important;
        margin-bottom: 0.25rem !important;
        padding-top: 0.2rem !important;
    }

    .sub-title {
        font-size: clamp(0.8rem, 1vw, 1rem) !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        margin-bottom: 0.8rem !important;
    }

    .terminal-strip {
        width: 100% !important;
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;
        gap: 0.55rem !important;
    }

    .terminal-pill {
        width: 100% !important;
        box-sizing: border-box !important;
        text-align: center !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        font-size: clamp(0.72rem, 0.9vw, 0.86rem) !important;
        padding: 0.58rem 0.7rem !important;
    }

    .signal-bullish,
    .signal-bearish,
    .signal-neutral,
    .grade-strong-buy,
    .grade-moderate-buy,
    .grade-wait,
    .grade-avoid,
    .mtf-bullish,
    .mtf-bearish,
    .mtf-neutral {
        width: 100% !important;
        box-sizing: border-box !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }

    [data-testid="stDataFrame"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    iframe {
        width: 100% !important;
        max-width: 100% !important;
    }

    @media (max-width: 1366px) {
        [data-testid="column"] {
            flex: 1 1 190px !important;
        }

        [data-testid="stAppViewBlockContainer"],
        .block-container {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.05rem !important;
        }
    }

    @media (max-width: 900px) {
        [data-testid="column"] {
            flex: 1 1 170px !important;
        }

        .terminal-strip {
            grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)) !important;
        }
    }

    @media (max-width: 640px) {
        [data-testid="column"] {
            flex: 1 1 100% !important;
        }

        .terminal-strip {
            grid-template-columns: 1fr !important;
        }

        .main-title {
            font-size: 1.65rem !important;
        }
    }


    div[data-testid="stMetric"] {
        min-height: 62px !important;
        padding: 0.4rem 0.52rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    div[data-testid="stMetricValue"] {
        margin-top: 0.15rem !important;
        margin-bottom: 0 !important;
        line-height: 1.12 !important;
    }

    div[data-testid="stMetricLabel"] {
        margin-bottom: 0 !important;
        line-height: 1.1 !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.45rem !important;
        margin-bottom: 0.25rem !important;
    }

    h1, h2, h3 {
        margin-top: 0.45rem !important;
        margin-bottom: 0.45rem !important;
    }

    .grade-strong-buy,
    .grade-moderate-buy,
    .grade-wait,
    .grade-avoid,
    .signal-bullish,
    .signal-bearish,
    .signal-neutral {
        padding: 12px !important;
        margin: 0.45rem 0 !important;
    }

    .professional-note {
        padding: 8px 10px !important;
        margin-top: 0.35rem !important;
        margin-bottom: 0.35rem !important;
    }

    .stAlert {
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
    }


    .live-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.45rem;
        margin-top: 0.35rem;
        margin-bottom: 0.55rem;
    }

    .live-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 9px;
        padding: 0.5rem 0.65rem;
        min-height: 50px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .live-card-title {
        font-size: 0.7rem;
        font-weight: 700;
        color: #64748b;
        line-height: 1.05;
        margin-bottom: 0.12rem;
    }

    .live-card-value {
        font-size: 1rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.08;
    }

    @media (max-width: 900px) {
        .live-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 560px) {
        .live-grid {
            grid-template-columns: 1fr;
        }
    }


    :root {
        --navy: #0f172a;
        --blue: #1d4ed8;
        --cyan: #0891b2;
        --green: #15803d;
        --amber: #d97706;
        --red: #b91c1c;
        --slate: #475569;
        --panel: #f8fafc;
        --border: #dbe3ee;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top right, rgba(29, 78, 216, 0.06), transparent 28%),
            linear-gradient(180deg, #f8fafc 0%, #eef4fb 100%);
    }

    .terminal-header {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        margin: 0.15rem 0 0.55rem 0;
        border-radius: 14px;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #0369a1 100%);
        color: white;
        box-sizing: border-box;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.16);
        overflow: visible;
    }

    .terminal-header-left {
        min-width: 0;
        flex: 1 1 auto;
    }

    .terminal-header-title {
        font-size: clamp(1.45rem, 2.5vw, 2.35rem);
        font-weight: 900;
        line-height: 1.15;
        margin: 0;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .terminal-header-subtitle {
        font-size: clamp(0.75rem, 0.95vw, 0.95rem);
        opacity: 0.88;
        margin-top: 0.22rem;
        line-height: 1.25;
        white-space: normal;
    }

    .vix-badge {
        flex: 0 0 auto;
        min-width: 145px;
        padding: 0.65rem 0.85rem;
        border-radius: 12px;
        text-align: center;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(8px);
    }

    .vix-label {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        opacity: 0.82;
    }

    .vix-value {
        font-size: clamp(1.2rem, 1.8vw, 1.65rem);
        font-weight: 900;
        line-height: 1.1;
        margin-top: 0.12rem;
    }

    .vix-state {
        font-size: 0.72rem;
        margin-top: 0.12rem;
        opacity: 0.9;
    }

    .status-open {
        background: linear-gradient(90deg, #dcfce7, #ecfdf5) !important;
        border-left: 5px solid #16a34a !important;
        color: #14532d !important;
    }

    .status-closed {
        background: linear-gradient(90deg, #fff7ed, #fffbeb) !important;
        border-left: 5px solid #d97706 !important;
        color: #78350f !important;
    }

    .terminal-pill {
        background: linear-gradient(135deg, #172554, #1e3a8a) !important;
        border: 1px solid #3b82f6 !important;
        color: #eff6ff !important;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.15);
    }

    .live-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1px solid var(--border) !important;
        border-left: 4px solid var(--blue) !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05) !important;
    }

    h1, h2, h3 {
        color: var(--navy) !important;
    }

    .professional-note {
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        color: #f8fafc !important;
        border-left: 4px solid #38bdf8 !important;
    }

    @media (max-width: 700px) {
        .terminal-header {
            align-items: flex-start;
            flex-direction: column;
        }

        .vix-badge {
            width: 100%;
            min-width: 0;
            box-sizing: border-box;
        }
    }


    .terminal-header {
        position: relative;
        z-index: 2;
    }

    .terminal-header-title {
        max-width: 100%;
    }

    .stButton > button {
        border-radius: 10px !important;
        border: 1px solid #2563eb !important;
        background: linear-gradient(135deg, #1d4ed8, #0369a1) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.18) !important;
    }

    .stButton > button:hover {
        border-color: #0ea5e9 !important;
        transform: translateY(-1px);
    }

    [data-testid="stAlert"] {
        border-radius: 10px !important;
    }


    .live-card:nth-child(1) { border-left-color: #2563eb !important; }
    .live-card:nth-child(2) { border-left-color: #7c3aed !important; }
    .live-card:nth-child(3) { border-left-color: #0891b2 !important; }
    .live-card:nth-child(4) { border-left-color: #059669 !important; }
    .live-card:nth-child(5) { border-left-color: #d97706 !important; }
    .live-card:nth-child(6) { border-left-color: #dc2626 !important; }

    div[data-testid="stMetric"]:has(
        div[data-testid="stMetricValue"]
    ) {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.10) !important;
    }

    .ce-heading {
        background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
        border: 1px solid #ef4444 !important;
    }

    .pe-heading {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0) !important;
        border: 1px solid #22c55e !important;
    }

    .strike-heading {
        background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
        border: 1px solid #f59e0b !important;
    }

    .smc-card {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 12px;
        min-height: 100px;
    }

    .smc-title {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 700;
    }

    .smc-value {
        font-size: 1.25rem;
        font-weight: 850;
        margin-top: 6px;
    }

    /* V19 responsive header and coloured cross-market cards */
    .terminal-header {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) minmax(155px, 190px) !important;
        align-items: center !important;
        overflow: visible !important;
    }

    .vix-badge {
        width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 5 !important;
    }

    .market-section-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin: 0.55rem 0 0.25rem;
    }

    .market-section-note {
        color: #64748b;
        font-size: 0.78rem;
        text-align: right;
    }

    .live-card.index-card {
        background: linear-gradient(135deg, #eff6ff, #dbeafe) !important;
        border-left-color: #2563eb !important;
    }

    .live-card.gold-card {
        background: linear-gradient(135deg, #fffbeb, #fde68a) !important;
        border-left-color: #d97706 !important;
    }

    .live-card.crude-card {
        background: linear-gradient(135deg, #f8fafc, #cbd5e1) !important;
        border-left-color: #334155 !important;
    }

    .live-card.bitcoin-card {
        background: linear-gradient(135deg, #fff7ed, #fed7aa) !important;
        border-left-color: #f97316 !important;
    }

    .live-card.unavailable-card {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0) !important;
        border-left-color: #94a3b8 !important;
    }

    .live-card-source {
        margin-top: 0.18rem;
        font-size: 0.65rem;
        line-height: 1.1;
        color: #64748b;
        font-weight: 650;
    }

    @media (max-width: 700px) {
        .terminal-header {
            grid-template-columns: 1fr !important;
        }
        .market-section-title {
            align-items: flex-start;
            flex-direction: column;
        }
        .market-section-note {
            text-align: left;
        }
    }


    /* V19.1 colorful cards */
    .color-card-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.65rem;margin:.45rem 0 .8rem;width:100%;}
    .color-card {border-radius:13px;padding:.78rem .9rem;min-height:76px;box-sizing:border-box;border:1px solid rgba(255,255,255,.35);box-shadow:0 5px 14px rgba(15,23,42,.10);display:flex;flex-direction:column;justify-content:center;}
    .color-card-label {font-size:.76rem;font-weight:800;opacity:.88;margin-bottom:.2rem;}
    .color-card-value {font-size:clamp(1rem,1.4vw,1.35rem);font-weight:900;line-height:1.15;overflow-wrap:anywhere;}
    .card-green {background:linear-gradient(135deg,#166534,#22c55e);color:#fff;}
    .card-red {background:linear-gradient(135deg,#991b1b,#ef4444);color:#fff;}
    .card-yellow {background:linear-gradient(135deg,#f59e0b,#fde047);color:#422006;}
    .card-blue {background:linear-gradient(135deg,#1d4ed8,#38bdf8);color:#fff;}
    .card-purple {background:linear-gradient(135deg,#6d28d9,#a78bfa);color:#fff;}
    .card-orange {background:linear-gradient(135deg,#c2410c,#fb923c);color:#fff;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+1) div[data-testid="stMetric"] {background:linear-gradient(135deg,#dbeafe,#bfdbfe)!important;border-left:5px solid #2563eb!important;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+2) div[data-testid="stMetric"] {background:linear-gradient(135deg,#ede9fe,#ddd6fe)!important;border-left:5px solid #7c3aed!important;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+3) div[data-testid="stMetric"] {background:linear-gradient(135deg,#cffafe,#a5f3fc)!important;border-left:5px solid #0891b2!important;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+4) div[data-testid="stMetric"] {background:linear-gradient(135deg,#dcfce7,#bbf7d0)!important;border-left:5px solid #16a34a!important;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+5) div[data-testid="stMetric"] {background:linear-gradient(135deg,#fef3c7,#fde68a)!important;border-left:5px solid #d97706!important;}
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(6n+6) div[data-testid="stMetric"] {background:linear-gradient(135deg,#fee2e2,#fecaca)!important;border-left:5px solid #dc2626!important;}

    /* =====================================================
       V20 FULL-COLOR TERMINAL + INDIA VIX VISIBILITY FIX
       ===================================================== */
    .terminal-header {
        grid-template-columns: minmax(0, 1fr) 138px !important;
        width: 100% !important;
        max-width: 100% !important;
        padding: .68rem .72rem !important;
        gap: .65rem !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }
    .terminal-header-left {min-width:0 !important;}
    .terminal-header-title {font-size:clamp(1.35rem,2.25vw,2.15rem)!important;}
    .vix-badge {
        width:138px !important;
        max-width:138px !important;
        min-width:138px !important;
        padding:.55rem .42rem !important;
        overflow:visible !important;
        box-sizing:border-box !important;
    }
    .vix-label,.vix-value,.vix-state {white-space:normal!important;overflow:visible!important;}

    /* Make all Streamlit metric cards colorful from top to bottom */
    div[data-testid="stMetric"] {
        color:#0f172a !important;
        border-width:1px 1px 1px 5px !important;
        box-shadow:0 5px 14px rgba(15,23,42,.10)!important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"], div[data-testid="stMetricDelta"] {
        color:inherit!important;
    }

    /* Color regular alert/status boxes too */
    [data-testid="stAlert"] {
        background:linear-gradient(135deg,#e0f2fe,#bae6fd)!important;
        border:1px solid #38bdf8!important;
        color:#0c4a6e!important;
        box-shadow:0 4px 12px rgba(14,116,144,.10)!important;
    }
    [data-testid="stExpander"] {
        background:linear-gradient(135deg,#f5f3ff,#ede9fe)!important;
        border:1px solid #a78bfa!important;
        border-radius:12px!important;
        overflow:hidden!important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background:linear-gradient(180deg,#ffffff,#eff6ff)!important;
        border:1px solid #93c5fd!important;
        border-radius:12px!important;
        padding:.2rem!important;
    }

    /* Color custom information cards that were previously white */
    .smc-card:nth-child(6n+1), .color-card:nth-child(6n+1) {background:linear-gradient(135deg,#dbeafe,#bfdbfe)!important;border-left:5px solid #2563eb!important;color:#172554!important;}
    .smc-card:nth-child(6n+2), .color-card:nth-child(6n+2) {background:linear-gradient(135deg,#ede9fe,#ddd6fe)!important;border-left:5px solid #7c3aed!important;color:#3b0764!important;}
    .smc-card:nth-child(6n+3), .color-card:nth-child(6n+3) {background:linear-gradient(135deg,#cffafe,#a5f3fc)!important;border-left:5px solid #0891b2!important;color:#164e63!important;}
    .smc-card:nth-child(6n+4), .color-card:nth-child(6n+4) {background:linear-gradient(135deg,#dcfce7,#bbf7d0)!important;border-left:5px solid #16a34a!important;color:#14532d!important;}
    .smc-card:nth-child(6n+5), .color-card:nth-child(6n+5) {background:linear-gradient(135deg,#fef3c7,#fde68a)!important;border-left:5px solid #d97706!important;color:#78350f!important;}
    .smc-card:nth-child(6n+6), .color-card:nth-child(6n+6) {background:linear-gradient(135deg,#fee2e2,#fecaca)!important;border-left:5px solid #dc2626!important;color:#7f1d1d!important;}
    .smc-title,.smc-value {color:inherit!important;}

    /* Inputs, paper trading and backtest controls */
    [data-testid="stNumberInput"], [data-testid="stSelectbox"], [data-testid="stTextInput"] {
        background:linear-gradient(135deg,#f8fafc,#e0f2fe)!important;
        border-radius:10px!important;
        padding:.25rem!important;
    }

    /* V20.1: ensure the complete INDIA VIX badge is always visible */
    .terminal-header {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) minmax(170px, 190px) !important;
        align-items: stretch !important;
        overflow: visible !important;
        min-height: 92px !important;
    }
    .vix-badge {
        width: 100% !important;
        max-width: none !important;
        min-width: 170px !important;
        min-height: 76px !important;
        padding: .65rem .7rem !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: visible !important;
        position: relative !important;
        z-index: 5 !important;
    }
    .vix-label {
        display: block !important;
        font-size: .72rem !important;
        line-height: 1.2 !important;
        margin: 0 0 .12rem 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    .vix-value {
        display: block !important;
        line-height: 1.15 !important;
        margin: 0 !important;
        overflow: visible !important;
    }
    .vix-state {
        display: block !important;
        line-height: 1.2 !important;
        margin-top: .18rem !important;
        white-space: normal !important;
        overflow: visible !important;
    }

    @media (max-width: 820px) {
        .terminal-header {
            grid-template-columns: 1fr !important;
            overflow: visible !important;
        }
        .vix-badge {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }
    }

    /* V21: prevent Streamlit toolbar from covering the terminal title */
    [data-testid="stAppViewBlockContainer"], .block-container {
        padding-top: 2.35rem !important;
    }
    .terminal-header {
        margin-top: .65rem !important;
        min-height: 108px !important;
        padding-top: 1rem !important;
        padding-bottom: .85rem !important;
    }
    .terminal-header-title {
        padding-top: .18rem !important;
        line-height: 1.25 !important;
        overflow: visible !important;
    }
    .terminal-header-subtitle {
        line-height: 1.35 !important;
        overflow: visible !important;
    }
    .vix-badge {
        min-height: 88px !important;
        align-self: center !important;
    }
    /* V22 market calendar and automatic pivot dashboard */
    .market-calendar-wrap {background:linear-gradient(145deg,#111827,#172554);border:1px solid #334155;border-radius:16px;padding:14px;box-shadow:0 10px 26px rgba(2,6,23,.25);margin:.55rem 0 .8rem;color:#f8fafc;}
    .market-calendar-title {font-size:1.05rem;font-weight:900;margin-bottom:.5rem;display:flex;justify-content:space-between;gap:.5rem;flex-wrap:wrap;}
    .market-calendar-grid {display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;}
    .cal-head {text-align:center;font-size:.72rem;font-weight:850;color:#93c5fd;padding:5px 2px;}
    .cal-day {min-height:58px;border-radius:9px;padding:6px;background:linear-gradient(145deg,#1e293b,#0f172a);border:1px solid #334155;font-size:.75rem;box-sizing:border-box;}
    .cal-empty {background:transparent;border-color:transparent;}
    .cal-weekend {background:linear-gradient(145deg,#3f1d2e,#1f1724);border-color:#7f1d1d;color:#fecaca;}
    .cal-holiday {background:linear-gradient(145deg,#78350f,#451a03);border-color:#f59e0b;color:#fef3c7;}
    .cal-today {outline:2px solid #38bdf8;box-shadow:0 0 0 2px rgba(56,189,248,.15);}
    .cal-number {font-size:.82rem;font-weight:900;}
    .cal-note {font-size:.58rem;line-height:1.15;margin-top:4px;overflow-wrap:anywhere;}
    .pivot-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.55rem;margin:.5rem 0 .8rem;}
    .pivot-card {border-radius:12px;padding:.7rem .75rem;border:1px solid #334155;box-shadow:0 5px 15px rgba(2,6,23,.18);background:linear-gradient(145deg,#1e293b,#0f172a);color:#f8fafc;}
    .pivot-label {font-size:.7rem;font-weight:800;color:#94a3b8;}
    .pivot-value {font-size:1.1rem;font-weight:900;margin-top:.12rem;}
    .pivot-resistance {border-left:5px solid #ef4444;background:linear-gradient(145deg,#3f1d2e,#1f1724);}
    .pivot-support {border-left:5px solid #22c55e;background:linear-gradient(145deg,#123524,#10251c);}
    .pivot-main {border-left:5px solid #38bdf8;background:linear-gradient(145deg,#172554,#0c4a6e);}
    .pivot-cpr {border-left:5px solid #a78bfa;background:linear-gradient(145deg,#2e1065,#1e1b4b);}
    @media (max-width:640px){.cal-day{min-height:46px;padding:4px}.cal-note{display:none}.market-calendar-grid{gap:3px}}

    /* One final decision banner */
    .final-one-buy-ce {background:linear-gradient(135deg,#14532d,#22c55e);color:white;border:2px solid #16a34a;}
    .final-one-buy-pe {background:linear-gradient(135deg,#7f1d1d,#ef4444);color:white;border:2px solid #dc2626;}
    .final-one-wait {background:linear-gradient(135deg,#92400e,#fbbf24);color:#3b2200;border:2px solid #d97706;}
    .final-one-banner {padding:16px;border-radius:14px;text-align:center;font-size:clamp(1.15rem,1.8vw,1.7rem);font-weight:900;margin:.55rem 0;box-shadow:0 7px 20px rgba(15,23,42,.16);}

    /* V31 full-width multi-timeframe panels */
    .mtf-full-panel {width:100%;box-sizing:border-box;border-radius:14px;padding:14px 16px;margin:.55rem 0;box-shadow:0 7px 18px rgba(15,23,42,.14);border:1px solid rgba(148,163,184,.35);color:#f8fafc;}
    .mtf-5m {background:linear-gradient(135deg,#0f172a,#1d4ed8);}
    .mtf-15m {background:linear-gradient(135deg,#312e81,#7c3aed);}
    .mtf-60m {background:linear-gradient(135deg,#064e3b,#059669);}
    .mtf-full-title {font-size:1.05rem;font-weight:900;margin-bottom:.55rem;letter-spacing:.02em;}
    .mtf-full-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.55rem;}
    .mtf-full-item {background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:.58rem .65rem;min-width:0;}
    .mtf-full-label {font-size:.72rem;font-weight:750;opacity:.82;margin-bottom:.16rem;}
    .mtf-full-value {font-size:clamp(.92rem,1.2vw,1.15rem);font-weight:900;overflow-wrap:anywhere;}
    @media(max-width:760px){.mtf-full-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
    @media(max-width:460px){.mtf-full-grid{grid-template-columns:1fr;}}

    /* V25 guaranteed option-chain colours using native HTML table */
    .option-html-wrap {width:100%;overflow:auto;max-height:650px;border:1px solid #475569;border-radius:12px;background:#0b1220;}
    table.option-html {width:100%;border-collapse:separate;border-spacing:0;min-width:1250px;font-size:.78rem;color:#e5e7eb;}
    table.option-html th {position:sticky;top:0;z-index:3;background:#111827;color:#f8fafc;padding:8px 7px;border-bottom:2px solid #475569;text-align:right;white-space:nowrap;}
    table.option-html td {padding:7px;border-bottom:1px solid #263244;text-align:right;white-space:nowrap;background:#111827;}
    table.option-html tr.level-atm td {background:#facc15!important;color:#1c1917!important;font-weight:900!important;border-top:2px solid #a16207;border-bottom:2px solid #a16207;}
    table.option-html tr.level-resistance td {background:#dc2626!important;color:#fff!important;font-weight:900!important;border-top:2px solid #7f1d1d;border-bottom:2px solid #7f1d1d;}
    table.option-html tr.level-support td {background:#16a34a!important;color:#fff!important;font-weight:900!important;border-top:2px solid #14532d;border-bottom:2px solid #14532d;}
    table.option-html tr.level-atm-resistance td {background:linear-gradient(90deg,#dc2626 0 50%,#facc15 50% 100%)!important;color:#111827!important;font-weight:950!important;}
    table.option-html tr.level-atm-support td {background:linear-gradient(90deg,#facc15 0 50%,#16a34a 50% 100%)!important;color:#111827!important;font-weight:950!important;}
    table.option-html tr.level-support-resistance td {background:linear-gradient(90deg,#dc2626 0 50%,#16a34a 50% 100%)!important;color:#fff!important;font-weight:950!important;}
    table.option-html tr.level-all td {background:linear-gradient(90deg,#dc2626 0 33%,#facc15 33% 66%,#16a34a 66% 100%)!important;color:#111827!important;font-weight:950!important;}
    table.option-html td.strike-cell {font-size:.86rem;font-weight:950;text-align:center;border-left:2px solid #64748b;border-right:2px solid #64748b;}
    table.option-html tr:hover td {filter:brightness(1.13);}

    /* V27 Indian option-chain: CE resistance, PE support and ATM remain independently visible */
    table.indian-chain-v27 td {background:#111827!important;color:#e5e7eb!important;}
    table.indian-chain-v27 td.v27-ce-resistance {background:linear-gradient(135deg,#7f1d1d,#dc2626)!important;color:#fff!important;font-weight:950!important;border-top:2px solid #f87171!important;border-bottom:2px solid #f87171!important;}
    table.indian-chain-v27 td.v27-pe-support {background:linear-gradient(135deg,#14532d,#16a34a)!important;color:#fff!important;font-weight:950!important;border-top:2px solid #4ade80!important;border-bottom:2px solid #4ade80!important;}
    .key-level-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.65rem;margin:.45rem 0 .75rem;position:sticky;top:0;z-index:20;}
    .key-level-card{border-radius:12px;padding:.72rem .85rem;display:flex;flex-direction:column;box-shadow:0 6px 16px rgba(0,0,0,.24);border:2px solid rgba(255,255,255,.32);font-weight:900;}
    .key-level-card span{font-size:1.25rem;line-height:1.15;margin:.15rem 0;}
    .key-level-card small{font-size:.72rem;font-weight:750;opacity:.92;}
    .key-support{background:linear-gradient(135deg,#14532d,#22c55e);color:#fff;}
    .key-atm{background:linear-gradient(135deg,#a16207,#facc15);color:#1c1917;}
    .key-resistance{background:linear-gradient(135deg,#7f1d1d,#ef4444);color:#fff;}
    table.indian-chain-v27 tbody tr.v27-sup-row td{background:rgba(22,163,74,.58)!important;color:#fff!important;font-weight:900!important;}
    table.indian-chain-v27 tbody tr.v27-res-row td{background:rgba(220,38,38,.58)!important;color:#fff!important;font-weight:900!important;}
    table.indian-chain-v27 tbody tr.v27-atm-row td{box-shadow:inset 0 2px #fde047,inset 0 -2px #fde047!important;}
    @media(max-width:760px){.key-level-grid{grid-template-columns:1fr;position:relative;}}
    table.indian-chain-v27 td.v27-support-outline {border-top:2px solid #22c55e!important;border-bottom:2px solid #22c55e!important;}
    table.indian-chain-v27 td.v27-resistance-outline {border-top:2px solid #ef4444!important;border-bottom:2px solid #ef4444!important;}
    table.indian-chain-v27 td.v27-atm-cell {background:#facc15!important;color:#111827!important;border:3px solid #fde047!important;}
    table.indian-chain-v27 td.v27-res-strike {box-shadow:inset 5px 0 0 #ef4444!important;}
    table.indian-chain-v27 td.v27-sup-strike {box-shadow:inset -5px 0 0 #22c55e!important;}
    .strike-box {display:flex;align-items:center;justify-content:center;gap:5px;min-width:82px;}
    .level-tag {display:inline-block;padding:2px 5px;margin-left:2px;border-radius:5px;font-size:.61rem;font-weight:950;line-height:1.1;}
    .tag-atm {background:#facc15;color:#111827;border:1px solid #a16207;}
    .tag-res {background:#dc2626;color:#fff;border:1px solid #fecaca;}
    .tag-sup {background:#16a34a;color:#fff;border:1px solid #bbf7d0;}


    /* =====================================================
       V31.1 RESPONSIVE: MOBILE + TABLET + DESKTOP
       ===================================================== */
    * { box-sizing: border-box; }

    /* Keep the app fluid on every screen size. */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Desktop: spacious terminal layout. */
    @media (min-width: 1200px) {
        [data-testid="stAppViewBlockContainer"], .block-container {
            padding-left: 1.15rem !important;
            padding-right: 1.15rem !important;
        }
        [data-testid="column"] { flex-basis: 190px !important; }
    }

    /* Tablet: two-column cards where possible. */
    @media (min-width: 641px) and (max-width: 1199px) {
        [data-testid="stAppViewBlockContainer"], .block-container {
            padding-left: .7rem !important;
            padding-right: .7rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            gap: .55rem !important;
        }
        [data-testid="column"] {
            flex: 1 1 calc(50% - .55rem) !important;
            min-width: 220px !important;
        }
        .color-card-grid,
        .pivot-grid { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
    }

    /* Mobile: one clean full-width column with touch-friendly controls. */
    @media (max-width: 640px) {
        [data-testid="stAppViewBlockContainer"], .block-container {
            padding-top: 1.1rem !important;
            padding-left: .48rem !important;
            padding-right: .48rem !important;
            padding-bottom: 1.2rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            gap: .42rem !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            flex: 1 1 100% !important;
        }
        .terminal-header {
            grid-template-columns: 1fr !important;
            min-height: auto !important;
            padding: .82rem !important;
            margin-top: .25rem !important;
            border-radius: 12px !important;
        }
        .terminal-header-title { font-size: 1.38rem !important; }
        .terminal-header-subtitle { font-size: .76rem !important; }
        .vix-badge {
            width: 100% !important;
            min-width: 0 !important;
            min-height: 70px !important;
        }
        .terminal-strip,
        .live-grid,
        .color-card-grid,
        .pivot-grid,
        .key-level-grid { grid-template-columns: 1fr !important; }
        .mtf-full-panel { padding: 11px !important; }
        .mtf-full-grid { grid-template-columns: repeat(2,minmax(0,1fr)) !important; }
        .market-calendar-wrap { padding: 9px !important; }
        .market-calendar-grid { gap: 2px !important; }
        .cal-day { min-height: 42px !important; padding: 3px !important; }
        .cal-number { font-size: .72rem !important; }
        .cal-note { display: none !important; }
        div[data-testid="stMetric"] {
            min-height: 66px !important;
            padding: .52rem .62rem !important;
        }
        div[data-testid="stMetricValue"] { font-size: 1.08rem !important; }
        .stButton > button,
        [data-testid="stDownloadButton"] button {
            width: 100% !important;
            min-height: 44px !important;
        }
        [data-testid="stSelectbox"],
        [data-testid="stNumberInput"],
        [data-testid="stTextInput"] { width: 100% !important; }
        .final-one-banner { padding: 12px 9px !important; }
        h1 { font-size: 1.55rem !important; }
        h2 { font-size: 1.28rem !important; }
        h3 { font-size: 1.08rem !important; }
    }

    @media (max-width: 420px) {
        .mtf-full-grid { grid-template-columns: 1fr !important; }
        .terminal-header-title { font-size: 1.24rem !important; }
        .option-html-wrap { max-height: 520px !important; }
    }

    /* Option chain stays readable: swipe horizontally on phone/tablet. */
    .option-html-wrap {
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-x: contain;
        scrollbar-width: thin;
    }
    table.option-html th:first-child,
    table.option-html td:first-child {
        position: sticky;
        left: 0;
        z-index: 2;
    }
    table.option-html th:first-child { z-index: 5; }

    /* Plotly charts and dataframes must never overflow the device. */
    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    .js-plotly-plot, .plot-container, .svg-container {
        width: 100% !important;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CREDENTIALS
# =========================================================
# Recommended:
# 1) Put credentials in environment variables:
#    DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN
# OR
# 2) Create .streamlit/secrets.toml:
#    DHAN_CLIENT_ID = "..."
#    DHAN_ACCESS_TOKEN = "..."
# Fallback placeholders are kept for easy setup.

def get_secret(name, fallback):
    try:
        return st.secrets.get(name, os.getenv(name, fallback))
    except Exception:
        return os.getenv(name, fallback)


CLIENT_ID = str(get_secret("DHAN_CLIENT_ID", "")).strip()
ACCESS_TOKEN = str(get_secret("DHAN_ACCESS_TOKEN", "")).strip()

CREDENTIALS_READY = (
    CLIENT_ID not in {"", "YOUR_CLIENT_ID"}
    and ACCESS_TOKEN not in {"", "YOUR_ACCESS_TOKEN"}
)

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
}

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN) if CREDENTIALS_READY else None


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "load_chain": False,
    "last_signal": "",
    "signal_log": [],
    "last_error": "",
    "paper_balance": 100000.0,
    "paper_positions": [],
    "paper_trades": [],
    "paper_order_message": "",
    "api_logs": [],
    "last_market_quotes": {},
    "commodity_chain_load": False,
    "commodity_choice": "GOLD",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# GENERAL HELPERS
# =========================================================

IST = ZoneInfo("Asia/Kolkata")


def safe_float(value, default=0.0):
    try:
        number = float(value if value is not None else default)
        if not math.isfinite(number):
            return default
        return number
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def render_html(html):
    """Render HTML without Markdown turning indented tags into code blocks."""
    cleaned = textwrap.dedent(str(html)).strip()
    cleaned = "".join(line.strip() for line in cleaned.splitlines())
    cleaned = re.sub(r">\s+<", "><", cleaned)
    st.markdown(cleaned, unsafe_allow_html=True)


def render_colored_option_table(frame, atm, resistance, support, height=820):
    """Render permanently visible key levels plus a strongly coloured option chain."""
    if frame is None or frame.empty:
        st.warning("No option-chain rows available.")
        return

    display = frame.copy()

    def level_row(level):
        if not level:
            return None
        matches = display[(display["Strike"] - float(level)).abs() < 0.001]
        return matches.iloc[0] if not matches.empty else None

    support_row = level_row(support)
    atm_row = level_row(atm)
    resistance_row = level_row(resistance)

    def key_card(label, level, row, css_class, side):
        if row is None:
            return f'<div class="key-level-card {css_class}"><b>{label}</b><span>₹ {level:,.0f}</span></div>'
        oi_col = "PE OI" if side == "PE" else "CE OI"
        ltp_col = "PE LTP" if side == "PE" else "CE LTP"
        return (
            f'<div class="key-level-card {css_class}">'
            f'<b>{label}</b><span>₹ {level:,.0f}</span>'
            f'<small>{side} OI: {safe_float(row.get(oi_col)):,.0f} · LTP: ₹ {safe_float(row.get(ltp_col)):,.2f}</small>'
            f'</div>'
        )

    pinned = (
        '<div class="key-level-grid">'
        + key_card("🟩 SUPPORT S1", support, support_row, "key-support", "PE")
        + key_card("🟨 ATM", atm, atm_row, "key-atm", "CE")
        + key_card("🟥 RESISTANCE R1", resistance, resistance_row, "key-resistance", "CE")
        + '</div>'
    )
    st.markdown(pinned, unsafe_allow_html=True)
    columns = list(display.columns)
    strike_pos = columns.index("Strike") if "Strike" in columns else -1
    numeric_formats = {
        "CE IV": "{:.2f}", "CE Delta": "{:.3f}", "CE Gamma": "{:.5f}",
        "CE Theta": "{:.2f}", "CE Vega": "{:.2f}", "CE LTP": "{:.2f}",
        "Strike": "{:.0f}", "PE LTP": "{:.2f}", "PE Delta": "{:.3f}",
        "PE Gamma": "{:.5f}", "PE Theta": "{:.2f}", "PE Vega": "{:.2f}",
        "PE IV": "{:.2f}",
    }

    def same_level(value, level):
        return math.isclose(safe_float(value), safe_float(level), rel_tol=0, abs_tol=0.001)

    parts = [
        f'<div class="option-html-wrap" style="max-height:{int(height)}px">',
        '<table class="option-html indian-chain-v27"><thead><tr>'
    ]
    parts.extend(f'<th>{col}</th>' for col in columns)
    parts.append('</tr></thead><tbody>')

    for _, row in display.iterrows():
        strike = safe_float(row.get("Strike"))
        is_atm = same_level(strike, atm)
        is_res = same_level(strike, resistance)
        is_sup = same_level(strike, support)
        row_classes = []
        if is_atm: row_classes.append("v27-atm-row")
        if is_res: row_classes.append("v27-res-row")
        if is_sup: row_classes.append("v27-sup-row")
        if is_res and is_atm:
            row_style = "background:linear-gradient(90deg,rgba(220,38,38,.72),rgba(250,204,21,.78))!important;"
        elif is_sup and is_atm:
            row_style = "background:linear-gradient(90deg,rgba(34,197,94,.72),rgba(250,204,21,.78))!important;"
        elif is_res:
            row_style = "background:rgba(220,38,38,.58)!important;box-shadow:inset 0 2px #f87171,inset 0 -2px #f87171;"
        elif is_sup:
            row_style = "background:rgba(22,163,74,.58)!important;box-shadow:inset 0 2px #4ade80,inset 0 -2px #4ade80;"
        elif is_atm:
            row_style = "background:rgba(250,204,21,.72)!important;box-shadow:inset 0 2px #fde047,inset 0 -2px #fde047;"
        else:
            row_style = ""
        parts.append(f'<tr class="{" ".join(row_classes)}" style="{row_style}">')

        for index, col in enumerate(columns):
            value = row[col]
            if pd.isna(value):
                text = ""
            elif col in numeric_formats:
                try:
                    text = numeric_formats[col].format(float(value))
                except Exception:
                    text = str(value)
            elif isinstance(value, (int, float)):
                text = f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"
            else:
                text = str(value)

            classes = []
            if col == "Strike":
                classes.append("strike-cell")
                if is_atm: classes.append("v27-atm-cell")
                if is_res: classes.append("v27-res-strike")
                if is_sup: classes.append("v27-sup-strike")
                labels = []
                if is_atm: labels.append('<span class="level-tag tag-atm">ATM</span>')
                if is_res: labels.append('<span class="level-tag tag-res">R</span>')
                if is_sup: labels.append('<span class="level-tag tag-sup">S</span>')
                text = f'<div class="strike-box"><b>{text}</b><div>{"".join(labels)}</div></div>'
            elif strike_pos >= 0 and index < strike_pos and is_res:
                classes.append("v27-ce-resistance")
            elif strike_pos >= 0 and index > strike_pos and is_sup:
                classes.append("v27-pe-support")

            # A subtle marker on the opposite half keeps the full level traceable.
            if strike_pos >= 0 and index < strike_pos and is_sup:
                classes.append("v27-support-outline")
            if strike_pos >= 0 and index > strike_pos and is_res:
                classes.append("v27-resistance-outline")

            class_attr = f' class="{" ".join(classes)}"' if classes else ""
            parts.append(f'<td{class_attr}>{text}</td>')
        parts.append('</tr>')

    parts.append('</tbody></table></div>')
    st.markdown(''.join(parts), unsafe_allow_html=True)


def request_with_retry(
    method,
    url,
    *,
    headers=None,
    json=None,
    timeout=25,
    attempts=3,
    pause_seconds=2,
):
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            response.raise_for_status()
            return response
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.HTTPError,
        ) as error:
            last_error = error

            if attempt < attempts:
                time.sleep(pause_seconds * attempt)

    raise last_error



def add_api_log(message, level="INFO"):
    timestamp = datetime.now(IST).strftime("%H:%M:%S")
    entry = {
        "Time": timestamp,
        "Level": str(level).upper(),
        "Message": str(message),
    }

    logs = st.session_state.get("api_logs", [])
    logs.append(entry)
    st.session_state.api_logs = logs[-100:]


def parse_marketfeed_payload(payload):
    """
    Accept official direct-REST responses and older SDK-wrapped responses.

    Official v2:
        {"status":"success", "data":{"IDX_I":{"13":{"last_price":...}}}}

    Some older SDK versions wrap data once more:
        {"status":"success", "data":{"data":{"IDX_I":{...}}}}
    """
    if not isinstance(payload, dict):
        return {}, "Response is not a dictionary."

    status = str(payload.get("status", "")).lower()

    if status and status != "success":
        return {}, format_api_error(payload)

    data = payload.get("data", {})

    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        data = data["data"]

    if not isinstance(data, dict):
        return {}, "Market-feed data section is missing."

    parsed = {}

    for segment, instruments in data.items():
        if not isinstance(instruments, dict):
            continue

        for security_id, values in instruments.items():
            if not isinstance(values, dict):
                continue

            last_price = safe_float(
                values.get(
                    "last_price",
                    values.get("lastPrice", values.get("ltp")),
                )
            )

            if last_price <= 0:
                continue

            parsed[(str(segment), str(security_id))] = {
                "last_price": last_price,
                "raw": values,
            }

    if not parsed:
        return {}, "No valid prices were found in the market-feed response."

    return parsed, ""


def direct_marketfeed_ltp(payload, attempts=3):
    url = "https://api.dhan.co/v2/marketfeed/ltp"

    last_message = ""

    for attempt in range(1, attempts + 1):
        try:
            response = requests.post(
                url,
                headers=HEADERS,
                json=payload,
                timeout=15,
            )

            try:
                body = response.json()
            except ValueError:
                body = {
                    "status": "failure",
                    "remarks": f"Non-JSON HTTP {response.status_code}",
                }

            if response.ok:
                parsed, parse_error = parse_marketfeed_payload(body)

                if parsed:
                    add_api_log(
                        f"Market LTP success on attempt {attempt}: {payload}"
                    )
                    return parsed, ""

                last_message = parse_error or format_api_error(body)
            else:
                last_message = (
                    f"HTTP {response.status_code}: {format_api_error(body)}"
                )

        except (requests.Timeout, requests.ConnectionError) as error:
            last_message = str(error)

        except Exception as error:
            last_message = str(error)

        add_api_log(
            f"Market LTP attempt {attempt} failed: {last_message}",
            "WARNING",
        )

        if attempt < attempts:
            time.sleep(attempt)

    return {}, last_message or "Market-feed request failed."


def fetch_professional_index_quotes():
    """
    Fetch each index independently.

    An unavailable BSE/NSE index can no longer break every other live card.
    Only genuine live values are returned—no dummy fallback prices.
    """
    instruments = [
        {"name": "NIFTY 50", "segment": "IDX_I", "security_id": 13},
        {"name": "BANK NIFTY", "segment": "IDX_I", "security_id": 25},
        {"name": "FIN NIFTY", "segment": "IDX_I", "security_id": 27},
        {"name": "MIDCAP NIFTY", "segment": "IDX_I", "security_id": 442},
        {"name": "SENSEX", "segment": "IDX_I", "security_id": 51},
        {"name": "BANKEX", "segment": "IDX_I", "security_id": 69},
    ]

    quotes = {}
    failures = []

    for instrument in instruments:
        key = (
            instrument["segment"],
            str(instrument["security_id"]),
        )

        parsed, error = direct_marketfeed_ltp(
            {
                instrument["segment"]: [
                    instrument["security_id"]
                ]
            },
            attempts=3,
        )

        row = parsed.get(key)

        if row:
            quotes[instrument["name"]] = {
                "last_price": row["last_price"],
                "segment": instrument["segment"],
                "security_id": instrument["security_id"],
            }
        else:
            failures.append(
                f'{instrument["name"]}: {error or "unavailable"}'
            )

        # Market quote limit is 1 request per second.
        time.sleep(1.05)

    return quotes, failures


@st.cache_data(ttl=21600, show_spinner=False)
def fetch_nse_trading_holidays(year):
    """
    Best-effort NSE trading holiday discovery.

    If NSE blocks the request, the dashboard safely falls back to
    weekday/time logic rather than displaying a false holiday.
    """
    url = "https://www.nseindia.com/api/holiday-master?type=trading"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/126 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.nseindia.com/resources/exchange-communication-holidays",
    }

    holidays = set()

    try:
        session = requests.Session()
        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=8,
        )
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()

        containers = []

        if isinstance(payload, dict):
            containers.extend(payload.values())
        elif isinstance(payload, list):
            containers.append(payload)

        for container in containers:
            if not isinstance(container, list):
                continue

            for row in container:
                if not isinstance(row, dict):
                    continue

                date_value = (
                    row.get("tradingDate")
                    or row.get("holidayDate")
                    or row.get("date")
                )

                if not date_value:
                    continue

                parsed_date = pd.to_datetime(
                    date_value,
                    errors="coerce",
                    dayfirst=True,
                )

                if pd.isna(parsed_date):
                    continue

                if parsed_date.year == year:
                    holidays.add(parsed_date.date().isoformat())

    except Exception:
        return set()

    return holidays



@st.cache_data(ttl=21600, show_spinner=False)
def fetch_nse_holiday_details(year):
    """Return NSE trading holidays as {ISO date: holiday name}."""
    url = "https://www.nseindia.com/api/holiday-master?type=trading"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.nseindia.com/resources/exchange-communication-holidays",
    }
    details = {}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        containers = list(payload.values()) if isinstance(payload, dict) else [payload]
        for container in containers:
            if not isinstance(container, list):
                continue
            for row in container:
                if not isinstance(row, dict):
                    continue
                date_value = row.get("tradingDate") or row.get("holidayDate") or row.get("date")
                parsed = pd.to_datetime(date_value, errors="coerce", dayfirst=True)
                if pd.isna(parsed) or parsed.year != year:
                    continue
                name = row.get("description") or row.get("holidayDescription") or row.get("reason") or "Market Holiday"
                details[parsed.date().isoformat()] = str(name)
    except Exception as error:
        add_api_log(f"Holiday calendar unavailable: {error}", "WARNING")
    return details


def render_market_calendar(display_date=None):
    display_date = display_date or datetime.now(IST).date()
    holiday_details = fetch_nse_holiday_details(display_date.year)
    month_matrix = calendar.Calendar(firstweekday=0).monthdayscalendar(display_date.year, display_date.month)
    weekday_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    cells = [f'<div class="cal-head">{name}</div>' for name in weekday_names]
    for week in month_matrix:
        for weekday, day in enumerate(week):
            if day == 0:
                cells.append('<div class="cal-day cal-empty"></div>')
                continue
            day_date = display_date.replace(day=day)
            iso = day_date.isoformat()
            classes = ["cal-day"]
            note = "Trading Day"
            if weekday >= 5:
                classes.append("cal-weekend")
                note = "Weekend"
            if iso in holiday_details:
                classes.append("cal-holiday")
                note = holiday_details[iso]
            if day_date == datetime.now(IST).date():
                classes.append("cal-today")
            cells.append(f'<div class="{" ".join(classes)}"><div class="cal-number">{day}</div><div class="cal-note">{note}</div></div>')
    title = display_date.strftime("%B %Y")
    legend = "🟠 Holiday &nbsp; 🔴 Weekend &nbsp; 🔵 Today"
    render_html(f'<div class="market-calendar-wrap"><div class="market-calendar-title"><span>📅 NSE Market Calendar — {title}</span><span>{legend}</span></div><div class="market-calendar-grid">{"".join(cells)}</div></div>')


def calculate_previous_day_pivots(candles):
    """Classic pivots and CPR calculated from the latest completed trading session."""
    if candles.empty or "Datetime" not in candles.columns:
        return None
    frame = candles.copy()
    frame["SessionDate"] = frame["Datetime"].dt.date
    today = datetime.now(IST).date()
    completed = frame[frame["SessionDate"] < today]
    if completed.empty:
        unique_dates = sorted(frame["SessionDate"].dropna().unique())
        if len(unique_dates) < 2:
            return None
        session_date = unique_dates[-2]
    else:
        session_date = completed["SessionDate"].max()
    session = frame[frame["SessionDate"] == session_date]
    if session.empty:
        return None
    high = safe_float(session["High"].max())
    low = safe_float(session["Low"].min())
    close = safe_float(session.iloc[-1]["Close"])
    if not all(value > 0 for value in (high, low, close)):
        return None
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    bc = (high + low) / 2
    tc = 2 * pivot - bc
    if bc > tc:
        bc, tc = tc, bc
    return {"Date": session_date, "High": high, "Low": low, "Close": close, "Pivot": pivot, "R1": r1, "R2": r2, "R3": r3, "S1": s1, "S2": s2, "S3": s3, "BC": bc, "TC": tc}


def render_pivot_dashboard(pivots):
    if not pivots:
        st.warning("Previous-session candles are unavailable, so pivot points could not be calculated.")
        return
    cards = []
    for label in ["R3", "R2", "R1"]:
        cards.append(f'<div class="pivot-card pivot-resistance"><div class="pivot-label">{label} Resistance</div><div class="pivot-value">₹ {pivots[label]:,.2f}</div></div>')
    cards.append(f'<div class="pivot-card pivot-main"><div class="pivot-label">Central Pivot</div><div class="pivot-value">₹ {pivots["Pivot"]:,.2f}</div></div>')
    for label in ["S1", "S2", "S3"]:
        cards.append(f'<div class="pivot-card pivot-support"><div class="pivot-label">{label} Support</div><div class="pivot-value">₹ {pivots[label]:,.2f}</div></div>')
    cards.extend([
        f'<div class="pivot-card pivot-cpr"><div class="pivot-label">CPR Top (TC)</div><div class="pivot-value">₹ {pivots["TC"]:,.2f}</div></div>',
        f'<div class="pivot-card pivot-cpr"><div class="pivot-label">CPR Bottom (BC)</div><div class="pivot-value">₹ {pivots["BC"]:,.2f}</div></div>',
    ])
    st.subheader("🧭 Automatic Pivot Points & CPR")
    st.caption(f'Calculated automatically from previous completed session: {pivots["Date"].strftime("%d-%m-%Y")} | H ₹{pivots["High"]:,.2f} • L ₹{pivots["Low"]:,.2f} • C ₹{pivots["Close"]:,.2f}')
    render_html('<div class="pivot-grid">' + ''.join(cards) + '</div>')

def professional_market_status():
    now = datetime.now(IST)
    today = now.date()
    weekday = now.weekday()

    holidays = fetch_nse_trading_holidays(today.year)
    is_holiday = today.isoformat() in holidays

    market_open = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0,
    )
    market_close = now.replace(
        hour=15,
        minute=30,
        second=0,
        microsecond=0,
    )

    if is_holiday:
        return (
            False,
            now,
            "🟠 Exchange Holiday — live trading is closed.",
            "Holiday",
        )

    if weekday >= 5:
        return (
            False,
            now,
            "🔴 Weekend — live trading is closed.",
            "Closed",
        )

    if market_open <= now <= market_close:
        return (
            True,
            now,
            "🟢 Market Open — live values may change quickly.",
            "Open",
        )

    return (
        False,
        now,
        "🔴 Market Closed — showing the latest available session.",
        "Closed",
    )


def format_api_error(response):
    if isinstance(response, dict):
        remarks = response.get("remarks")
        if isinstance(remarks, dict):
            message = (
                remarks.get("error_message")
                or remarks.get("error_type")
                or remarks
            )
        else:
            message = remarks

        nested = response.get("data")
        if isinstance(nested, dict):
            nested = nested.get("data", nested)

        return str(message or nested or response)

    return str(response)


def market_status():
    is_open, now, note, _status = professional_market_status()
    return is_open, now, note


def make_beep_wav(
    frequency=880,
    duration=0.22,
    sample_rate=22050,
    volume=0.35,
):
    frame_count = int(duration * sample_rate)
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for index in range(frame_count):
            value = int(
                volume
                * 32767
                * math.sin(
                    2 * math.pi * frequency * index / sample_rate
                )
            )
            wav_file.writeframesraw(struct.pack("<h", value))

    return buffer.getvalue()


def play_signal_sound():
    encoded = base64.b64encode(make_beep_wav()).decode("ascii")

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{encoded}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DHAN API FUNCTIONS
# =========================================================

@st.cache_data(ttl=60)
def get_expiry_list(
    security_id,
    segment,
    client_id,
    access_token,
):
    url = "https://api.dhan.co/v2/optionchain/expirylist"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "access-token": access_token,
        "client-id": client_id,
    }

    payload = {
        "UnderlyingScrip": security_id,
        "UnderlyingSeg": segment,
    }

    response = request_with_retry(
        "POST",
        url,
        headers=headers,
        json=payload,
        timeout=20,
    )
    return response.json()


def get_option_chain(security_id, segment, expiry):
    url = "https://api.dhan.co/v2/optionchain"

    payload = {
        "UnderlyingScrip": security_id,
        "UnderlyingSeg": segment,
        "Expiry": expiry,
    }

    response = request_with_retry(
        "POST",
        url,
        headers=HEADERS,
        json=payload,
        timeout=20,
    )
    return response.json()


@st.cache_data(ttl=20)
def get_intraday_candles(
    security_id,
    exchange_segment,
    instrument,
    interval,
    client_id,
    access_token,
):
    now = datetime.now(IST)
    from_time = now - timedelta(days=7)

    url = "https://api.dhan.co/v2/charts/intraday"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "access-token": access_token,
        "client-id": client_id,
    }

    payload = {
        "securityId": str(security_id),
        "exchangeSegment": exchange_segment,
        "instrument": instrument,
        "interval": str(interval),
        "oi": False,
        "fromDate": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "toDate": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    response = request_with_retry(
        "POST",
        url,
        headers=headers,
        json=payload,
        timeout=25,
    )
    return response.json()


def candles_to_dataframe(response):
    required = ["open", "high", "low", "close", "volume", "timestamp"]

    if not isinstance(response, dict):
        return pd.DataFrame()

    if not all(key in response for key in required):
        return pd.DataFrame()

    lengths = [len(response.get(key, [])) for key in required]
    row_count = min(lengths) if lengths else 0

    if row_count == 0:
        return pd.DataFrame()

    frame = pd.DataFrame(
        {
            "Open": response["open"][:row_count],
            "High": response["high"][:row_count],
            "Low": response["low"][:row_count],
            "Close": response["close"][:row_count],
            "Volume": response["volume"][:row_count],
            "Timestamp": response["timestamp"][:row_count],
        }
    )

    frame["Datetime"] = pd.to_datetime(
        frame["Timestamp"],
        unit="s",
        utc=True,
    ).dt.tz_convert(IST)

    for column in ["Open", "High", "Low", "Close", "Volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame.dropna().sort_values("Datetime").reset_index(drop=True)


# =========================================================
# TECHNICAL INDICATORS
# =========================================================

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    relative_strength = average_gain / average_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + relative_strength))

    return rsi.fillna(50)


def calculate_vwap(frame):
    typical_price = (
        frame["High"] + frame["Low"] + frame["Close"]
    ) / 3

    cumulative_volume = frame["Volume"].cumsum().replace(0, pd.NA)

    return (
        (typical_price * frame["Volume"]).cumsum()
        / cumulative_volume
    ).ffill()


def calculate_atr(frame, period=10):
    previous_close = frame["Close"].shift(1)

    true_range = pd.concat(
        [
            frame["High"] - frame["Low"],
            (frame["High"] - previous_close).abs(),
            (frame["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def calculate_supertrend(frame, period=10, multiplier=3.0):
    output = frame.copy()

    if output.empty:
        empty_float = pd.Series(dtype="float64")
        empty_int = pd.Series(dtype="int64")
        return empty_float, empty_int

    atr = calculate_atr(output, period)
    hl2 = (output["High"] + output["Low"]) / 2

    basic_upper = hl2 + multiplier * atr
    basic_lower = hl2 - multiplier * atr

    final_upper = pd.Series(index=output.index, dtype="float64")
    final_lower = pd.Series(index=output.index, dtype="float64")
    direction = pd.Series(0, index=output.index, dtype="int64")
    supertrend = pd.Series(index=output.index, dtype="float64")

    first_valid = atr.first_valid_index()

    if first_valid is None:
        return supertrend, direction

    first_position = output.index.get_loc(first_valid)

    final_upper.iloc[first_position] = basic_upper.iloc[first_position]
    final_lower.iloc[first_position] = basic_lower.iloc[first_position]
    direction.iloc[first_position] = 1
    supertrend.iloc[first_position] = final_lower.iloc[first_position]

    for position in range(first_position + 1, len(output)):
        previous = position - 1

        previous_upper = final_upper.iloc[previous]
        previous_lower = final_lower.iloc[previous]

        if not math.isfinite(safe_float(previous_upper, float("nan"))):
            previous_upper = basic_upper.iloc[previous]

        if not math.isfinite(safe_float(previous_lower, float("nan"))):
            previous_lower = basic_lower.iloc[previous]

        if (
            basic_upper.iloc[position] < previous_upper
            or output["Close"].iloc[previous] > previous_upper
        ):
            final_upper.iloc[position] = basic_upper.iloc[position]
        else:
            final_upper.iloc[position] = previous_upper

        if (
            basic_lower.iloc[position] > previous_lower
            or output["Close"].iloc[previous] < previous_lower
        ):
            final_lower.iloc[position] = basic_lower.iloc[position]
        else:
            final_lower.iloc[position] = previous_lower

        previous_direction = direction.iloc[previous]

        if previous_direction >= 0:
            if output["Close"].iloc[position] < final_lower.iloc[position]:
                direction.iloc[position] = -1
                supertrend.iloc[position] = final_upper.iloc[position]
            else:
                direction.iloc[position] = 1
                supertrend.iloc[position] = final_lower.iloc[position]
        else:
            if output["Close"].iloc[position] > final_upper.iloc[position]:
                direction.iloc[position] = 1
                supertrend.iloc[position] = final_lower.iloc[position]
            else:
                direction.iloc[position] = -1
                supertrend.iloc[position] = final_upper.iloc[position]

    supertrend = supertrend.ffill()
    direction = direction.replace(0, pd.NA).ffill().fillna(0).astype(int)

    return supertrend, direction


def enrich_candles(frame):
    if frame.empty:
        return frame

    output = frame.copy()
    output["RSI"] = calculate_rsi(output["Close"], 14)
    output["VWAP"] = calculate_vwap(output)
    output["ATR"] = calculate_atr(output, 10)

    supertrend, direction = calculate_supertrend(
        output,
        period=10,
        multiplier=3.0,
    )

    output["Supertrend"] = supertrend
    output["TrendDirection"] = direction

    return output



# =========================================================
# SMART MONEY / PRICE ACTION HEURISTICS
# =========================================================

def detect_fair_value_gaps(frame, lookback=80):
    if frame.empty or len(frame) < 3:
        return []

    gaps = []
    recent = frame.tail(lookback).reset_index(drop=True)

    for index in range(2, len(recent)):
        first = recent.iloc[index - 2]
        third = recent.iloc[index]

        if safe_float(third["Low"]) > safe_float(first["High"]):
            gaps.append(
                {
                    "Type": "Bullish FVG",
                    "Low": safe_float(first["High"]),
                    "High": safe_float(third["Low"]),
                    "Time": third["Datetime"],
                }
            )

        if safe_float(third["High"]) < safe_float(first["Low"]):
            gaps.append(
                {
                    "Type": "Bearish FVG",
                    "Low": safe_float(third["High"]),
                    "High": safe_float(first["Low"]),
                    "Time": third["Datetime"],
                }
            )

    return gaps[-5:]


def detect_order_blocks(frame, lookback=60):
    if frame.empty or len(frame) < 5:
        return []

    recent = frame.tail(lookback).reset_index(drop=True)
    atr_value = safe_float(recent["ATR"].iloc[-1], 0.0)
    blocks = []

    for index in range(1, len(recent) - 2):
        candle = recent.iloc[index]
        next_one = recent.iloc[index + 1]
        next_two = recent.iloc[index + 2]

        displacement_up = (
            safe_float(next_two["Close"]) - safe_float(candle["High"])
        )
        displacement_down = (
            safe_float(candle["Low"]) - safe_float(next_two["Close"])
        )

        if (
            safe_float(candle["Close"]) < safe_float(candle["Open"])
            and displacement_up > max(atr_value * 0.6, 1)
        ):
            blocks.append(
                {
                    "Type": "Bullish Order Block",
                    "Low": safe_float(candle["Low"]),
                    "High": safe_float(candle["High"]),
                    "Time": candle["Datetime"],
                }
            )

        if (
            safe_float(candle["Close"]) > safe_float(candle["Open"])
            and displacement_down > max(atr_value * 0.6, 1)
        ):
            blocks.append(
                {
                    "Type": "Bearish Order Block",
                    "Low": safe_float(candle["Low"]),
                    "High": safe_float(candle["High"]),
                    "Time": candle["Datetime"],
                }
            )

    return blocks[-5:]


def detect_liquidity_levels(frame, lookback=80):
    if frame.empty:
        return 0.0, 0.0

    recent = frame.tail(lookback)
    buy_side = safe_float(recent["High"].nlargest(3).mean())
    sell_side = safe_float(recent["Low"].nsmallest(3).mean())

    return buy_side, sell_side


def detect_institutional_activity(frame, lookback=40):
    if frame.empty or len(frame) < 5:
        return "Unavailable", 0.0

    recent = frame.tail(lookback).copy()
    average_volume = safe_float(recent["Volume"].rolling(20).mean().iloc[-1])
    last_volume = safe_float(recent["Volume"].iloc[-1])
    volume_ratio = last_volume / average_volume if average_volume else 0.0

    body = abs(
        safe_float(recent["Close"].iloc[-1])
        - safe_float(recent["Open"].iloc[-1])
    )
    atr_value = safe_float(recent["ATR"].iloc[-1])

    if volume_ratio >= 1.8 and body >= atr_value * 0.8:
        direction = (
            "Bullish Institutional Activity"
            if recent["Close"].iloc[-1] > recent["Open"].iloc[-1]
            else "Bearish Institutional Activity"
        )
        return direction, volume_ratio

    if volume_ratio >= 1.3:
        return "Elevated Institutional Activity", volume_ratio

    return "Normal Activity", volume_ratio


def build_professional_candlestick(
    candles,
    support,
    resistance,
    max_pain,
    order_blocks,
    fair_value_gaps,
    buy_liquidity,
    sell_liquidity,
):
    recent = candles.tail(180).copy()

    figure = go.Figure()

    figure.add_trace(
        go.Candlestick(
            x=recent["Datetime"],
            open=recent["Open"],
            high=recent["High"],
            low=recent["Low"],
            close=recent["Close"],
            name="Price",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=recent["Datetime"],
            y=recent["VWAP"],
            mode="lines",
            name="VWAP",
            line={"width": 1.5},
        )
    )

    valid_supertrend = recent["Supertrend"].where(
        recent["Supertrend"].apply(lambda value: math.isfinite(safe_float(value)))
    )

    figure.add_trace(
        go.Scatter(
            x=recent["Datetime"],
            y=valid_supertrend,
            mode="lines",
            name="Supertrend",
            line={"width": 1.4},
        )
    )

    for label, level in [
        ("Support", support),
        ("Resistance", resistance),
        ("Max Pain", max_pain),
        ("Buy-side Liquidity", buy_liquidity),
        ("Sell-side Liquidity", sell_liquidity),
    ]:
        if level:
            figure.add_hline(
                y=level,
                line_dash="dot",
                annotation_text=label,
                annotation_position="top left",
            )

    for block in order_blocks[-2:]:
        figure.add_hrect(
            y0=block["Low"],
            y1=block["High"],
            opacity=0.12,
            line_width=0,
            annotation_text=block["Type"],
            annotation_position="top left",
        )

    for gap in fair_value_gaps[-2:]:
        figure.add_hrect(
            y0=gap["Low"],
            y1=gap["High"],
            opacity=0.08,
            line_width=0,
            annotation_text=gap["Type"],
            annotation_position="bottom right",
        )

    figure.update_layout(
        height=620,
        margin={"l": 10, "r": 10, "t": 35, "b": 10},
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.02, "x": 0},
        template="plotly_white",
        title="TradingView-style Price Action Chart",
    )

    return figure


def smc_bias(
    spot_price,
    order_blocks,
    fair_value_gaps,
    buy_liquidity,
    sell_liquidity,
):
    bullish = 0
    bearish = 0
    reasons = []

    for block in order_blocks[-3:]:
        if block["Type"].startswith("Bullish") and spot_price >= block["High"]:
            bullish += 1
            reasons.append("Price is above a bullish order block.")
        if block["Type"].startswith("Bearish") and spot_price <= block["Low"]:
            bearish += 1
            reasons.append("Price is below a bearish order block.")

    for gap in fair_value_gaps[-3:]:
        if gap["Type"].startswith("Bullish") and spot_price >= gap["High"]:
            bullish += 1
            reasons.append("Bullish FVG remains below price.")
        if gap["Type"].startswith("Bearish") and spot_price <= gap["Low"]:
            bearish += 1
            reasons.append("Bearish FVG remains above price.")

    if buy_liquidity and spot_price > buy_liquidity:
        bullish += 1
        reasons.append("Buy-side liquidity has been swept.")
    if sell_liquidity and spot_price < sell_liquidity:
        bearish += 1
        reasons.append("Sell-side liquidity has been swept.")

    if bullish > bearish:
        return "Bullish SMC Bias", bullish - bearish, reasons
    if bearish > bullish:
        return "Bearish SMC Bias", bearish - bullish, reasons
    return "Neutral SMC Bias", 0, reasons or ["No clear SMC imbalance."]


# =========================================================
# OPTION ANALYTICS
# =========================================================

def calculate_max_pain(dataframe):
    if dataframe.empty:
        return 0.0

    strikes = dataframe["Strike"].astype(float).tolist()
    best_strike = 0.0
    minimum_total_payout = None

    for settlement_price in strikes:
        call_payout = (
            (settlement_price - dataframe["Strike"]).clip(lower=0)
            * dataframe["CE OI"]
        ).sum()

        put_payout = (
            (dataframe["Strike"] - settlement_price).clip(lower=0)
            * dataframe["PE OI"]
        ).sum()

        total_payout = call_payout + put_payout

        if minimum_total_payout is None or total_payout < minimum_total_payout:
            minimum_total_payout = total_payout
            best_strike = settlement_price

    return float(best_strike)


def analyse_oi_build_up(
    total_ce_change,
    total_pe_change,
    atm_ce_change,
    atm_pe_change,
):
    notes = []

    if total_ce_change > 0 and total_pe_change > 0:
        if total_pe_change > total_ce_change:
            summary = "Put writing is stronger"
            bias = "Bullish"
        elif total_ce_change > total_pe_change:
            summary = "Call writing is stronger"
            bias = "Bearish"
        else:
            summary = "Call and Put writing are balanced"
            bias = "Neutral"

    elif total_ce_change > 0 and total_pe_change <= 0:
        summary = "Call writing with Put unwinding"
        bias = "Bearish"

    elif total_pe_change > 0 and total_ce_change <= 0:
        summary = "Put writing with Call unwinding"
        bias = "Bullish"

    else:
        summary = "Both sides show net unwinding"
        bias = "Neutral / Volatile"

    if atm_pe_change > atm_ce_change:
        notes.append("ATM Put OI change is stronger.")
    elif atm_ce_change > atm_pe_change:
        notes.append("ATM Call OI change is stronger.")
    else:
        notes.append("ATM OI change is balanced.")

    return summary, bias, notes


def build_signal_and_score(
    pcr,
    total_ce_change,
    total_pe_change,
    atm_ce_change,
    atm_pe_change,
    spot_price,
    support,
    resistance,
    max_pain,
    latest_rsi,
    latest_vwap,
    trend_direction,
):
    bullish_points = 0
    bearish_points = 0
    reasons = []

    if pcr >= 1.25:
        bullish_points += 3
        reasons.append("PCR strongly favours Put OI.")
    elif pcr >= 1.10:
        bullish_points += 2
        reasons.append("PCR moderately favours Put OI.")
    elif pcr <= 0.75:
        bearish_points += 3
        reasons.append("PCR strongly favours Call OI.")
    elif pcr <= 0.90:
        bearish_points += 2
        reasons.append("PCR moderately favours Call OI.")
    else:
        reasons.append("PCR is near neutral.")

    if total_pe_change > total_ce_change:
        bullish_points += 2
        reasons.append("Total Put OI change is stronger.")
    elif total_ce_change > total_pe_change:
        bearish_points += 2
        reasons.append("Total Call OI change is stronger.")

    if atm_pe_change > atm_ce_change:
        bullish_points += 1
        reasons.append("ATM Put OI change is stronger.")
    elif atm_ce_change > atm_pe_change:
        bearish_points += 1
        reasons.append("ATM Call OI change is stronger.")

    if support and spot_price > support:
        bullish_points += 1
        reasons.append("Spot is above Put-OI support.")

    if resistance and spot_price < resistance:
        bearish_points += 1
        reasons.append("Spot is below Call-OI resistance.")

    if max_pain:
        if spot_price > max_pain:
            bullish_points += 1
            reasons.append("Spot is above Max Pain.")
        elif spot_price < max_pain:
            bearish_points += 1
            reasons.append("Spot is below Max Pain.")

    if latest_vwap:
        if spot_price > latest_vwap:
            bullish_points += 2
            reasons.append("Spot is above VWAP.")
        elif spot_price < latest_vwap:
            bearish_points += 2
            reasons.append("Spot is below VWAP.")

    if latest_rsi >= 60:
        bullish_points += 2
        reasons.append("RSI confirms bullish momentum.")
    elif latest_rsi <= 40:
        bearish_points += 2
        reasons.append("RSI confirms bearish momentum.")
    else:
        reasons.append("RSI is neutral.")

    if trend_direction == 1:
        bullish_points += 2
        reasons.append("Supertrend direction is bullish.")
    elif trend_direction == -1:
        bearish_points += 2
        reasons.append("Supertrend direction is bearish.")

    net_score = bullish_points - bearish_points
    total_points = max(bullish_points + bearish_points, 1)

    if net_score >= 4:
        recommendation = "BUY CE BIAS"
        sentiment = "Bullish"
        signal_class = "signal-bullish"
        quality_score = min(
            95,
            max(60, round(55 + 40 * bullish_points / total_points)),
        )

    elif net_score <= -4:
        recommendation = "BUY PE BIAS"
        sentiment = "Bearish"
        signal_class = "signal-bearish"
        quality_score = min(
            95,
            max(60, round(55 + 40 * bearish_points / total_points)),
        )

    else:
        recommendation = "WAIT / NO TRADE"
        sentiment = "Sideways"
        signal_class = "signal-neutral"
        quality_score = min(72, max(40, 58 - abs(net_score) * 2))

    return (
        recommendation,
        sentiment,
        signal_class,
        quality_score,
        reasons,
        bullish_points,
        bearish_points,
    )


def breakout_breakdown_status(
    spot_price,
    support,
    resistance,
    buffer_points,
):
    breakout_level = resistance + buffer_points
    breakdown_level = support - buffer_points

    if resistance and spot_price > breakout_level:
        return (
            "BREAKOUT CONFIRMED",
            "alert-breakout",
            f"Spot is above {breakout_level:,.0f}.",
            breakout_level,
            breakdown_level,
        )

    if support and spot_price < breakdown_level:
        return (
            "BREAKDOWN CONFIRMED",
            "alert-breakdown",
            f"Spot is below {breakdown_level:,.0f}.",
            breakout_level,
            breakdown_level,
        )

    return (
        "WAIT FOR CONFIRMATION",
        "alert-range",
        (
            f"Watch breakout above {breakout_level:,.0f} "
            f"or breakdown below {breakdown_level:,.0f}."
        ),
        breakout_level,
        breakdown_level,
    )


def select_option_contract(
    dataframe,
    recommendation,
    atm_strike,
):
    row = dataframe.loc[dataframe["Strike"] == atm_strike]

    if row.empty:
        return "WAIT", atm_strike, 0.0

    candidate = row.iloc[0]

    if recommendation == "BUY CE BIAS":
        return "CE", atm_strike, safe_float(candidate["CE LTP"])

    if recommendation == "BUY PE BIAS":
        return "PE", atm_strike, safe_float(candidate["PE LTP"])

    return "WAIT", atm_strike, 0.0


def calculate_option_premium_levels(
    premium,
    recommendation,
    atr_reference,
):
    if recommendation == "WAIT / NO TRADE" or premium <= 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    entry = premium

    # Premium SL remains conservative. ATR reference adds a small buffer.
    risk_percent = 0.20
    if atr_reference > 0:
        risk_percent = min(0.28, max(0.15, atr_reference / 1000))

    stop_loss = max(0.05, premium * (1 - risk_percent))
    risk_amount = entry - stop_loss

    target1 = entry + risk_amount * 1.0
    target2 = entry + risk_amount * 1.5
    target3 = entry + risk_amount * 2.0

    return entry, stop_loss, target1, target2, target3


def add_signal_to_log(
    index_name,
    expiry,
    recommendation,
    strike,
    option_type,
    premium_entry,
    premium_stop,
    target1,
    quality_score,
):
    now_text = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "Time": now_text,
        "Index": index_name,
        "Expiry": expiry,
        "Signal": recommendation,
        "Strike": strike,
        "Option": option_type,
        "Entry Premium": premium_entry,
        "Stop Premium": premium_stop,
        "Target 1": target1,
        "Quality Score": quality_score,
    }

    existing = st.session_state.signal_log

    if not existing or (
        existing[-1]["Signal"] != recommendation
        or existing[-1]["Index"] != index_name
        or existing[-1]["Strike"] != strike
    ):
        existing.append(entry)




# =========================================================
# MULTI-TIMEFRAME ENGINE
# =========================================================

def timeframe_snapshot(frame):
    if frame.empty:
        return {
            "Available": False,
            "Close": 0.0,
            "RSI": 50.0,
            "VWAP": 0.0,
            "ATR": 0.0,
            "Trend": 0,
            "Supertrend": 0.0,
            "Bias": "Unavailable",
            "Score": 0,
        }

    latest = frame.iloc[-1]
    close_price = safe_float(latest["Close"])
    rsi_value = safe_float(latest["RSI"], 50.0)
    vwap_value = safe_float(latest["VWAP"])
    atr_value = safe_float(latest["ATR"])
    trend_value = safe_int(latest["TrendDirection"])
    supertrend_value = safe_float(latest["Supertrend"])

    bullish = 0
    bearish = 0

    if close_price > vwap_value:
        bullish += 2
    elif close_price < vwap_value:
        bearish += 2

    if rsi_value >= 58:
        bullish += 2
    elif rsi_value <= 42:
        bearish += 2

    if trend_value == 1:
        bullish += 3
    elif trend_value == -1:
        bearish += 3

    net_score = bullish - bearish

    if net_score >= 3:
        bias = "Bullish"
    elif net_score <= -3:
        bias = "Bearish"
    else:
        bias = "Neutral"

    return {
        "Available": True,
        "Close": close_price,
        "RSI": rsi_value,
        "VWAP": vwap_value,
        "ATR": atr_value,
        "Trend": trend_value,
        "Supertrend": supertrend_value,
        "Bias": bias,
        "Score": net_score,
    }


def mtf_confirmation(snapshot_5m, snapshot_15m):
    reasons = []
    confirmation_points = 0

    if not snapshot_5m["Available"] or not snapshot_15m["Available"]:
        return {
            "Bias": "Unavailable",
            "Class": "mtf-neutral",
            "Confidence Boost": 0,
            "Points": 0,
            "Reasons": ["Both 5-minute and 15-minute data are required."],
        }

    bias_5m = snapshot_5m["Bias"]
    bias_15m = snapshot_15m["Bias"]

    if bias_5m == bias_15m and bias_5m == "Bullish":
        confirmation_points += 5
        reasons.append("5-minute and 15-minute trends both agree bullish.")

    elif bias_5m == bias_15m and bias_5m == "Bearish":
        confirmation_points -= 5
        reasons.append("5-minute and 15-minute trends both agree bearish.")

    else:
        reasons.append(
            f"Timeframes disagree: 5m={bias_5m}, 15m={bias_15m}."
        )

    if snapshot_5m["Trend"] == snapshot_15m["Trend"] == 1:
        confirmation_points += 2
        reasons.append("Supertrend agrees bullish on both timeframes.")

    elif snapshot_5m["Trend"] == snapshot_15m["Trend"] == -1:
        confirmation_points -= 2
        reasons.append("Supertrend agrees bearish on both timeframes.")

    if (
        snapshot_5m["Close"] > snapshot_5m["VWAP"]
        and snapshot_15m["Close"] > snapshot_15m["VWAP"]
    ):
        confirmation_points += 2
        reasons.append("Price is above VWAP on both timeframes.")

    elif (
        snapshot_5m["Close"] < snapshot_5m["VWAP"]
        and snapshot_15m["Close"] < snapshot_15m["VWAP"]
    ):
        confirmation_points -= 2
        reasons.append("Price is below VWAP on both timeframes.")

    if snapshot_5m["RSI"] >= 55 and snapshot_15m["RSI"] >= 55:
        confirmation_points += 1
        reasons.append("RSI confirms bullish momentum on both timeframes.")

    elif snapshot_5m["RSI"] <= 45 and snapshot_15m["RSI"] <= 45:
        confirmation_points -= 1
        reasons.append("RSI confirms bearish momentum on both timeframes.")

    if confirmation_points >= 6:
        bias = "Strong Bullish Confirmation"
        css_class = "mtf-bullish"
        confidence_boost = 8
    elif confirmation_points >= 3:
        bias = "Bullish Confirmation"
        css_class = "mtf-bullish"
        confidence_boost = 5
    elif confirmation_points <= -6:
        bias = "Strong Bearish Confirmation"
        css_class = "mtf-bearish"
        confidence_boost = 8
    elif confirmation_points <= -3:
        bias = "Bearish Confirmation"
        css_class = "mtf-bearish"
        confidence_boost = 5
    else:
        bias = "Mixed / No Confirmation"
        css_class = "mtf-neutral"
        confidence_boost = -8

    return {
        "Bias": bias,
        "Class": css_class,
        "Confidence Boost": confidence_boost,
        "Points": confirmation_points,
        "Reasons": reasons,
    }


def refine_recommendation_with_mtf(
    recommendation,
    quality_score,
    mtf_result,
    snapshot_5m,
    snapshot_15m,
):
    refined = recommendation
    refined_score = quality_score
    notes = []

    mtf_bias = mtf_result["Bias"]
    boost = mtf_result["Confidence Boost"]

    if recommendation == "BUY CE BIAS":
        if "Bullish" in mtf_bias:
            refined_score += boost
            notes.append("CE bias confirmed by 5m + 15m.")
        elif "Bearish" in mtf_bias:
            refined = "WAIT / NO TRADE"
            refined_score = min(refined_score, 55)
            notes.append("CE bias cancelled because MTF confirmation is bearish.")
        else:
            refined_score += boost
            notes.append("CE bias reduced because MTF confirmation is mixed.")

    elif recommendation == "BUY PE BIAS":
        if "Bearish" in mtf_bias:
            refined_score += boost
            notes.append("PE bias confirmed by 5m + 15m.")
        elif "Bullish" in mtf_bias:
            refined = "WAIT / NO TRADE"
            refined_score = min(refined_score, 55)
            notes.append("PE bias cancelled because MTF confirmation is bullish.")
        else:
            refined_score += boost
            notes.append("PE bias reduced because MTF confirmation is mixed.")

    else:
        if "Strong Bullish" in mtf_bias:
            refined = "BUY CE BIAS"
            refined_score = max(refined_score, 68)
            notes.append("MTF engine upgraded WAIT to cautious CE bias.")
        elif "Strong Bearish" in mtf_bias:
            refined = "BUY PE BIAS"
            refined_score = max(refined_score, 68)
            notes.append("MTF engine upgraded WAIT to cautious PE bias.")
        else:
            notes.append("MTF engine keeps the signal at WAIT.")

    refined_score = max(35, min(96, int(round(refined_score))))

    return refined, refined_score, notes



def mtf_trade_direction(snapshot):
    if not snapshot.get("Available"):
        return "UNAVAILABLE"

    bullish_points = 0
    bearish_points = 0

    if snapshot["Trend"] == 1:
        bullish_points += 3
    elif snapshot["Trend"] == -1:
        bearish_points += 3

    if snapshot["Close"] > snapshot["VWAP"]:
        bullish_points += 2
    elif snapshot["Close"] < snapshot["VWAP"]:
        bearish_points += 2

    if snapshot["RSI"] >= 55:
        bullish_points += 2
    elif snapshot["RSI"] <= 45:
        bearish_points += 2

    if bullish_points - bearish_points >= 3:
        return "BUY CE"

    if bearish_points - bullish_points >= 3:
        return "BUY PE"

    return "WAIT"


def calculate_mtf_agreement(snapshot_5m, snapshot_15m):
    checks = []

    direction_5m = mtf_trade_direction(snapshot_5m)
    direction_15m = mtf_trade_direction(snapshot_15m)

    checks.append(direction_5m == direction_15m and direction_5m != "WAIT")
    checks.append(snapshot_5m["Trend"] == snapshot_15m["Trend"])
    checks.append(
        (snapshot_5m["Close"] > snapshot_5m["VWAP"])
        == (snapshot_15m["Close"] > snapshot_15m["VWAP"])
    )
    checks.append(
        (snapshot_5m["RSI"] >= 50)
        == (snapshot_15m["RSI"] >= 50)
    )

    valid_checks = [bool(value) for value in checks]
    agreement = int(round(sum(valid_checks) / len(valid_checks) * 100))

    return agreement, direction_5m, direction_15m


def calculate_ai_confidence(
    base_score,
    agreement,
    direction_5m,
    direction_15m,
    mtf_points,
):
    confidence = float(base_score)

    if direction_5m == direction_15m and direction_5m in {"BUY CE", "BUY PE"}:
        confidence += 8

    if agreement >= 100:
        confidence += 5
    elif agreement >= 75:
        confidence += 2
    elif agreement <= 50:
        confidence -= 10

    confidence += min(5, abs(mtf_points) * 0.5)

    return max(35, min(97, int(round(confidence))))


def final_mtf_recommendation(
    base_recommendation,
    direction_5m,
    direction_15m,
    agreement,
    confidence,
):
    if (
        direction_5m == direction_15m == "BUY CE"
        and agreement >= 75
        and confidence >= 65
    ):
        return "BUY CE"

    if (
        direction_5m == direction_15m == "BUY PE"
        and agreement >= 75
        and confidence >= 65
    ):
        return "BUY PE"

    if direction_5m != direction_15m:
        return "WAIT — TIMEFRAMES NOT ALIGNED"

    if base_recommendation == "BUY CE BIAS":
        return "WATCH CE — WAIT FOR CONFIRMATION"

    if base_recommendation == "BUY PE BIAS":
        return "WATCH PE — WAIT FOR CONFIRMATION"

    return "WAIT / NO TRADE"



def build_three_timeframe_grade(
    snapshot_5m,
    snapshot_15m,
    snapshot_60m,
    agreement_5_15,
    ai_confidence,
):
    direction_5m = mtf_trade_direction(snapshot_5m)
    direction_15m = mtf_trade_direction(snapshot_15m)
    direction_60m = mtf_trade_direction(snapshot_60m)

    aligned_count = 0
    directions = [direction_5m, direction_15m, direction_60m]

    for direction in {"BUY CE", "BUY PE"}:
        aligned_count = max(aligned_count, directions.count(direction))

    if (
        direction_5m == direction_15m == direction_60m == "BUY CE"
        and agreement_5_15 >= 75
        and ai_confidence >= 80
    ):
        return {
            "Grade": "STRONG BUY CE",
            "Class": "grade-strong-buy",
            "Direction": "BUY CE",
            "Score": min(97, ai_confidence + 4),
            "Reason": "5m, 15m and 60m all confirm bullish conditions.",
        }

    if (
        direction_5m == direction_15m == direction_60m == "BUY PE"
        and agreement_5_15 >= 75
        and ai_confidence >= 80
    ):
        return {
            "Grade": "STRONG BUY PE",
            "Class": "grade-strong-buy",
            "Direction": "BUY PE",
            "Score": min(97, ai_confidence + 4),
            "Reason": "5m, 15m and 60m all confirm bearish conditions.",
        }

    if (
        direction_5m == direction_15m == "BUY CE"
        and direction_60m in {"BUY CE", "WAIT"}
        and ai_confidence >= 68
    ):
        return {
            "Grade": "MODERATE BUY CE",
            "Class": "grade-moderate-buy",
            "Direction": "BUY CE",
            "Score": ai_confidence,
            "Reason": "5m and 15m agree bullish; 60m is not opposing.",
        }

    if (
        direction_5m == direction_15m == "BUY PE"
        and direction_60m in {"BUY PE", "WAIT"}
        and ai_confidence >= 68
    ):
        return {
            "Grade": "MODERATE BUY PE",
            "Class": "grade-moderate-buy",
            "Direction": "BUY PE",
            "Score": ai_confidence,
            "Reason": "5m and 15m agree bearish; 60m is not opposing.",
        }

    if direction_5m != direction_15m:
        return {
            "Grade": "WAIT — TIMEFRAMES NOT ALIGNED",
            "Class": "grade-wait",
            "Direction": "WAIT",
            "Score": ai_confidence,
            "Reason": "5m and 15m disagree, so no fresh entry is allowed.",
        }

    if direction_60m not in {"WAIT", direction_15m}:
        return {
            "Grade": "AVOID — HIGHER TIMEFRAME OPPOSING",
            "Class": "grade-avoid",
            "Direction": "WAIT",
            "Score": min(ai_confidence, 55),
            "Reason": "60m trend opposes the lower-timeframe setup.",
        }

    return {
        "Grade": "WAIT — NO HIGH-QUALITY SETUP",
        "Class": "grade-wait",
        "Direction": "WAIT",
        "Score": min(ai_confidence, 65),
        "Reason": "Conditions are incomplete or confidence is below threshold.",
    }



def directional_bias_plan(
    snapshot_5m,
    snapshot_15m,
    snapshot_60m,
    spot_price,
    support,
    resistance,
    atm_strike,
):
    direction_5m = mtf_trade_direction(snapshot_5m)
    direction_15m = mtf_trade_direction(snapshot_15m)
    direction_60m = mtf_trade_direction(snapshot_60m)

    bullish_weight = 0
    bearish_weight = 0

    weight_map = [
        (direction_60m, 40),
        (direction_15m, 40),
        (direction_5m, 20),
    ]

    for direction, weight in weight_map:
        if direction == "BUY CE":
            bullish_weight += weight
        elif direction == "BUY PE":
            bearish_weight += weight

    if bullish_weight > bearish_weight:
        bias = "BULLISH — WATCH CE"
        option_side = "CE"
        trigger = resistance
        invalidation = support
    elif bearish_weight > bullish_weight:
        bias = "BEARISH — WATCH PE"
        option_side = "PE"
        trigger = support
        invalidation = resistance
    else:
        bias = "SIDEWAYS — NO TRADE"
        option_side = "WAIT"
        trigger = 0.0
        invalidation = 0.0

    return {
        "Bias": bias,
        "OptionSide": option_side,
        "RecommendedStrike": atm_strike,
        "Trigger": trigger,
        "Invalidation": invalidation,
        "BullishWeight": bullish_weight,
        "BearishWeight": bearish_weight,
    }


def refined_option_plan(
    direction,
    option_type,
    premium_entry,
    premium_stop,
    premium_target1,
    premium_target2,
    premium_target3,
):
    if direction not in {"BUY CE", "BUY PE"}:
        return {
            "Action": "WAIT",
            "Option": "NO TRADE",
            "Entry": 0.0,
            "Stop": 0.0,
            "Target1": 0.0,
            "Target2": 0.0,
            "Target3": 0.0,
            "RiskReward": "N/A",
        }

    risk = max(premium_entry - premium_stop, 0.0)
    reward = max(premium_target2 - premium_entry, 0.0)
    rr = reward / risk if risk > 0 else 0.0

    return {
        "Action": direction,
        "Option": option_type,
        "Entry": premium_entry,
        "Stop": premium_stop,
        "Target1": premium_target1,
        "Target2": premium_target2,
        "Target3": premium_target3,
        "RiskReward": f"1:{rr:.2f}" if rr > 0 else "N/A",
    }


# =========================================================
# PAPER TRADING & BACKTESTING
# =========================================================

def open_paper_position(
    index_name,
    expiry,
    option_type,
    strike,
    entry_price,
    quantity,
    stop_price,
    target_price,
):
    if option_type not in {"CE", "PE"}:
        return False, "No valid CE/PE signal available."

    if entry_price <= 0 or quantity <= 0:
        return False, "Entry price and quantity must be greater than zero."

    estimated_cost = entry_price * quantity

    if estimated_cost > st.session_state.paper_balance:
        return False, "Insufficient paper-trading balance."

    position = {
        "ID": len(st.session_state.paper_positions) + len(
            st.session_state.paper_trades
        ) + 1,
        "Opened": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
        "Index": index_name,
        "Expiry": expiry,
        "Option": option_type,
        "Strike": float(strike),
        "Entry": float(entry_price),
        "Quantity": int(quantity),
        "Stop": float(stop_price),
        "Target": float(target_price),
        "Status": "OPEN",
    }

    st.session_state.paper_balance -= estimated_cost
    st.session_state.paper_positions.append(position)

    return True, f"Paper position opened: {strike:.0f} {option_type}"


def current_option_price(
    option_dataframe,
    strike,
    option_type,
):
    matching = option_dataframe.loc[
        option_dataframe["Strike"] == float(strike)
    ]

    if matching.empty:
        return 0.0

    row = matching.iloc[0]

    if option_type == "CE":
        return safe_float(row["CE LTP"])

    if option_type == "PE":
        return safe_float(row["PE LTP"])

    return 0.0


def close_paper_position(
    position_id,
    option_dataframe,
    exit_reason="Manual Exit",
):
    positions = st.session_state.paper_positions

    for position in positions:
        if position["ID"] != position_id:
            continue

        exit_price = current_option_price(
            option_dataframe,
            position["Strike"],
            position["Option"],
        )

        if exit_price <= 0:
            return False, "Current option price is unavailable."

        quantity = position["Quantity"]
        entry_cost = position["Entry"] * quantity
        exit_value = exit_price * quantity
        pnl = exit_value - entry_cost

        trade = dict(position)
        trade.update(
            {
                "Closed": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
                "Exit": exit_price,
                "PnL": pnl,
                "Exit Reason": exit_reason,
                "Status": "CLOSED",
            }
        )

        st.session_state.paper_balance += exit_value
        st.session_state.paper_trades.append(trade)
        st.session_state.paper_positions = [
            item for item in positions if item["ID"] != position_id
        ]

        return True, f"Position closed. Paper P&L: ₹{pnl:,.2f}"

    return False, "Position was not found."


def auto_manage_paper_positions(option_dataframe):
    closed_messages = []

    for position in list(st.session_state.paper_positions):
        live_price = current_option_price(
            option_dataframe,
            position["Strike"],
            position["Option"],
        )

        if live_price <= 0:
            continue

        if position["Stop"] > 0 and live_price <= position["Stop"]:
            success, message = close_paper_position(
                position["ID"],
                option_dataframe,
                "Stop Loss",
            )
            if success:
                closed_messages.append(message)

        elif position["Target"] > 0 and live_price >= position["Target"]:
            success, message = close_paper_position(
                position["ID"],
                option_dataframe,
                "Target",
            )
            if success:
                closed_messages.append(message)

    return closed_messages


def paper_positions_dataframe(option_dataframe):
    rows = []

    for position in st.session_state.paper_positions:
        live_price = current_option_price(
            option_dataframe,
            position["Strike"],
            position["Option"],
        )

        pnl = (
            (live_price - position["Entry"]) * position["Quantity"]
            if live_price > 0
            else 0.0
        )

        row = dict(position)
        row["Live Price"] = live_price
        row["Unrealized PnL"] = pnl
        rows.append(row)

    return pd.DataFrame(rows)


def calculate_paper_statistics():
    trades = pd.DataFrame(st.session_state.paper_trades)

    if trades.empty:
        return {
            "Total Trades": 0,
            "Winning Trades": 0,
            "Losing Trades": 0,
            "Win Rate": 0.0,
            "Net PnL": 0.0,
            "Average PnL": 0.0,
        }

    winning = int((trades["PnL"] > 0).sum())
    losing = int((trades["PnL"] < 0).sum())
    total = len(trades)

    return {
        "Total Trades": total,
        "Winning Trades": winning,
        "Losing Trades": losing,
        "Win Rate": (winning / total * 100) if total else 0.0,
        "Net PnL": safe_float(trades["PnL"].sum()),
        "Average PnL": safe_float(trades["PnL"].mean()),
    }


def backtest_strategy(
    candles,
    initial_capital=100000.0,
    risk_percent=1.0,
):
    if candles.empty or len(candles) < 40:
        return pd.DataFrame(), {
            "Initial Capital": initial_capital,
            "Final Capital": initial_capital,
            "Net PnL": 0.0,
            "Total Trades": 0,
            "Win Rate": 0.0,
            "Max Drawdown": 0.0,
        }

    frame = candles.copy().reset_index(drop=True)
    capital = float(initial_capital)
    equity_curve = [capital]
    trades = []
    active_trade = None

    for index in range(20, len(frame)):
        row = frame.iloc[index]
        previous = frame.iloc[index - 1]

        close_price = safe_float(row["Close"])
        atr_value = safe_float(row["ATR"])
        rsi_value = safe_float(row["RSI"], 50.0)
        vwap_value = safe_float(row["VWAP"])
        trend_value = safe_int(row["TrendDirection"])

        bullish_signal = (
            trend_value == 1
            and close_price > vwap_value
            and rsi_value >= 55
        )

        bearish_signal = (
            trend_value == -1
            and close_price < vwap_value
            and rsi_value <= 45
        )

        if active_trade is None:
            if not atr_value:
                equity_curve.append(capital)
                continue

            risk_amount = capital * risk_percent / 100

            if bullish_signal:
                stop = close_price - 1.5 * atr_value
                target = close_price + 2.0 * atr_value
                risk_per_unit = close_price - stop
                quantity = max(1, int(risk_amount / max(risk_per_unit, 0.01)))

                active_trade = {
                    "Side": "LONG",
                    "Entry Time": row["Datetime"],
                    "Entry": close_price,
                    "Stop": stop,
                    "Target": target,
                    "Quantity": quantity,
                }

            elif bearish_signal:
                stop = close_price + 1.5 * atr_value
                target = close_price - 2.0 * atr_value
                risk_per_unit = stop - close_price
                quantity = max(1, int(risk_amount / max(risk_per_unit, 0.01)))

                active_trade = {
                    "Side": "SHORT",
                    "Entry Time": row["Datetime"],
                    "Entry": close_price,
                    "Stop": stop,
                    "Target": target,
                    "Quantity": quantity,
                }

        else:
            exit_price = None
            reason = None

            if active_trade["Side"] == "LONG":
                if safe_float(row["Low"]) <= active_trade["Stop"]:
                    exit_price = active_trade["Stop"]
                    reason = "Stop Loss"
                elif safe_float(row["High"]) >= active_trade["Target"]:
                    exit_price = active_trade["Target"]
                    reason = "Target"
                elif bearish_signal:
                    exit_price = close_price
                    reason = "Opposite Signal"

                if exit_price is not None:
                    pnl = (
                        exit_price - active_trade["Entry"]
                    ) * active_trade["Quantity"]

            else:
                if safe_float(row["High"]) >= active_trade["Stop"]:
                    exit_price = active_trade["Stop"]
                    reason = "Stop Loss"
                elif safe_float(row["Low"]) <= active_trade["Target"]:
                    exit_price = active_trade["Target"]
                    reason = "Target"
                elif bullish_signal:
                    exit_price = close_price
                    reason = "Opposite Signal"

                if exit_price is not None:
                    pnl = (
                        active_trade["Entry"] - exit_price
                    ) * active_trade["Quantity"]

            if exit_price is not None:
                capital += pnl

                trades.append(
                    {
                        **active_trade,
                        "Exit Time": row["Datetime"],
                        "Exit": exit_price,
                        "PnL": pnl,
                        "Exit Reason": reason,
                    }
                )

                active_trade = None

        equity_curve.append(capital)

    if active_trade is not None:
        last_row = frame.iloc[-1]
        exit_price = safe_float(last_row["Close"])

        if active_trade["Side"] == "LONG":
            pnl = (
                exit_price - active_trade["Entry"]
            ) * active_trade["Quantity"]
        else:
            pnl = (
                active_trade["Entry"] - exit_price
            ) * active_trade["Quantity"]

        capital += pnl

        trades.append(
            {
                **active_trade,
                "Exit Time": last_row["Datetime"],
                "Exit": exit_price,
                "PnL": pnl,
                "Exit Reason": "End of Data",
            }
        )

    trade_frame = pd.DataFrame(trades)

    equity_series = pd.Series(equity_curve, dtype="float64")
    rolling_peak = equity_series.cummax()
    drawdown = (
        (equity_series - rolling_peak)
        / rolling_peak.replace(0, pd.NA)
        * 100
    )

    winning_trades = (
        int((trade_frame["PnL"] > 0).sum())
        if not trade_frame.empty
        else 0
    )

    total_trades = len(trade_frame)

    summary = {
        "Initial Capital": initial_capital,
        "Final Capital": capital,
        "Net PnL": capital - initial_capital,
        "Total Trades": total_trades,
        "Win Rate": (
            winning_trades / total_trades * 100
            if total_trades
            else 0.0
        ),
        "Max Drawdown": abs(safe_float(drawdown.min(), 0.0)),
    }

    return trade_frame, summary



@st.cache_data(ttl=21600)
def resolve_india_vix_security_id():
    """
    Resolve INDIA VIX from Dhan's official instrument master.

    This avoids hard-coding a Security ID that may differ or change.
    Returns an integer Security ID or None.
    """
    url = "https://images.dhan.co/api-data/api-scrip-master.csv"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        decoded_lines = response.content.decode(
            "utf-8-sig",
            errors="ignore",
        ).splitlines()

        reader = csv.DictReader(decoded_lines)

        for row in reader:
            searchable = " | ".join(
                str(value or "") for value in row.values()
            ).upper()

            if "INDIA VIX" not in searchable:
                continue

            security_key = next(
                (
                    key
                    for key in row.keys()
                    if key
                    and "SECURITY" in key.upper()
                    and "ID" in key.upper()
                ),
                None,
            )

            if not security_key:
                continue

            security_id = safe_int(row.get(security_key), 0)

            if security_id > 0:
                return security_id

    except Exception:
        return None

    return None


def fetch_india_vix():
    """
    Fetch INDIA VIX independently.

    A VIX lookup failure never breaks the main dashboard or index cards.
    """
    if not CREDENTIALS_READY or dhan is None:
        return 0.0, "API not connected"

    security_id = resolve_india_vix_security_id()

    if not security_id:
        return 0.0, "Instrument unavailable"

    try:
        result = dhan.ticker_data({"IDX_I": [security_id]})

        if result.get("status") != "success":
            return 0.0, "Data unavailable"

        market_data = result.get("data", {}).get("data", {})
        segment_data = market_data.get("IDX_I", {})

        row = segment_data.get(
            str(security_id),
            segment_data.get(security_id, {}),
        )

        value = safe_float(row.get("last_price"))

        if value <= 0:
            return 0.0, "Data unavailable"

        if value < 13:
            state = "Low volatility"
        elif value < 20:
            state = "Normal volatility"
        elif value < 30:
            state = "High volatility"
        else:
            state = "Extreme volatility"

        return value, state

    except Exception:
        return 0.0, "Data unavailable"


@st.cache_data(ttl=21600, show_spinner=False)
def load_dhan_instrument_master():
    """Load Dhan's official instrument master for dynamic MCX resolution."""
    url = "https://images.dhan.co/api-data/api-scrip-master.csv"
    try:
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        text = response.content.decode("utf-8-sig", errors="ignore")
        return list(csv.DictReader(text.splitlines()))
    except Exception as error:
        add_api_log(f"Instrument master unavailable: {error}", "WARNING")
        return []


def _row_value(row, *keywords):
    for key, value in row.items():
        normalized = str(key or "").upper().replace("_", " ")
        if all(word.upper() in normalized for word in keywords):
            return value
    return None


@st.cache_data(ttl=21600, show_spinner=False)
def resolve_nearest_mcx_future(symbol):
    """Resolve the nearest non-expired standard MCX future without hard-coded IDs."""
    symbol = str(symbol).upper().strip()
    today = datetime.now(IST).date()
    candidates = []

    for row in load_dhan_instrument_master():
        searchable = " | ".join(str(value or "") for value in row.values()).upper()
        if "MCX" not in searchable or "FUT" not in searchable:
            continue

        trading_symbol = str(
            _row_value(row, "TRADING", "SYMBOL")
            or _row_value(row, "DISPLAY", "NAME")
            or _row_value(row, "SYMBOL")
            or ""
        ).upper().strip()

        # Prefer standard GOLD and CRUDEOIL contracts, not mini variants.
        if not trading_symbol.startswith(symbol):
            continue
        if symbol == "GOLD" and trading_symbol.startswith(("GOLDM", "GOLDTEN", "GOLDPETAL", "GOLDGUINEA")):
            continue
        if symbol == "CRUDEOIL" and trading_symbol.startswith("CRUDEOILM"):
            continue

        security_id = safe_int(_row_value(row, "SECURITY", "ID"), 0)
        if security_id <= 0:
            continue

        expiry_raw = (
            _row_value(row, "EXPIRY", "DATE")
            or _row_value(row, "EXPIRY")
            or ""
        )
        expiry = pd.to_datetime(expiry_raw, errors="coerce", dayfirst=True)
        if pd.isna(expiry):
            continue
        expiry_date = expiry.date()
        if expiry_date < today:
            continue

        exchange_segment = str(
            _row_value(row, "EXCHANGE", "SEGMENT") or "MCX_COMM"
        ).strip() or "MCX_COMM"
        if "MCX" in exchange_segment.upper():
            exchange_segment = "MCX_COMM"

        candidates.append({
            "security_id": security_id,
            "segment": exchange_segment,
            "trading_symbol": trading_symbol,
            "expiry": expiry_date.isoformat(),
        })

    return min(candidates, key=lambda item: item["expiry"]) if candidates else None


def fetch_mcx_future_quote(symbol):
    if not CREDENTIALS_READY:
        return None, "Dhan API not connected"

    contract = resolve_nearest_mcx_future(symbol)
    if not contract:
        return None, "Active MCX contract not resolved"

    parsed, error = direct_marketfeed_ltp(
        {contract["segment"]: [contract["security_id"]]},
        attempts=3,
    )
    row = parsed.get((contract["segment"], str(contract["security_id"])))
    if not row:
        return None, error or "Quote unavailable"

    return {
        "last_price": safe_float(row.get("last_price")),
        "symbol": contract["trading_symbol"],
        "expiry": contract["expiry"],
        "source": "Dhan MCX",
    }, ""


@st.cache_data(ttl=20, show_spinner=False)
def fetch_crypto_inr(coin_id, symbol):
    """Fetch public crypto spot price in INR; no dummy fallback."""
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin_id}&vs_currencies=inr&include_24hr_change=true"
    )
    try:
        response = request_with_retry("GET", url, timeout=12, attempts=2)
        payload = response.json().get(coin_id, {})
        price = safe_float(payload.get("inr"))
        change = safe_float(payload.get("inr_24h_change"))
        if price <= 0:
            return None, f"{symbol}/INR unavailable"
        return {
            "last_price": price,
            "change_24h": change,
            "symbol": f"{symbol}/INR",
            "source": "CoinGecko spot",
            "asset_type": "CRYPTO",
        }, ""
    except Exception as error:
        return None, str(error)


def fetch_cross_market_quotes():
    """Fetch major MCX futures and BTC/ETH spot independently."""
    results = {}
    failures = []

    commodity_map = [
        ("GOLD", "GOLD"),
        ("SILVER", "SILVER"),
        ("CRUDE OIL", "CRUDEOIL"),
        ("NATURAL GAS", "NATURALGAS"),
    ]

    for label, symbol in commodity_map:
        quote, error = fetch_mcx_future_quote(symbol)
        if quote:
            quote["asset_type"] = "COMMODITY"
            quote["root_symbol"] = symbol
            results[label] = quote
        else:
            failures.append(f"{label}: {error}")
        time.sleep(1.05)

    for label, coin_id, symbol in [
        ("BITCOIN", "bitcoin", "BTC"),
        ("ETHEREUM", "ethereum", "ETH"),
    ]:
        quote, error = fetch_crypto_inr(coin_id, symbol)
        if quote:
            results[label] = quote
        else:
            failures.append(f"{label}: {error}")

    return results, failures


def commodity_chain_dataframe(chain_response):
    """Convert a Dhan MCX option-chain response into a compact table."""
    data = chain_response.get("data", {}) if isinstance(chain_response, dict) else {}
    spot = safe_float(data.get("last_price"))
    rows = []
    for strike_text, option_data in (data.get("oc", {}) or {}).items():
        ce = (option_data or {}).get("ce") or {}
        pe = (option_data or {}).get("pe") or {}
        ce_oi = safe_int(ce.get("oi"))
        pe_oi = safe_int(pe.get("oi"))
        rows.append({
            "CE OI": ce_oi,
            "CE Chg OI": ce_oi - safe_int(ce.get("previous_oi")),
            "CE Volume": safe_int(ce.get("volume")),
            "CE IV": safe_float(ce.get("implied_volatility")),
            "CE LTP": safe_float(ce.get("last_price")),
            "Strike": safe_float(strike_text),
            "PE LTP": safe_float(pe.get("last_price")),
            "PE IV": safe_float(pe.get("implied_volatility")),
            "PE Volume": safe_int(pe.get("volume")),
            "PE Chg OI": pe_oi - safe_int(pe.get("previous_oi")),
            "PE OI": pe_oi,
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, spot, 0.0, 0.0, 0.0
    frame = frame.sort_values("Strike").reset_index(drop=True)
    atm = safe_float(frame.loc[(frame["Strike"] - spot).abs().idxmin(), "Strike"])
    resistance = safe_float(frame.loc[frame["CE OI"].idxmax(), "Strike"])
    support = safe_float(frame.loc[frame["PE OI"].idxmax(), "Strike"])
    return frame, spot, atm, resistance, support


# =========================================================
# HEADER AND SIDEBAR
# =========================================================

vix_value, vix_state = fetch_india_vix()
vix_display = f"{vix_value:.2f}" if vix_value > 0 else "N/A"

st.markdown(
    f"""
    <div class="terminal-header">
        <div class="terminal-header-left">
            <div class="terminal-header-title">
                Shankar Trading Dashboard
            </div>
            <div class="terminal-header-subtitle">
                NSE • BSE • NIFTY • BANK NIFTY • Option Chain • OI • PCR • Max Pain •
                Pivot Points • SMC • Paper Trading • Backtesting
            </div>
        </div>
        <div class="vix-badge">
            <div class="vix-label">INDIA VIX</div>
            <div class="vix-value">{vix_display}</div>
            <div class="vix-state">{vix_state}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

is_market_open, now_ist, market_note = market_status()

st.markdown(
    f'<div class="{"status-open" if is_market_open else "status-closed"}">'
    f'{market_note} IST time: {now_ist.strftime("%d-%m-%Y %I:%M:%S %p")}'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="terminal-strip">
        <div class="terminal-pill">5m Entry Engine</div>
        <div class="terminal-pill">15m Trend Confirmation</div>
        <div class="terminal-pill">5m + 15m + 60m Confirmation</div>
        <div class="terminal-pill">OI + PCR + Max Pain</div>
        <div class="terminal-pill">Options SMC + FVG + Liquidity</div>
        <div class="terminal-pill">Options Paper Trading + Backtest</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Dashboard Controls")

    auto_refresh = st.toggle(
        "Auto refresh every 10 seconds",
        value=False,
    )

    sound_alert = st.toggle(
        "Sound on new CE/PE signal",
        value=True,
    )

    show_api_debug = st.toggle(
        "Show hidden API logger",
        value=False,
        help="Displays recent API attempts and parser messages.",
    )

    st.info(
        "The terminal automatically uses 5-minute candles for entries and "
        "15-minute candles for trend confirmation."
    )

    chart_interval = "5"

    st.divider()

    st.subheader("💰 Risk Calculator")

    trading_capital = st.number_input(
        "Trading capital (₹)",
        min_value=1000.0,
        value=15000.0,
        step=1000.0,
    )

    risk_percent = st.number_input(
        "Risk per trade (%)",
        min_value=0.25,
        max_value=5.0,
        value=1.0,
        step=0.25,
    )

    lot_size = st.number_input(
        "Current lot size",
        min_value=1,
        value=75,
        step=1,
        help="Enter the current exchange lot size manually.",
    )

    st.caption(
        "Lot sizes and exchange rules can change. Keep this value updated."
    )

    st.divider()

    st.subheader("🧪 Paper Trading")

    paper_starting_balance = st.number_input(
        "Paper account balance (₹)",
        min_value=10000.0,
        value=float(st.session_state.paper_balance),
        step=10000.0,
    )

    if st.button("Reset Paper Account"):
        st.session_state.paper_balance = paper_starting_balance
        st.session_state.paper_positions = []
        st.session_state.paper_trades = []
        st.success("Paper account reset.")

    st.divider()

    if st.button("Clear signal history"):
        st.session_state.signal_log = []
        st.success("Signal history cleared.")

if not CREDENTIALS_READY:
    st.error(
        "Dhan Client ID and Access Token are missing. "
        "Set DHAN_CLIENT_ID and DHAN_ACCESS_TOKEN in environment variables "
        "or .streamlit/secrets.toml, then restart the app."
    )
    st.stop()

connection_columns = st.columns(4)

connection_columns[0].metric(
    "API Connection",
    "Ready" if CREDENTIALS_READY else "Missing credentials",
)
connection_columns[1].metric(
    "INDIA VIX",
    vix_display,
)
connection_columns[2].metric(
    "VIX Status",
    vix_state,
)
connection_columns[3].metric(
    "Market Status",
    professional_market_status()[3],
)

if st.button("🔄 Refresh Dashboard", width="stretch"):
    st.rerun()


# =========================================================
# LIVE MARKET DATA
# =========================================================

with st.spinner("Loading live index prices..."):
    live_quotes, live_failures = fetch_professional_index_quotes()

if live_quotes:
    st.session_state.last_market_quotes = live_quotes

    st.success(
        f"✅ {len(live_quotes)} live index prices connected"
    )
    st.subheader("📡 Live Index Monitor")

    live_cards = []

    for instrument_name in [
        "NIFTY 50",
        "BANK NIFTY",
        "FIN NIFTY",
        "MIDCAP NIFTY",
        "SENSEX",
        "BANKEX",
    ]:
        quote = live_quotes.get(instrument_name)

        if not quote:
            continue

        last_price = safe_float(quote.get("last_price"))

        live_cards.append(
            f"""
            <div class="live-card index-card">
                <div class="live-card-title">{instrument_name}</div>
                <div class="live-card-value">₹ {last_price:,.2f}</div>
            </div>
            """
        )

    render_html(
        '<div class="live-grid">' + "".join(live_cards) + "</div>"
    )

else:
    previous_quotes = st.session_state.get(
        "last_market_quotes",
        {},
    )

    if previous_quotes:
        st.warning(
            "Live index refresh is temporarily unavailable. "
            "The last successfully received values are retained."
        )

        live_cards = []

        for instrument_name, quote in previous_quotes.items():
            last_price = safe_float(quote.get("last_price"))

            live_cards.append(
                f"""
                <div class="live-card">
                    <div class="live-card-title">
                        {instrument_name} • Last received
                    </div>
                    <div class="live-card-value">
                        ₹ {last_price:,.2f}
                    </div>
                </div>
                """
            )

        render_html(
            '<div class="live-grid">' + "".join(live_cards) + "</div>"
        )

    else:
        st.warning(
            "Live index feed is temporarily unavailable. "
            "No dummy prices are being displayed. "
            "Option analysis can still be loaded separately."
        )

if live_failures:
    add_api_log(
        "Partial index-feed failures: "
        + " | ".join(live_failures),
        "WARNING",
    )

# Commodity & Crypto section moved to a separate dashboard.

status_columns = st.columns(4)

status_columns[0].metric(
    "Dhan API",
    "Connected" if CREDENTIALS_READY else "Disconnected",
)
status_columns[1].metric(
    "INDIA VIX",
    f"{vix_value:.2f}" if vix_value > 0 else "N/A",
)
status_columns[2].metric(
    "Volatility State",
    vix_state,
)
status_columns[3].metric(
    "Market",
    professional_market_status()[3],
)

if show_api_debug:
    with st.expander("🛠 Hidden API Logger", expanded=False):
        logs = pd.DataFrame(st.session_state.get("api_logs", []))

        if logs.empty:
            st.info("No API log entries yet.")
        else:
            st.dataframe(
                logs.iloc[::-1],
                width="stretch",
                hide_index=True,
            )



st.subheader("📅 Market Holidays & Trading Days")
render_market_calendar(now_ist.date())

st.divider()


# =========================================================
# INDEX AND EXPIRY
# =========================================================

st.subheader("📈 Full Option & Technical Analysis")

index_choice = st.selectbox(
    "Select Index",
    [
        "NIFTY 50",
        "BANK NIFTY",
        "FIN NIFTY",
        "MIDCAP NIFTY",
        "SENSEX",
        "BANKEX",
    ],
)

index_details = {
    "NIFTY 50": {
        "security_id": 13,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 10,
    },
    "BANK NIFTY": {
        "security_id": 25,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 25,
    },
    "FIN NIFTY": {
        "security_id": 27,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 10,
    },
    "MIDCAP NIFTY": {
        "security_id": 442,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 10,
    },
    "SENSEX": {
        "security_id": 51,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 25,
    },
    "BANKEX": {
        "security_id": 69,
        "segment": "IDX_I",
        "instrument": "INDEX",
        "alert_buffer": 25,
    },
}

selected_index = index_details[index_choice]

try:
    expiry_response = get_expiry_list(
        selected_index["security_id"],
        selected_index["segment"],
        CLIENT_ID,
        ACCESS_TOKEN,
    )

    if expiry_response.get("status") != "success":
        st.error(
            "Expiry API failed. Check your Data API subscription and token. "
            f"Details: {format_api_error(expiry_response)}"
        )
        st.stop()

    expiry_dates = expiry_response.get("data", [])

except Exception as error:
    st.error(
        "Could not load expiry dates. "
        "Check token, internet, and Data API subscription. "
        f"Details: {error}"
    )
    st.stop()

if not expiry_dates:
    st.warning("No active expiry dates received.")
    st.stop()

selected_expiry = st.selectbox(
    "Select Expiry",
    expiry_dates,
)

if st.button(
    "📊 Load Full Dashboard Analysis",
    width="stretch",
):
    st.session_state.load_chain = True


# =========================================================
# MAIN ANALYSIS
# =========================================================

if st.session_state.load_chain:
    try:
        with st.spinner("Loading option chain and technical indicators..."):
            chain_response = get_option_chain(
                selected_index["security_id"],
                selected_index["segment"],
                selected_expiry,
            )

            candle_response_5m = get_intraday_candles(
                selected_index["security_id"],
                selected_index["segment"],
                selected_index["instrument"],
                "5",
                CLIENT_ID,
                ACCESS_TOKEN,
            )

            candle_response_15m = get_intraday_candles(
                selected_index["security_id"],
                selected_index["segment"],
                selected_index["instrument"],
                "15",
                CLIENT_ID,
                ACCESS_TOKEN,
            )

            candle_response_60m = get_intraday_candles(
                selected_index["security_id"],
                selected_index["segment"],
                selected_index["instrument"],
                "60",
                CLIENT_ID,
                ACCESS_TOKEN,
            )

        if chain_response.get("status") != "success":
            st.error(
                "Option-chain API returned an error. "
                f"Details: {format_api_error(chain_response)}"
            )
            st.stop()

        chain_data = chain_response.get("data", {})
        spot_price = safe_float(chain_data.get("last_price"))
        option_chain = chain_data.get("oc", {})

        rows = []

        for strike_text, option_data in option_chain.items():
            strike = safe_float(strike_text)
            ce = option_data.get("ce") or {}
            pe = option_data.get("pe") or {}

            ce_greeks = ce.get("greeks") or {}
            pe_greeks = pe.get("greeks") or {}

            ce_oi = safe_int(ce.get("oi"))
            pe_oi = safe_int(pe.get("oi"))

            ce_previous_oi = safe_int(ce.get("previous_oi"))
            pe_previous_oi = safe_int(pe.get("previous_oi"))

            rows.append(
                {
                    "CE OI": ce_oi,
                    "CE Chg OI": ce_oi - ce_previous_oi,
                    "CE Volume": safe_int(ce.get("volume")),
                    "CE IV": safe_float(ce.get("implied_volatility")),
                    "CE Delta": safe_float(ce_greeks.get("delta")),
                    "CE Gamma": safe_float(ce_greeks.get("gamma")),
                    "CE Theta": safe_float(ce_greeks.get("theta")),
                    "CE Vega": safe_float(ce_greeks.get("vega")),
                    "CE LTP": safe_float(ce.get("last_price")),
                    "Strike": strike,
                    "PE LTP": safe_float(pe.get("last_price")),
                    "PE Delta": safe_float(pe_greeks.get("delta")),
                    "PE Gamma": safe_float(pe_greeks.get("gamma")),
                    "PE Theta": safe_float(pe_greeks.get("theta")),
                    "PE Vega": safe_float(pe_greeks.get("vega")),
                    "PE IV": safe_float(pe.get("implied_volatility")),
                    "PE Volume": safe_int(pe.get("volume")),
                    "PE Chg OI": pe_oi - pe_previous_oi,
                    "PE OI": pe_oi,
                }
            )

        dataframe = pd.DataFrame(rows)

        if dataframe.empty:
            st.warning("No option-chain data received.")
            st.stop()

        dataframe = dataframe.sort_values("Strike")
        dataframe["ATM Distance"] = (
            dataframe["Strike"] - spot_price
        ).abs()

        atm_index = dataframe["ATM Distance"].idxmin()
        atm_row = dataframe.loc[atm_index]
        atm_strike = safe_float(atm_row["Strike"])

        atm_ce_change = safe_float(atm_row["CE Chg OI"])
        atm_pe_change = safe_float(atm_row["PE Chg OI"])

        # Intraday OI structure: resistance must be ABOVE ATM and support BELOW ATM.
        # Use nearby strikes only, so far-away legacy OI does not create misleading levels.
        strike_values = dataframe["Strike"].dropna().sort_values().unique()
        strike_step = 50.0
        if len(strike_values) >= 2:
            differences = pd.Series(strike_values).diff().dropna()
            positive_differences = differences[differences > 0]
            if not positive_differences.empty:
                strike_step = safe_float(positive_differences.median(), 50.0)

        structure_window = max(strike_step * 12, 600.0)
        nearby_structure = dataframe[
            (dataframe["Strike"] >= atm_strike - structure_window)
            & (dataframe["Strike"] <= atm_strike + structure_window)
        ].copy()

        resistance_candidates = nearby_structure[nearby_structure["Strike"] > atm_strike]
        support_candidates = nearby_structure[nearby_structure["Strike"] < atm_strike]

        if resistance_candidates.empty:
            resistance_candidates = dataframe[dataframe["Strike"] > atm_strike]
        if support_candidates.empty:
            support_candidates = dataframe[dataframe["Strike"] < atm_strike]

        resistance_ranked = resistance_candidates.nlargest(2, "CE OI")
        support_ranked = support_candidates.nlargest(2, "PE OI")

        resistance = (
            safe_float(resistance_ranked.iloc[0]["Strike"])
            if not resistance_ranked.empty
            else atm_strike
        )
        resistance_2 = (
            safe_float(resistance_ranked.iloc[1]["Strike"])
            if len(resistance_ranked) > 1
            else 0.0
        )
        support = (
            safe_float(support_ranked.iloc[0]["Strike"])
            if not support_ranked.empty
            else atm_strike
        )
        support_2 = (
            safe_float(support_ranked.iloc[1]["Strike"])
            if len(support_ranked) > 1
            else 0.0
        )

        nearest_base = dataframe.nsmallest(21, "ATM Distance")
        important_rows = dataframe[
            dataframe["Strike"].apply(
                lambda value: any(
                    math.isclose(safe_float(value), level, rel_tol=0, abs_tol=0.001)
                    for level in [atm_strike, resistance, resistance_2, support, support_2]
                )
            )
        ]
        nearest_rows = (
            pd.concat([nearest_base, important_rows], ignore_index=True)
            .drop_duplicates(subset=["Strike"])
            .sort_values("Strike")
            .drop(columns=["ATM Distance"])
        )

        total_ce_oi = dataframe["CE OI"].sum()
        total_pe_oi = dataframe["PE OI"].sum()
        total_ce_change = dataframe["CE Chg OI"].sum()
        total_pe_change = dataframe["PE Chg OI"].sum()

        pcr = total_pe_oi / total_ce_oi if total_ce_oi else 0

        max_pain = calculate_max_pain(dataframe)

        candles_5m = enrich_candles(
            candles_to_dataframe(candle_response_5m)
        )

        candles_15m = enrich_candles(
            candles_to_dataframe(candle_response_15m)
        )

        candles_60m = enrich_candles(
            candles_to_dataframe(candle_response_60m)
        )

        candles = candles_5m
        previous_day_pivots = calculate_previous_day_pivots(candles_5m)

        latest_rsi = 50.0
        latest_vwap = 0.0
        latest_atr = 0.0
        trend_direction = 0
        latest_supertrend = 0.0

        if not candles.empty:
            latest = candles.iloc[-1]
            latest_rsi = safe_float(latest["RSI"], 50.0)
            latest_vwap = safe_float(latest["VWAP"])
            latest_atr = safe_float(latest["ATR"])
            trend_direction = safe_int(latest["TrendDirection"])
            latest_supertrend = safe_float(latest["Supertrend"], 0.0)

            if not latest_supertrend and latest_atr:
                latest_close = safe_float(latest["Close"], spot_price)

                if trend_direction == 1:
                    latest_supertrend = latest_close - 3 * latest_atr
                elif trend_direction == -1:
                    latest_supertrend = latest_close + 3 * latest_atr

        snapshot_5m = timeframe_snapshot(candles_5m)
        snapshot_15m = timeframe_snapshot(candles_15m)
        snapshot_60m = timeframe_snapshot(candles_60m)
        mtf_result = mtf_confirmation(snapshot_5m, snapshot_15m)

        (
            mtf_agreement,
            mtf_direction_5m,
            mtf_direction_15m,
        ) = calculate_mtf_agreement(
            snapshot_5m,
            snapshot_15m,
        )

        order_blocks = detect_order_blocks(candles)
        fair_value_gaps = detect_fair_value_gaps(candles)
        buy_liquidity, sell_liquidity = detect_liquidity_levels(candles)
        institutional_activity, volume_ratio = detect_institutional_activity(
            candles
        )
        smc_market_bias, smc_strength, smc_reasons = smc_bias(
            spot_price,
            order_blocks,
            fair_value_gaps,
            buy_liquidity,
            sell_liquidity,
        )

        (
            oi_summary,
            oi_bias,
            oi_notes,
        ) = analyse_oi_build_up(
            total_ce_change,
            total_pe_change,
            atm_ce_change,
            atm_pe_change,
        )

        (
            recommendation,
            sentiment,
            signal_class,
            quality_score,
            reasons,
            bullish_points,
            bearish_points,
        ) = build_signal_and_score(
            pcr,
            total_ce_change,
            total_pe_change,
            atm_ce_change,
            atm_pe_change,
            spot_price,
            support,
            resistance,
            max_pain,
            latest_rsi,
            latest_vwap,
            trend_direction,
        )

        (
            recommendation,
            quality_score,
            mtf_filter_notes,
        ) = refine_recommendation_with_mtf(
            recommendation,
            quality_score,
            mtf_result,
            snapshot_5m,
            snapshot_15m,
        )

        if recommendation == "BUY CE BIAS":
            sentiment = "Bullish"
            signal_class = "signal-bullish"
        elif recommendation == "BUY PE BIAS":
            sentiment = "Bearish"
            signal_class = "signal-bearish"
        else:
            sentiment = "Sideways"
            signal_class = "signal-neutral"

        reasons.extend(mtf_filter_notes)

        ai_confidence = calculate_ai_confidence(
            quality_score,
            mtf_agreement,
            mtf_direction_5m,
            mtf_direction_15m,
            mtf_result["Points"],
        )

        final_ai_recommendation = final_mtf_recommendation(
            recommendation,
            mtf_direction_5m,
            mtf_direction_15m,
            mtf_agreement,
            ai_confidence,
        )

        professional_grade = build_three_timeframe_grade(
            snapshot_5m,
            snapshot_15m,
            snapshot_60m,
            mtf_agreement,
            ai_confidence,
        )

        directional_plan = directional_bias_plan(
            snapshot_5m,
            snapshot_15m,
            snapshot_60m,
            spot_price,
            support,
            resistance,
            atm_strike,
        )

        final_ai_recommendation = professional_grade["Grade"]
        ai_confidence = professional_grade["Score"]

        if final_ai_recommendation == "BUY CE":
            recommendation = "BUY CE BIAS"
            sentiment = "Bullish"
            signal_class = "signal-bullish"
            quality_score = ai_confidence
        elif final_ai_recommendation == "BUY PE":
            recommendation = "BUY PE BIAS"
            sentiment = "Bearish"
            signal_class = "signal-bearish"
            quality_score = ai_confidence
        else:
            recommendation = "WAIT / NO TRADE"
            sentiment = "Sideways"
            signal_class = "signal-neutral"
            quality_score = ai_confidence

        if professional_grade["Direction"] == "BUY CE":
            recommendation = "BUY CE BIAS"
            sentiment = "Bullish"
            signal_class = "signal-bullish"
        elif professional_grade["Direction"] == "BUY PE":
            recommendation = "BUY PE BIAS"
            sentiment = "Bearish"
            signal_class = "signal-bearish"
        else:
            recommendation = "WAIT / NO TRADE"
            sentiment = "Sideways"
            signal_class = "signal-neutral"

        quality_score = ai_confidence

        (
            alert_title,
            alert_class,
            alert_note,
            breakout_level,
            breakdown_level,
        ) = breakout_breakdown_status(
            spot_price,
            support,
            resistance,
            selected_index["alert_buffer"],
        )

        # =====================================================
        # V22 UNIFIED FINAL DECISION ENGINE
        # One actionable output only: BUY CE / BUY PE / WAIT.
        # Trend bias may remain visible, but it cannot become an entry
        # until price-action trigger and non-opposing SMC agree.
        # =====================================================
        mtf_direction = professional_grade.get("Direction", "WAIT")
        smc_bullish = "Bullish" in smc_market_bias
        smc_bearish = "Bearish" in smc_market_bias
        ce_trigger_confirmed = alert_title == "BREAKOUT CONFIRMED"
        pe_trigger_confirmed = alert_title == "BREAKDOWN CONFIRMED"
        vix_risk_high = vix_value >= 22 if vix_value > 0 else False

        # V31 confidence policy (single source of truth):
        # 80-100 = BUY CE / BUY PE, 70-79 = WAIT FOR CONFIRMATION,
        # 0-69 = NO TRADE. Every lower panel must follow this result.
        if ai_confidence >= 80 and mtf_direction == "BUY CE":
            unified_action = "BUY CE"
            unified_grade = "BUY CE — HIGH CONFIDENCE"
            unified_reason = (
                "Confidence is 80% or above and the multi-timeframe direction is bullish. "
                f"Use ₹{breakout_level:,.0f} as the entry trigger and avoid chasing before confirmation."
            )
            unified_class = "grade-strong-buy"
            unified_banner_class = "final-one-buy-ce"
        elif ai_confidence >= 80 and mtf_direction == "BUY PE":
            unified_action = "BUY PE"
            unified_grade = "BUY PE — HIGH CONFIDENCE"
            unified_reason = (
                "Confidence is 80% or above and the multi-timeframe direction is bearish. "
                f"Use ₹{breakdown_level:,.0f} as the entry trigger and avoid chasing before confirmation."
            )
            unified_class = "grade-avoid"
            unified_banner_class = "final-one-buy-pe"
        elif 70 <= ai_confidence <= 79:
            unified_action = "WAIT"
            unified_grade = "WAIT FOR CONFIRMATION"
            if mtf_direction == "BUY CE":
                unified_reason = f"Bullish bias is present, but confidence is below 80%. Watch breakout above ₹{breakout_level:,.0f}."
            elif mtf_direction == "BUY PE":
                unified_reason = f"Bearish bias is present, but confidence is below 80%. Watch breakdown below ₹{breakdown_level:,.0f}."
            else:
                unified_reason = "Confidence is 70–79%, but the 5m, 15m and 60m directions are not aligned."
            unified_class = "grade-wait"
            unified_banner_class = "final-one-wait"
        else:
            unified_action = "NO TRADE"
            unified_grade = "NO TRADE — CAPITAL PROTECTION"
            unified_reason = "Confidence is 69% or below. No CE or PE trade is allowed."
            unified_class = "grade-avoid"
            unified_banner_class = "final-one-buy-pe"

        professional_grade = {
            **professional_grade,
            "Grade": unified_grade,
            "Class": unified_class,
            "Direction": unified_action if unified_action in {"BUY CE", "BUY PE"} else "WAIT",
            "Reason": unified_reason,
        }
        final_ai_recommendation = unified_action
        recommendation = (
            "BUY CE BIAS" if unified_action == "BUY CE"
            else "BUY PE BIAS" if unified_action == "BUY PE"
            else "WAIT / NO TRADE"
        )
        sentiment = "Bullish" if unified_action == "BUY CE" else "Bearish" if unified_action == "BUY PE" else "Sideways"
        signal_class = "signal-bullish" if unified_action == "BUY CE" else "signal-bearish" if unified_action == "BUY PE" else "signal-neutral"

        # Force every downstream panel to use the same final decision.
        if unified_action == "BUY CE":
            directional_plan = {
                **directional_plan,
                "Bias": "BULLISH",
                "OptionSide": "CE",
                "RecommendedStrike": float(atm_strike),
                "Trigger": float(breakout_level),
                "Invalidation": float(support),
            }
        elif unified_action == "BUY PE":
            directional_plan = {
                **directional_plan,
                "Bias": "BEARISH",
                "OptionSide": "PE",
                "RecommendedStrike": float(atm_strike),
                "Trigger": float(breakdown_level),
                "Invalidation": float(resistance),
            }
        else:
            directional_plan = {
                **directional_plan,
                "Bias": unified_grade,
                "OptionSide": unified_action,
                "RecommendedStrike": 0.0,
                "Trigger": 0.0,
                "Invalidation": 0.0,
            }

        if unified_action in {"BUY CE", "BUY PE"}:
            option_type, option_strike, option_premium = select_option_contract(
                dataframe,
                recommendation,
                atm_strike,
            )
            (
                premium_entry,
                premium_stop,
                premium_target1,
                premium_target2,
                premium_target3,
            ) = calculate_option_premium_levels(
                option_premium,
                recommendation,
                latest_atr,
            )
            pro_option_plan = refined_option_plan(
                professional_grade["Direction"],
                option_type,
                premium_entry,
                premium_stop,
                premium_target1,
                premium_target2,
                premium_target3,
            )
        else:
            option_type = ""
            option_strike = 0.0
            option_premium = 0.0
            premium_entry = premium_stop = 0.0
            premium_target1 = premium_target2 = premium_target3 = 0.0
            pro_option_plan = {
                "Action": unified_action,
                "RiskReward": "N/A",
            }

        add_signal_to_log(
            index_choice,
            selected_expiry,
            recommendation,
            option_strike,
            option_type,
            premium_entry,
            premium_stop,
            premium_target1,
            quality_score,
        )

        st.success(f"✅ {index_choice} full analysis loaded")

        # ---------------- SUMMARY METRICS ----------------

        summary1 = st.columns(6)

        summary1[0].metric("Spot", f"₹ {spot_price:,.2f}")
        summary1[1].metric("ATM", f"₹ {atm_strike:,.0f}")
        summary1[2].metric("PCR", f"{pcr:.2f}")
        summary1[3].metric("Max Pain", f"₹ {max_pain:,.0f}")
        summary1[4].metric("Support S1", f"₹ {support:,.0f}")
        summary1[5].metric("Resistance R1", f"₹ {resistance:,.0f}")

        structure_cols = st.columns(4)
        structure_cols[0].metric("Support S1", f"₹ {support:,.0f}")
        structure_cols[1].metric("Support S2", f"₹ {support_2:,.0f}" if support_2 else "N/A")
        structure_cols[2].metric("Resistance R1", f"₹ {resistance:,.0f}")
        structure_cols[3].metric("Resistance R2", f"₹ {resistance_2:,.0f}" if resistance_2 else "N/A")

        summary2 = st.columns(6)

        summary2[0].metric("RSI", f"{latest_rsi:.1f}")
        summary2[1].metric("VWAP", f"₹ {latest_vwap:,.2f}")
        summary2[2].metric(
            "Supertrend",
            "Bullish" if trend_direction == 1 else (
                "Bearish" if trend_direction == -1 else "Unavailable"
            ),
        )
        summary2[3].metric(
            "Supertrend Level",
            f"₹ {latest_supertrend:,.2f}" if latest_supertrend else "N/A",
        )
        summary2[4].metric("ATR", f"{latest_atr:.2f}")
        summary2[5].metric("Trade Quality", f"{quality_score}/100")

        freshness_columns = st.columns(3)

        freshness_columns[0].metric(
            "Data Time",
            (
                candles["Datetime"].iloc[-1].strftime("%I:%M:%S %p")
                if not candles.empty
                else "Unavailable"
            ),
        )
        freshness_columns[1].metric(
            "Selected Interval",
            f"{chart_interval} minute",
        )
        freshness_columns[2].metric(
            "API Status",
            "Connected",
        )

        render_pivot_dashboard(previous_day_pivots)

        # ---------------- PROFESSIONAL AI CONFIRMATION ----------------

        st.subheader("🎯 Final Options Decision")

        final_decision_columns = st.columns(6)

        final_decision_columns[0].metric(
            "Decision",
            professional_grade["Grade"],
        )
        final_decision_columns[1].metric(
            "Confidence",
            f"{ai_confidence}%",
        )
        final_decision_columns[2].metric(
            "Preferred Option",
            directional_plan["OptionSide"],
        )
        final_decision_columns[3].metric(
            "Strike",
            (
                f"{directional_plan['RecommendedStrike']:.0f} "
                f"{directional_plan['OptionSide']}"
                if directional_plan["OptionSide"] in {"CE", "PE"}
                else "No Trade"
            ),
        )
        final_decision_columns[4].metric(
            "Entry Trigger",
            (
                f"₹ {directional_plan['Trigger']:,.2f}"
                if directional_plan["Trigger"]
                else "Wait"
            ),
        )
        final_decision_columns[5].metric(
            "Invalidation",
            (
                f"₹ {directional_plan['Invalidation']:,.2f}"
                if directional_plan["Invalidation"]
                else "N/A"
            ),
        )

        st.markdown(
            f'<div class="final-one-banner {unified_banner_class}">'
            f'{unified_action} — {professional_grade["Grade"]} — {ai_confidence}/100'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="professional-note">'
            f'{professional_grade["Reason"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.subheader("📊 Professional Multi-Timeframe Confirmation")

        def render_full_mtf_panel(tf_label, snapshot, css_class):
            direction = mtf_trade_direction(snapshot)
            supertrend_text = (
                "Bullish" if snapshot["Trend"] == 1
                else "Bearish" if snapshot["Trend"] == -1
                else "N/A"
            )
            vwap_text = f'₹ {snapshot["VWAP"]:,.2f}' if snapshot["VWAP"] else "N/A"
            html = (
                f'<div class="mtf-full-panel {css_class}">'
                f'<div class="mtf-full-title">📊 {tf_label} ANALYSIS</div>'
                '<div class="mtf-full-grid">'
                f'<div class="mtf-full-item"><div class="mtf-full-label">Trend</div><div class="mtf-full-value">{direction}</div></div>'
                f'<div class="mtf-full-item"><div class="mtf-full-label">RSI</div><div class="mtf-full-value">{snapshot["RSI"]:.1f}</div></div>'
                f'<div class="mtf-full-item"><div class="mtf-full-label">VWAP</div><div class="mtf-full-value">{vwap_text}</div></div>'
                f'<div class="mtf-full-item"><div class="mtf-full-label">Supertrend</div><div class="mtf-full-value">{supertrend_text}</div></div>'
                '</div></div>'
            )
            render_html(html)

        render_full_mtf_panel("5 MINUTE", snapshot_5m, "mtf-5m")
        render_full_mtf_panel("15 MINUTE", snapshot_15m, "mtf-15m")
        render_full_mtf_panel("60 MINUTE", snapshot_60m, "mtf-60m")

        mtf_summary = st.columns(4)
        mtf_summary[0].metric("5m vs 15m Agreement", f"{mtf_agreement}%")
        mtf_summary[1].metric("AI Confidence", f"{ai_confidence}%")
        mtf_summary[2].metric("MTF Score", f"{mtf_result['Points']}")
        mtf_summary[3].metric("Final Grade", professional_grade["Grade"])

        # ---------------- FINAL SIGNAL ----------------


        st.write("**Signal reasons:** " + " | ".join(reasons))


        st.subheader("🧠 AI-Style SMC Decision Panel")

        ai_columns = st.columns(5)

        ai_columns[0].metric("Final Recommendation", unified_action)
        ai_columns[1].metric("SMC Bias", smc_market_bias)
        ai_columns[2].metric(
            "Institutional Activity",
            institutional_activity,
        )
        ai_columns[3].metric(
            "Volume Ratio",
            f"{volume_ratio:.2f}x",
        )
        ai_columns[4].metric(
            "SMC Strength",
            f"{smc_strength}/5",
        )

        st.caption(
            "AI-style means a multi-factor rule engine; it is not a trained "
            "machine-learning model. SMC detections are heuristic."
        )
        st.write("**SMC reasons:** " + " | ".join(smc_reasons))

        status_css = (
            "alert-breakout" if unified_action == "BUY CE"
            else "alert-breakdown" if unified_action == "BUY PE"
            else "alert-range"
        )
        st.markdown(
            f'<div class="{status_css}"><strong>{unified_grade}</strong>: {unified_reason}</div>',
            unsafe_allow_html=True,
        )

        if (
            sound_alert
            and unified_action in {"BUY CE", "BUY PE"}
            and recommendation != st.session_state.last_signal
        ):
            play_signal_sound()

        st.session_state.last_signal = recommendation

        # ---------------- EXACT OPTION PLAN ----------------

        st.subheader("🧭 Options Direction & Entry Trigger")

        bias_columns = st.columns(6)

        bias_columns[0].metric(
            "Market Bias",
            directional_plan["Bias"],
        )
        bias_columns[1].metric(
            "Preferred Option",
            directional_plan["OptionSide"],
        )
        bias_columns[2].metric(
            "Recommended Strike",
            (
                f"{directional_plan['RecommendedStrike']:.0f} "
                f"{directional_plan['OptionSide']}"
                if directional_plan["OptionSide"] in {"CE", "PE"}
                else "No Trade"
            ),
        )
        bias_columns[3].metric(
            "Entry Trigger",
            (
                f"₹ {directional_plan['Trigger']:,.2f}"
                if directional_plan["Trigger"]
                else "Wait"
            ),
        )
        bias_columns[4].metric(
            "Invalidation",
            (
                f"₹ {directional_plan['Invalidation']:,.2f}"
                if directional_plan["Invalidation"]
                else "N/A"
            ),
        )
        bias_columns[5].metric(
            "Bias Weight",
            (
                f"Bull {directional_plan['BullishWeight']} / "
                f"Bear {directional_plan['BearishWeight']}"
            ),
        )

        st.caption(
            "V31 policy: 80–100% = BUY, 70–79% = WAIT FOR CONFIRMATION, "
            "0–69% = NO TRADE. All panels use this same final decision."
        )

        st.subheader("🎯 Exact Option Trade Reference")

        plan = st.columns(6)

        plan[0].metric(
            "Action",
            pro_option_plan["Action"],
        )
        plan[1].metric(
            "Option",
            (
                f"{option_strike:.0f} {option_type}"
                if unified_action in {"BUY CE", "BUY PE"}
                else "No Trade"
            ),
        )
        plan[2].metric(
            "Premium Entry",
            f"₹ {premium_entry:,.2f}" if premium_entry else "Wait",
        )
        plan[3].metric(
            "Premium Stop",
            f"₹ {premium_stop:,.2f}" if premium_stop else "Wait",
        )
        plan[4].metric(
            "Target 1",
            f"₹ {premium_target1:,.2f}" if premium_target1 else "Wait",
        )
        plan[5].metric(
            "Target 2 / 3",
            (
                f"₹ {premium_target2:,.2f} / ₹ {premium_target3:,.2f}"
                if premium_target2
                else "Wait"
            ),
        )

        st.caption(
            "Premium levels are references derived from current premium and "
            "ATR context. Verify liquidity and price action before trading."
        )

        rr_columns = st.columns(3)

        rr_columns[0].metric(
            "Risk:Reward",
            pro_option_plan["RiskReward"],
        )
        rr_columns[1].metric(
            "Setup Quality",
            professional_grade["Grade"],
        )
        rr_columns[2].metric(
            "Higher-Timeframe Filter",
            mtf_trade_direction(snapshot_60m),
        )

        # ---------------- RISK CALCULATOR ----------------

        st.subheader("🛡️ Position Size & Risk")

        maximum_risk = trading_capital * risk_percent / 100
        premium_risk_per_unit = max(
            premium_entry - premium_stop,
            0,
        )

        risk_per_lot = premium_risk_per_unit * lot_size

        allowed_lots = (
            math.floor(maximum_risk / risk_per_lot)
            if risk_per_lot > 0
            else 0
        )

        required_capital_one_lot = premium_entry * lot_size

        risk_columns = st.columns(6)

        risk_columns[0].metric(
            "Max Risk",
            f"₹ {maximum_risk:,.2f}",
        )
        risk_columns[1].metric(
            "Risk / Unit",
            f"₹ {premium_risk_per_unit:,.2f}",
        )
        risk_columns[2].metric(
            "Risk / Lot",
            f"₹ {risk_per_lot:,.2f}",
        )
        risk_columns[3].metric(
            "Allowed Lots",
            str(allowed_lots),
        )
        risk_columns[4].metric(
            "Quantity",
            str(allowed_lots * lot_size),
        )
        risk_columns[5].metric(
            "Approx. Premium Capital / Lot",
            f"₹ {required_capital_one_lot:,.2f}",
        )

        if option_type != "WAIT" and allowed_lots == 0:
            st.warning(
                "Your selected risk limit does not allow even one full lot "
                "at the displayed stop-loss distance."
            )

        # ---------------- PAPER TRADING ----------------

        st.subheader("🧪 One-Click Paper Trading")

        for auto_message in auto_manage_paper_positions(dataframe):
            st.info(auto_message)

        paper_columns = st.columns(4)

        paper_quantity = paper_columns[0].number_input(
            "Paper Quantity",
            min_value=1,
            value=max(int(lot_size), 1),
            step=max(int(lot_size), 1),
            key="paper_quantity",
        )

        paper_columns[1].metric(
            "Paper Balance",
            f"₹ {st.session_state.paper_balance:,.2f}",
        )

        paper_columns[2].metric(
            "Open Positions",
            str(len(st.session_state.paper_positions)),
        )

        paper_columns[3].metric(
            "Closed Trades",
            str(len(st.session_state.paper_trades)),
        )

        open_disabled = (
            option_type == "WAIT"
            or premium_entry <= 0
        )

        if st.button(
            "▶️ One-Click Paper Trade",
            disabled=open_disabled,
            width="stretch",
        ):
            success, message = open_paper_position(
                index_choice,
                selected_expiry,
                option_type,
                option_strike,
                premium_entry,
                int(paper_quantity),
                premium_stop,
                premium_target1,
            )

            if success:
                st.success(message)
            else:
                st.error(message)

        open_positions_frame = paper_positions_dataframe(dataframe)

        if not open_positions_frame.empty:
            st.write("**Open Paper Positions**")

            st.dataframe(
                open_positions_frame,
                width="stretch",
                hide_index=True,
            )

            position_ids = open_positions_frame["ID"].tolist()

            selected_position_id = st.selectbox(
                "Select position to close",
                position_ids,
            )

            if st.button("⏹️ Close Selected Paper Position"):
                success, message = close_paper_position(
                    int(selected_position_id),
                    dataframe,
                    "Manual Exit",
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        paper_stats = calculate_paper_statistics()

        paper_stats_columns = st.columns(6)

        paper_stats_columns[0].metric(
            "Paper Total Trades",
            str(paper_stats["Total Trades"]),
        )
        paper_stats_columns[1].metric(
            "Paper Wins",
            str(paper_stats["Winning Trades"]),
        )
        paper_stats_columns[2].metric(
            "Paper Losses",
            str(paper_stats["Losing Trades"]),
        )
        paper_stats_columns[3].metric(
            "Paper Win Rate",
            f"{paper_stats['Win Rate']:.1f}%",
        )
        paper_stats_columns[4].metric(
            "Paper Net P&L",
            f"₹ {paper_stats['Net PnL']:,.2f}",
        )
        paper_stats_columns[5].metric(
            "Average P&L",
            f"₹ {paper_stats['Average PnL']:,.2f}",
        )

        closed_paper_frame = pd.DataFrame(
            st.session_state.paper_trades
        )

        if not closed_paper_frame.empty:
            with st.expander("View Paper Trade Journal"):
                st.dataframe(
                    closed_paper_frame,
                    width="stretch",
                    hide_index=True,
                )

                st.download_button(
                    "⬇️ Download Paper Journal CSV",
                    data=closed_paper_frame.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="shankar_paper_trade_journal.csv",
                    mime="text/csv",
                )

        # ---------------- BACKTESTING ----------------

        st.subheader("🧮 Historical 5-Minute Entry Strategy Backtest")

        backtest_columns = st.columns(2)

        backtest_capital = backtest_columns[0].number_input(
            "Backtest starting capital (₹)",
            min_value=10000.0,
            value=100000.0,
            step=10000.0,
        )

        backtest_risk = backtest_columns[1].number_input(
            "Backtest risk per trade (%)",
            min_value=0.25,
            max_value=5.0,
            value=1.0,
            step=0.25,
        )

        if st.button("Run Backtest", width="stretch"):
            backtest_trades, backtest_summary = backtest_strategy(
                candles,
                initial_capital=backtest_capital,
                risk_percent=backtest_risk,
            )

            result_columns = st.columns(6)

            result_columns[0].metric(
                "Initial Capital",
                f"₹ {backtest_summary['Initial Capital']:,.2f}",
            )
            result_columns[1].metric(
                "Final Capital",
                f"₹ {backtest_summary['Final Capital']:,.2f}",
            )
            result_columns[2].metric(
                "Net P&L",
                f"₹ {backtest_summary['Net PnL']:,.2f}",
            )
            result_columns[3].metric(
                "Total Trades",
                str(backtest_summary["Total Trades"]),
            )
            result_columns[4].metric(
                "Win Rate",
                f"{backtest_summary['Win Rate']:.1f}%",
            )
            result_columns[5].metric(
                "Max Drawdown",
                f"{backtest_summary['Max Drawdown']:.2f}%",
            )

            if not backtest_trades.empty:
                st.dataframe(
                    backtest_trades,
                    width="stretch",
                    hide_index=True,
                )

                st.download_button(
                    "⬇️ Download Backtest Results CSV",
                    data=backtest_trades.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="shankar_backtest_results.csv",
                    mime="text/csv",
                )
            else:
                st.info(
                    "No backtest trades were generated for the available "
                    "historical candles and selected rules."
                )

        # ---------------- OI ANALYSIS ----------------

        st.subheader("📊 OI Build-Up Analysis")

        oi_columns = st.columns(6)

        oi_columns[0].metric("OI Build-Up", oi_summary)
        oi_columns[1].metric("OI Bias", oi_bias)
        oi_columns[2].metric(
            "Total CE Chg OI",
            f"{total_ce_change:,.0f}",
        )
        oi_columns[3].metric(
            "Total PE Chg OI",
            f"{total_pe_change:,.0f}",
        )
        oi_columns[4].metric(
            "ATM CE Chg OI",
            f"{atm_ce_change:,.0f}",
        )
        oi_columns[5].metric(
            "ATM PE Chg OI",
            f"{atm_pe_change:,.0f}",
        )

        st.caption(" | ".join(oi_notes))

        # ---------------- SMC / LIQUIDITY ----------------

        st.subheader("🏦 Smart Money Concepts")

        smc_columns = st.columns(6)

        latest_bullish_ob = next(
            (
                item for item in reversed(order_blocks)
                if item["Type"] == "Bullish Order Block"
            ),
            None,
        )
        latest_bearish_ob = next(
            (
                item for item in reversed(order_blocks)
                if item["Type"] == "Bearish Order Block"
            ),
            None,
        )
        latest_bullish_fvg = next(
            (
                item for item in reversed(fair_value_gaps)
                if item["Type"] == "Bullish FVG"
            ),
            None,
        )
        latest_bearish_fvg = next(
            (
                item for item in reversed(fair_value_gaps)
                if item["Type"] == "Bearish FVG"
            ),
            None,
        )

        smc_columns[0].metric(
            "Bullish Order Block",
            (
                f"₹ {latest_bullish_ob['Low']:,.0f}–"
                f"{latest_bullish_ob['High']:,.0f}"
                if latest_bullish_ob
                else "N/A"
            ),
        )
        smc_columns[1].metric(
            "Bearish Order Block",
            (
                f"₹ {latest_bearish_ob['Low']:,.0f}–"
                f"{latest_bearish_ob['High']:,.0f}"
                if latest_bearish_ob
                else "N/A"
            ),
        )
        smc_columns[2].metric(
            "Bullish FVG",
            (
                f"₹ {latest_bullish_fvg['Low']:,.0f}–"
                f"{latest_bullish_fvg['High']:,.0f}"
                if latest_bullish_fvg
                else "N/A"
            ),
        )
        smc_columns[3].metric(
            "Bearish FVG",
            (
                f"₹ {latest_bearish_fvg['Low']:,.0f}–"
                f"{latest_bearish_fvg['High']:,.0f}"
                if latest_bearish_fvg
                else "N/A"
            ),
        )
        smc_columns[4].metric(
            "Buy-side Liquidity",
            f"₹ {buy_liquidity:,.2f}" if buy_liquidity else "N/A",
        )
        smc_columns[5].metric(
            "Sell-side Liquidity",
            f"₹ {sell_liquidity:,.2f}" if sell_liquidity else "N/A",
        )

        # ---------------- CHARTS ----------------

        st.subheader("📉 Professional Multi-Timeframe Chart")

        if not candles.empty:
            professional_chart = build_professional_candlestick(
                candles,
                support,
                resistance,
                max_pain,
                order_blocks,
                fair_value_gaps,
                buy_liquidity,
                sell_liquidity,
            )

            if not candles_15m.empty:
                recent_15m = candles_15m.tail(100)

                professional_chart.add_trace(
                    go.Scatter(
                        x=recent_15m["Datetime"],
                        y=recent_15m["Close"],
                        mode="lines",
                        name="15m Close",
                        line={"width": 2, "dash": "dot"},
                    )
                )

                professional_chart.add_trace(
                    go.Scatter(
                        x=recent_15m["Datetime"],
                        y=recent_15m["VWAP"],
                        mode="lines",
                        name="15m VWAP",
                        line={"width": 1.8, "dash": "dash"},
                    )
                )

            if not candles_60m.empty:
                recent_60m = candles_60m.tail(80)

                professional_chart.add_trace(
                    go.Scatter(
                        x=recent_60m["Datetime"],
                        y=recent_60m["Close"],
                        mode="lines",
                        name="60m Close",
                        line={"width": 2.2, "dash": "longdash"},
                    )
                )

                professional_chart.add_trace(
                    go.Scatter(
                        x=recent_60m["Datetime"],
                        y=recent_60m["VWAP"],
                        mode="lines",
                        name="60m VWAP",
                        line={"width": 1.6, "dash": "dot"},
                    )
                )

            st.plotly_chart(
                professional_chart,
                width="stretch",
                config={
                    "displaylogo": False,
                    "scrollZoom": True,
                    "responsive": True,
                },
            )
        else:
            st.warning(
                "Historical candles were unavailable, so the professional "
                "chart and SMC analysis could not be calculated."
            )

        st.subheader("📊 OI Profile Near ATM")

        oi_chart = (
            nearest_rows[
                ["Strike", "CE OI", "PE OI"]
            ]
            .set_index("Strike")
        )

        st.bar_chart(oi_chart, height=380)

        # ---------------- OPTION TABLE ----------------

        left_title, middle_title, right_title = st.columns(
            [8, 2, 8]
        )

        with left_title:
            st.markdown(
                '<div class="ce-heading">CALL SIDE — CE</div>',
                unsafe_allow_html=True,
            )

        with middle_title:
            st.markdown(
                '<div class="strike-heading">STRIKE</div>',
                unsafe_allow_html=True,
            )

        with right_title:
            st.markdown(
                '<div class="pe-heading">PUT SIDE — PE</div>',
                unsafe_allow_html=True,
            )

        def highlight_levels(row):
            strike = safe_float(row["Strike"])
            is_atm = math.isclose(strike, safe_float(atm_strike), rel_tol=0, abs_tol=0.001)
            is_resistance = math.isclose(strike, safe_float(resistance), rel_tol=0, abs_tol=0.001)
            is_support = math.isclose(strike, safe_float(support), rel_tol=0, abs_tol=0.001)

            if is_atm and is_resistance and is_support:
                css = "background:linear-gradient(90deg,#ef4444 0 33%,#facc15 33% 66%,#22c55e 66% 100%);color:#111827;font-weight:950;border:3px solid #111827"
            elif is_atm and is_resistance:
                css = "background:linear-gradient(90deg,#ef4444 0 50%,#facc15 50% 100%);color:#111827;font-weight:950;border:3px solid #7f1d1d"
            elif is_atm and is_support:
                css = "background:linear-gradient(90deg,#facc15 0 50%,#22c55e 50% 100%);color:#052e16;font-weight:950;border:3px solid #166534"
            elif is_resistance and is_support:
                css = "background:linear-gradient(90deg,#ef4444 0 50%,#22c55e 50% 100%);color:#ffffff;font-weight:950;border:3px solid #111827"
            elif is_resistance:
                css = "background-color:#ef4444;color:#ffffff;font-weight:950;border-top:3px solid #7f1d1d;border-bottom:3px solid #7f1d1d"
            elif is_support:
                css = "background-color:#22c55e;color:#052e16;font-weight:950;border-top:3px solid #166534;border-bottom:3px solid #166534"
            elif is_atm:
                css = "background-color:#facc15;color:#1c1917;font-weight:950;border-top:3px solid #a16207;border-bottom:3px solid #a16207"
            else:
                css = ""
            return [css] * len(row)

        def emphasize_strike_column(column):
            return [
                "font-weight: bold; background-color: #f3f4f6"
            ] * len(column)

        render_colored_option_table(
            nearest_rows,
            atm_strike,
            resistance,
            support,
            height=820,
        )

        st.info(
            "🟨 Yellow Strike = ATM | "
            "🟥 Red CE Side = Max CE OI Resistance | "
            "🟩 Green PE Side = Max PE OI Support"
        )

        # ---------------- SIGNAL HISTORY ----------------

        st.subheader("🧾 Signal History")

        history_frame = pd.DataFrame(st.session_state.signal_log)

        if not history_frame.empty:
            st.dataframe(
                history_frame.tail(100),
                width="stretch",
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download Signal History CSV",
                data=history_frame.to_csv(index=False).encode("utf-8"),
                file_name="shankar_signal_history.csv",
                mime="text/csv",
            )
        else:
            st.info("No signal history recorded yet.")

        # ---------------- TRADE CHECKLIST ----------------

        st.subheader("✅ Pre-Trade Checklist")

        checklist_columns = st.columns(5)

        checklist_columns[0].metric(
            "Trend",
            "Confirmed" if trend_direction in {-1, 1} else "Unavailable",
        )
        checklist_columns[1].metric(
            "VWAP",
            (
                "Above" if spot_price > latest_vwap else "Below"
                if latest_vwap
                else "Unavailable"
            ),
        )
        checklist_columns[2].metric(
            "Liquidity",
            "Available" if buy_liquidity and sell_liquidity else "Limited",
        )
        checklist_columns[3].metric(
            "Signal",
            recommendation,
        )
        checklist_columns[4].metric(
            "Risk Lot",
            (
                f"{allowed_lots} allowed"
                if option_type != "WAIT"
                else "No trade"
            ),
        )

        # ---------------- FINAL SAFETY ----------------

        st.warning(
            "Educational analysis only. Paper trades are simulated and no real orders are placed. "
            "Trade Quality is a rule-based score—not a validated probability. "
            "Confirm trend, liquidity, bid/ask spread, lot size and risk before "
            "placing any real trade."
        )

    except requests.HTTPError as error:
        auto_refresh = False
        st.error(
            "Dhan API request failed. Check whether the Access Token has "
            f"expired and confirm Data API subscription. Details: {error}"
        )

    except Exception as error:
        auto_refresh = False
        st.error(f"Full-dashboard analysis error: {error}")


st.divider()

st.write(
    "Last refreshed:",
    datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p"),
)

if auto_refresh and st.session_state.load_chain:
    time.sleep(10)
    st.rerun()
