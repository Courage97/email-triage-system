import pathfix  # noqa
# pages/inbox.py
# Real-time IMAP inbox — fetch, classify, approve, mark as read

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config.constants import (
    IMAP_PROVIDERS, AUTOREFRESH_OPTIONS, INBOX_FETCH_LIMIT,
    ROUTING_MAP, IRRELEVANT_THRESHOLD,
)
from utils.imap_client import (
    connect, fetch_unread, fetch_all_recent,
    mark_as_read, disconnect, test_connection,
)
from utils.log_manager import add_log_entry
from models.predictor import predict_email, combine_subject_body
from models.validator import validate_result


def render_inbox(models: dict):
    st.markdown("## 📬 Live Inbox")
    st.caption("Fetch and classify emails directly from your mailbox — no copy-pasting needed")

    _render_connection_panel()

    if not st.session_state.get('imap_connected'):
        st.info("👆 Connect your mailbox above to start fetching emails.")
        return

    st.divider()
    _render_inbox_controls()
    st.divider()
    _render_email_queue(models)


# ─── Connection Panel ─────────────────────────────────────────────────────────

def _render_connection_panel():
    with st.expander(
        "📡 Mailbox Connection" + (" ✅ Connected" if st.session_state.get('imap_connected') else " — Click to configure"),
        expanded=not st.session_state.get('imap_connected', False)
    ):
        st.caption("Your credentials are used only for this session and never stored.")

        provider_name = st.selectbox(
            "Email Provider",
            options=list(IMAP_PROVIDERS.keys()),
            key="imap_provider"
        )
        provider = IMAP_PROVIDERS[provider_name]

        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input(
                "IMAP Host",
                value=provider['host'] or "",
                placeholder="imap.gmail.com",
                key="imap_host_field"
            )
        with col2:
            # Always use the provider preset port — never cache stale value
            port = st.number_input(
                "Port",
                value=int(provider['port']),
                min_value=1, max_value=65535,
                key=f"imap_port_{provider_name}"
            )

        col3, col4 = st.columns(2)
        with col3:
            username = st.text_input(
                "Email Address",
                placeholder="registry@university.edu",
                key="imap_username_field"
            )
        with col4:
            password = st.text_input(
                "Password / App Password",
                type="password",
                placeholder="••••••••",
                key="imap_password_field"
            )

        # Gmail note
        if provider_name == "Gmail":
            st.info(
                "**Gmail users:** You must use an **App Password**, not your regular password. "
                "Enable 2FA → Google Account → Security → App Passwords."
            )

        col_test, col_connect, col_disconnect = st.columns([1, 1, 1])

        with col_test:
            if st.button("🔍 Test Connection", key="imap_test", use_container_width=True):
                if not host or not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Testing…"):
                        ok, msg = test_connection(host, int(port), username, password)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

        with col_connect:
            if st.button("🔗 Connect", type="primary", key="imap_connect", use_container_width=True):
                if not host or not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Connecting…"):
                        ok, msg = test_connection(host, int(port), username, password)
                    if ok:
                        st.session_state['imap_connected']       = True
                        st.session_state['imap_host_saved']      = host
                        st.session_state['imap_port_saved']      = int(port)
                        st.session_state['imap_username_saved']  = username
                        st.session_state['imap_password_saved']  = password
                        st.session_state['inbox_emails']   = []
                        st.success("✅ Connected! Fetching inbox…")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        with col_disconnect:
            if st.session_state.get('imap_connected'):
                if st.button("🔌 Disconnect", key="imap_disconnect", use_container_width=True):
                    _clear_connection()
                    st.rerun()


# ─── Inbox Controls ───────────────────────────────────────────────────────────

def _render_inbox_controls():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.caption(f"📧 Connected as: **{st.session_state.get('imap_username_saved','')}**")

    with col2:
        view_mode = st.selectbox(
            "Show",
            ["Unread only", "Recent (all)"],
            key="inbox_view_mode"
        )

    with col3:
        refresh_label = st.selectbox(
            "Auto-refresh",
            list(AUTOREFRESH_OPTIONS.keys()),
            index=1,
            key="inbox_autorefresh"
        )

    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_clicked = st.button("🔄 Fetch Now", use_container_width=True, key="inbox_fetch_btn")

    # Auto-refresh
    interval = AUTOREFRESH_OPTIONS[refresh_label]
    if interval > 0:
        st_autorefresh(interval=interval * 1000, key="inbox_autorefresh_timer")

    # Fetch on button click OR on first load after connect
    if fetch_clicked or 'inbox_emails' not in st.session_state:
        _fetch_emails(view_mode)

    # Show last fetch time
    if st.session_state.get('inbox_last_fetched'):
        st.caption(f"Last fetched: {st.session_state['inbox_last_fetched']}")


# ─── Email Queue ──────────────────────────────────────────────────────────────

def _render_email_queue(models: dict):
    emails = st.session_state.get('inbox_emails', [])

    if not emails:
        st.info("📭 No unread emails found. Try switching to 'Recent (all)' or click Fetch Now.")
        return

    st.caption(f"INBOX — {len(emails)} EMAIL(S)")

    for i, em in enumerate(emails):
        _render_email_row(em, i, models)


def _render_email_row(em: dict, index: int, models: dict):
    """Render a single inbox email as an expandable classify card."""
    key_prefix = f"inbox_{index}_{em.get('uid', index)}"

    with st.expander(f"📧 **{em['subject']}** · *{em['sender']}* · `{em['date']}`"):

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**From:** {em['sender']}")
            st.markdown(f"**Date:** {em['date']}")
            st.markdown(f"**Subject:** {em['subject']}")
            st.divider()
            st.caption("BODY PREVIEW")
            st.text(em['body'][:500] + ("…" if len(em['body']) > 500 else ""))

        with col2:
            classify_key = f"{key_prefix}_classify"
            if st.button("🤖 Classify", key=classify_key, use_container_width=True, type="primary"):
                with st.spinner("Classifying…"):
                    full_text = combine_subject_body(em['subject'], em['body'])
                    result    = predict_email(full_text, models)
                st.session_state[f"{key_prefix}_result"] = result

        # Show result if classified
        result = st.session_state.get(f"{key_prefix}_result")
        if result:
            _render_inline_result(em, result, key_prefix, models)


def _render_inline_result(em: dict, result: dict, key_prefix: str, models: dict):
    """Render classification result + action buttons inline in the email row."""
    validation = validate_result(result)
    routing    = ROUTING_MAP.get(result['category'], {})
    conf_pct   = result['confidence'] * 100

    st.divider()

    # ── Irrelevant flag ───────────────────────────────────────────────────
    if validation['is_irrelevant']:
        st.error(
            f"⛔ **Irrelevant / Not for Registry**\n\n"
            f"{validation['irrelevant_reason']}"
        )
        col_irr, col_override = st.columns(2)
        with col_irr:
            if st.button("✅ Confirm Irrelevant", key=f"{key_prefix}_confirm_irr",
                         use_container_width=True):
                _save_email(em, result, validation, irrelevant=True)
                _mark_read_in_imap(em)
                st.success("Marked as irrelevant and logged.")
                del st.session_state[f"{key_prefix}_result"]
                st.rerun()
        with col_override:
            if st.button("✏️ Override Category", key=f"{key_prefix}_irr_override",
                         use_container_width=True):
                st.session_state[f"{key_prefix}_show_override"] = True
        return

    # ── Normal result ─────────────────────────────────────────────────────
    st.markdown(f"**Category:** {routing.get('icon','📧')} {result['category']}")
    st.markdown(f"**Route to:** {routing.get('dept','Registry')}")
    st.markdown(f"**Priority:** {validation['priority']['badge']} {validation['priority']['label']}")
    st.caption(f"Confidence: {conf_pct:.1f}%")
    st.progress(int(conf_pct))

    if validation['alert']:
        if validation['alert']['type'] == 'warning':
            st.warning(validation['alert']['message'])
        else:
            st.error(validation['alert']['message'])

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Route", key=f"{key_prefix}_approve",
                     use_container_width=True, type="primary"):
            _save_email(em, result, validation, irrelevant=False)
            _mark_read_in_imap(em)
            st.success(f"✅ Routed to **{routing.get('dept','Registry')}**")
            del st.session_state[f"{key_prefix}_result"]
            st.rerun()

    with col2:
        if st.button("✏️ Override", key=f"{key_prefix}_override_btn",
                     use_container_width=True):
            st.session_state[f"{key_prefix}_show_override"] = True

    # Override panel
    if st.session_state.get(f"{key_prefix}_show_override"):
        _render_override(em, result, validation, key_prefix)


def _render_override(em, result, validation, key_prefix):
    from config.constants import CATEGORIES
    st.caption("SELECT CORRECT CATEGORY")

    other_cats   = [c for c in CATEGORIES if c != result['category']]
    all_options  = [result['category']] + other_cats
    new_category = st.selectbox("Correct category", all_options,
                                key=f"{key_prefix}_override_select")

    if st.button("✅ Confirm Override", key=f"{key_prefix}_confirm_override",
                 type="primary", use_container_width=True):
        overridden_result     = {**result, 'category': new_category}
        overridden_validation = validate_result(overridden_result)
        _save_email(
            em, overridden_result, overridden_validation,
            irrelevant=False, was_overridden=True,
            original_category=result['category']
        )
        _mark_read_in_imap(em)
        new_routing = ROUTING_MAP.get(new_category, {})
        st.success(f"✅ Override confirmed. Routed to **{new_routing.get('dept','Registry')}**")
        del st.session_state[f"{key_prefix}_result"]
        st.session_state[f"{key_prefix}_show_override"] = False
        st.rerun()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _fetch_emails(view_mode: str):
    """Connect to IMAP and fetch emails into session state."""
    from datetime import datetime
    try:
        mail = connect(
            st.session_state['imap_host_saved'],
            st.session_state['imap_port_saved'],
            st.session_state['imap_username_saved'],
            st.session_state['imap_password_saved'],
        )
        if view_mode == "Unread only":
            emails = fetch_unread(mail, limit=INBOX_FETCH_LIMIT)
        else:
            emails = fetch_all_recent(mail, limit=INBOX_FETCH_LIMIT)
        disconnect(mail)
        st.session_state['inbox_emails']      = emails
        st.session_state['inbox_last_fetched'] = datetime.now().strftime('%H:%M:%S')
    except Exception as e:
        st.error(f"❌ Fetch failed: {e}")
        st.session_state['inbox_emails'] = []


def _mark_read_in_imap(em: dict):
    """Mark the email as read in the actual inbox."""
    try:
        mail = connect(
            st.session_state['imap_host_saved'],
            st.session_state['imap_port_saved'],
            st.session_state['imap_username_saved'],
            st.session_state['imap_password_saved'],
        )
        mark_as_read(mail, em['uid'])
        disconnect(mail)
    except Exception as e:
        print(f"[inbox] mark_as_read failed: {e}")


def _save_email(
    em:                dict,
    result:            dict,
    validation:        dict,
    irrelevant:        bool  = False,
    was_overridden:    bool  = False,
    original_category: str   = None,
):
    """Save classified email to the log."""
    routing  = ROUTING_MAP.get(result['category'], {})
    priority = validation['priority']
    category = "Irrelevant" if irrelevant else result['category']
    dept     = "Not Routed" if irrelevant else routing.get('dept', 'Registry')

    add_log_entry(
        subject=em.get('subject', ''),
        body=em.get('body', ''),
        category=category,
        confidence=result['confidence'],
        department=dept,
        priority=priority.get('key', 'normal'),
        elapsed_ms=result.get('elapsed_ms', '—'),
        was_overridden=was_overridden,
        original_category=original_category,
    )


def _clear_connection():
    """Clear all IMAP session state."""
    for key in ['imap_connected', 'imap_host_saved', 'imap_port_saved',
                'imap_username_saved', 'imap_password_saved', 'inbox_emails',
                'inbox_last_fetched']:
        st.session_state.pop(key, None)