from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st


st.set_page_config(
    page_title="Support Control Room",
    page_icon="SC",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root { --ink: #18232c; --muted: #6b7780; --paper: #f5f7f6; --line: #dfe6e2; --teal: #0d766e; --orange: #dd6b3d; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: var(--paper); color: var(--ink); }
    .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"] { color: var(--ink); }
    .stApp [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    .stApp [data-testid="stMetricValue"] { color: var(--ink) !important; }
    [data-testid="stSidebar"] { background: #182c31; }
    [data-testid="stSidebar"] * { color: #edf5f0 !important; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    h1 { font-size: 2.2rem !important; margin-bottom: .25rem; }
    .eyebrow { color: var(--teal); font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .subtitle { color: var(--muted); margin: 0 0 1.5rem; }
    .status-pill { display: inline-block; border: 1px solid #b8d8ce; background: #e8f5ef; color: #17624f; border-radius: 999px; padding: .25rem .6rem; font-size: .78rem; font-weight: 700; }
    .panel { background: white; border: 1px solid var(--line); border-radius: 8px; padding: 1.1rem 1.2rem; }
    .ticket-id { color: var(--teal); font-family: 'Space Grotesk', sans-serif; font-weight: 700; }
    div[data-testid="stMetric"] { background: white; border: 1px solid var(--line); border-radius: 8px; padding: .9rem 1rem; }
    .stButton > button, .stFormSubmitButton > button { border-radius: 6px; font-weight: 700; border: 0; background: var(--teal); color: white; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { background: #095b56; color: white; }
    textarea, input { border-radius: 6px !important; color: var(--ink) !important; background: white !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULT_API_URL = os.getenv("SUPPORT_API_URL", "http://127.0.0.1:8000")


def api_request(method: str, path: str, base_url: str, **kwargs: Any) -> tuple[bool, Any]:
    try:
        response = httpx.request(
            method, f"{base_url.rstrip('/')}{path}", timeout=8.0, **kwargs)
        if response.is_success:
            return True, response.json()
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        return False, f"HTTP {response.status_code}: {detail}"
    except httpx.HTTPError as exc:
        return False, f"Backend unavailable: {exc}"


def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown("## SUPPORT / CONTROL ROOM")
        st.caption("Memory-aware customer operations")
        st.divider()
        api_url = st.text_input("Backend URL", value=DEFAULT_API_URL)
        ok, health = api_request("GET", "/health", api_url)
        if ok:
            st.success("API connected", icon=":material/check_circle:")
        else:
            st.error("API offline", icon=":material/error:")
            st.caption(str(health))
        view = st.radio("Workspace", [
                        "Overview", "New ticket", "Customer memory"], label_visibility="collapsed")
        st.divider()
        st.caption("Hindsight Cloud memory")
        st.caption("FastAPI + Groq + persistent memory")
    return api_url, view


def overview(api_url: str) -> None:
    st.markdown('<div class="eyebrow">Operations overview</div>',
                unsafe_allow_html=True)
    st.title("Support control room")
    st.markdown('<p class="subtitle">See where the queue stands, then move directly into the next customer conversation.</p>', unsafe_allow_html=True)

    ok, metrics = api_request("GET", "/api/analytics/metrics", api_url)
    if not ok:
        st.error(str(metrics))
        return

    columns = st.columns(4)
    columns[0].metric("Tickets handled", metrics.get("total_tickets", 0))
    columns[1].metric("Customers", metrics.get("customer_count", 0))
    columns[2].metric(
        "Avg resolution", f"{metrics.get('avg_resolution_time_minutes', 0):.1f} min")
    columns[3].metric("Service", metrics.get(
        "service_status", "unknown").title())

    st.write("")
    left, right = st.columns([1.25, .75])
    with left:
        st.markdown("### System posture")
        st.markdown('<div class="panel">The agent combines customer history, sentiment signals, solution generation, and escalation routing in one request path.</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown("### Memory layer")
        memory_ok, memory = api_request("GET", "/api/memory/status", api_url)
        if memory_ok:
            st.json(memory, expanded=True)
        else:
            st.warning(str(memory))
    with right:
        st.markdown("### Quick actions")
        if st.button("Open ticket workspace", width="stretch"):
            st.session_state["view"] = "New ticket"
            st.rerun()
        if st.button("Inspect a customer", width="stretch"):
            st.session_state["view"] = "Customer memory"
            st.rerun()
        st.markdown(
            "<br><span class='status-pill'>Demo memory active</span>", unsafe_allow_html=True)


def new_ticket(api_url: str) -> None:
    st.markdown('<div class="eyebrow">Agent workspace</div>',
                unsafe_allow_html=True)
    st.title("New support ticket")
    st.markdown('<p class="subtitle">Send a customer message through the full support pipeline and inspect the reasoning signals.</p>', unsafe_allow_html=True)

    with st.form("ticket_form", clear_on_submit=False):
        customer_id = st.text_input(
            "Customer ID", value=st.session_state.get("customer_id", "cust_demo_001"))
        channel = st.selectbox("Channel", ["chat", "email", "phone", "web"])
        message = st.text_area(
            "Customer message", height=150, placeholder="Describe the customer issue...")
        submitted = st.form_submit_button("Run support agent", width="stretch")

    if submitted:
        if not customer_id.strip() or not message.strip():
            st.warning("Customer ID and message are required.")
            return
        ok, result = api_request("POST", "/api/support/ticket", api_url, json={
                                 "customer_id": customer_id, "message": message, "channel": channel})
        if not ok:
            st.error(str(result))
            return
        st.session_state["customer_id"] = customer_id
        st.session_state["last_ticket"] = result
        st.success("Ticket processed")

    result = st.session_state.get("last_ticket")
    if not result:
        return

    st.write("")
    st.markdown(
        f"### <span class='ticket-id'>{result.get('ticket_id', 'Ticket')}</span>", unsafe_allow_html=True)
    left, right = st.columns([1.4, .8])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("#### Recommended response")
        st.write(result.get("response", ""))
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("#### Pipeline signals")
        st.json(result.get("metadata", {}), expanded=True)
        st.caption("Memory used")
        st.json(result.get("memory_used", {}), expanded=True)

    with st.expander("Resolve this ticket"):
        with st.form("resolve_form"):
            outcome = st.selectbox(
                "Outcome", ["resolved", "escalated", "follow_up_required"])
            method = st.text_input("Resolution method", value="standard_flow")
            minutes = st.number_input(
                "Resolution time (minutes)", min_value=0, value=5, step=1)
            satisfaction = st.slider(
                "Satisfaction score", min_value=1.0, max_value=10.0, value=8.0, step=.5)
            resolve = st.form_submit_button("Save resolution", width="stretch")
        if resolve:
            ok, response = api_request(
                "POST",
                f"/api/support/ticket/{result.get('ticket_id')}/resolve",
                api_url,
                json={"customer_id": st.session_state.get(
                    "customer_id", ""), "outcome": outcome, "resolution_method": method, "resolution_time_minutes": minutes, "satisfaction_score": satisfaction},
            )
            if ok:
                st.success("Resolution saved to memory")
                st.json(response)
            else:
                st.error(str(response))


def customer_memory(api_url: str) -> None:
    st.markdown('<div class="eyebrow">Customer intelligence</div>',
                unsafe_allow_html=True)
    st.title("Customer memory")
    st.markdown('<p class="subtitle">Inspect the profile, recurring issue patterns, and recent conversations for one customer.</p>', unsafe_allow_html=True)

    with st.form("customer_form"):
        customer_id = st.text_input(
            "Customer ID", value=st.session_state.get("customer_id", "cust_demo_001"))
        lookup = st.form_submit_button("Load customer", width="stretch")

    if lookup:
        ok, result = api_request(
            "GET", f"/api/customer/{customer_id.strip()}/profile", api_url)
        if ok:
            st.session_state["customer_id"] = customer_id.strip()
            st.session_state["customer_profile"] = result
        else:
            st.error(str(result))

    result = st.session_state.get("customer_profile")
    if not result:
        st.info("Load a customer to inspect their memory.")
        return

    profile = result.get("profile", {})
    metrics = result.get("metrics", {})
    columns = st.columns(4)
    columns[0].metric("Tier", profile.get("tier", "Standard"))
    columns[1].metric("Tickets", profile.get("total_tickets", 0))
    columns[2].metric("Churn risk", profile.get("churn_risk", "low").title())
    columns[3].metric(
        "Repeat rate", f"{result.get('patterns', {}).get('repeat_rate', 0):.0%}")

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Profile")
        st.json(profile, expanded=True)
        st.markdown("### Issue patterns")
        st.json(result.get("patterns", {}), expanded=True)
    with right:
        st.markdown("### Recent tickets")
        tickets = result.get("ticket_history", [])
        if not tickets:
            st.caption("No prior tickets found.")
        for ticket in reversed(tickets):
            with st.container(border=True):
                st.markdown(
                    f"**{ticket.get('ticket_id', 'ticket')}** · {ticket.get('category', 'general')} · {ticket.get('status', 'open')}")
                st.caption(ticket.get("message", ""))
                st.write(ticket.get("response", ""))


api_url, selected_view = render_sidebar()
selected_view = st.session_state.get("view", selected_view)
if selected_view == "Overview":
    overview(api_url)
elif selected_view == "New ticket":
    new_ticket(api_url)
else:
    customer_memory(api_url)
