import streamlit as st
import json
import os
import pandas as pd
import sys

# Add project root so Python can import backend scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from deploy_multi import deploy_single
from stop_all import stop_single
from status_check import get_single_status

# --- Day 8 Monitoring imports ---
from monitoring import (
    get_container_uptime,
    get_deployment_history,
    get_service_version
)

# Path to services.json
SERVICES_FILE = os.path.join(BASE_DIR, "services.json")

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Multi-Service Orchestrator", layout="wide")

# ---------------------------------------------------------
# 🔷 Custom UI Styling (ONLY UI – no logic touched)
# ---------------------------------------------------------
st.markdown("""
<style>
h1 {
    text-align:center;
    font-weight:800;
}
.section-box {
    background:#111827;
    padding:18px;
    border-radius:12px;
    margin-bottom:15px;
}
.card {
    background:#1f2933;
    padding:14px;
    border-radius:12px;
    border:1px solid #2d3846;
}
.stButton > button {
    width:100%;
    border-radius:8px;
}
.metric-card {
    background:#020817;
    border-radius:12px;
    padding:10px;
    border:1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Services
# ---------------------------------------------------------
try:
    with open(SERVICES_FILE, "r") as f:
        services = json.load(f)
except Exception as e:
    st.error(f"Error loading services.json: {e}")
    services = []

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🚀 Smart Multi-Service Deployment Orchestrator")
st.markdown("### Control & monitor all services with production-grade visibility")

# =========================================================
# 🔹 SERVICE CONTROL PANEL
# =========================================================
st.subheader("⚙️ Service Control Panel")

for svc in services:
    name = svc["name"]

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"#### 🔹 {name}")

        col1,col2,col3 = st.columns(3)

        if col1.button(f"🚀 Deploy {name}", key=f"deploy_{name}"):
            st.code(deploy_single(name))

        if col2.button(f"🛑 Stop {name}", key=f"stop_{name}"):
            st.code(stop_single(name))

        if col3.button(f"📡 Status {name}", key=f"status_{name}"):
            st.code(get_single_status(name))

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

# =========================================================
# 🔹 SERVICES REGISTRY
# =========================================================
st.subheader("📋 Registered Services")

if services:
    df = pd.DataFrame(services)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("services.json is empty.")

# =========================================================
# 🔹 MONITORING DASHBOARD
# =========================================================
st.subheader("📊 Service Monitoring Dashboard")

for svc in services:
    name = svc["name"]

    # ---------------------------------------
    # ✅ EXACT SAME STATUS LOGIC (NO CHANGE)
    # ---------------------------------------
    raw = get_single_status(name).strip()

    try:
        state, started = raw.split("|")
    except:
        state = "not_running"
        started = ""

    if state == "not_running":
        status = "🔴 Down"
        uptime = "Not Running"
    elif state == "running":
        status = "🟢 Healthy"
        uptime = started
    else:
        status = "⚠️ Unhealthy"
        uptime = "Unknown"

    version = get_service_version(name)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"#### 🧩 {name}")

        m1,m2,m3 = st.columns(3)

        with m1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="⏱ Uptime", value=uptime)
            st.markdown('</div>', unsafe_allow_html=True)

        with m2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="📦 Image Version", value=version)
            st.markdown('</div>', unsafe_allow_html=True)

        with m3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="✅ Service Status", value=status)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

# =========================================================
# 🔹 DEPLOYMENT HISTORY
# =========================================================
st.subheader("📜 Deployment Audit Log")

history = get_deployment_history()
if history:
    st.json(history)
else:
    st.warning("No deployment history found yet.")
