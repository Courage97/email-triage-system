import pathfix  # noqa
import streamlit as st

from config.constants import SAMPLE_EMAILS, CATEGORIES, ROUTING_MAP
from models.predictor import predict_email, combine_subject_body
from models.validator import validate_result
from components.result_card import render_result_card, render_probability_chart
from components.routing_card import render_routing_card, render_override_routing_card
from components.confidence_bar import render_threshold_legend
from utils.log_manager import add_log_entry


def render_classify(models: dict):
    _render_header()
    subject, body = _render_input_panel()

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        classify_clicked = st.button("Classify →", type="primary",
                                     use_container_width=True, key="classify_btn")

    if classify_clicked:
        if not subject.strip() and not body.strip():
            st.error("Please enter a subject or body before classifying.")
            return
        full_text = combine_subject_body(subject, body)
        with st.spinner("Analysing with MobileBERT…"):
            result = predict_email(full_text, models)
        # Store result in session state so it survives reruns
        st.session_state['last_result']  = result
        st.session_state['last_subject'] = subject
        st.session_state['last_body']    = body
        st.session_state['show_override'] = False

    # Show results if we have a stored result
    if 'last_result' in st.session_state:
        result  = st.session_state['last_result']
        subject = st.session_state.get('last_subject', subject)
        body    = st.session_state.get('last_body', body)
        validation = validate_result(result)

        st.markdown("---")
        render_result_card(result)
        render_routing_card(result, elapsed_ms=result['elapsed_ms'])
        render_probability_chart(result)
        st.markdown("---")
        _render_actions(result, validation, subject, body)


def _render_header():
    st.markdown("## 📧 Email Classifier")
    st.caption("Paste an email below — the AI will classify and route it instantly")
    render_threshold_legend()
    st.markdown("<br>", unsafe_allow_html=True)


def _render_input_panel():
    selected = st.selectbox(
        "Quick-test with a sample email",
        options=list(SAMPLE_EMAILS.keys()),
        key="sample_select"
    )
    is_sample = selected != list(SAMPLE_EMAILS.keys())[0]

    col1, col2 = st.columns([1, 2])
    with col1:
        subject = st.text_input(
            "Subject Line",
            value=SAMPLE_EMAILS[selected]["subject"] if is_sample else "",
            placeholder="Enter email subject…",
            key="email_subject"
        )
    with col2:
        body = st.text_area(
            "Email Body",
            value=SAMPLE_EMAILS[selected]["body"] if is_sample else "",
            height=160,
            placeholder="Paste or type the email content here…",
            key="email_body"
        )
    return subject, body


def _render_actions(result, validation, subject, body):
    st.caption("ACTIONS")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("✅ Approve & Route", use_container_width=True, key="btn_approve"):
            _save_and_confirm(subject, body, result, validation,
                              was_overridden=False, original_category=None)
            # Clear result after saving so user can classify next email
            del st.session_state['last_result']

    with col2:
        if st.button("✏️ Wrong Category? Override", use_container_width=True,
                     key="btn_override_toggle"):
            st.session_state['show_override'] = not st.session_state.get('show_override', False)

    if st.session_state.get('show_override', False):
        _render_override_panel(result, validation, subject, body)


def _render_override_panel(result, validation, subject, body):
    st.markdown("**Select the correct category:**")
    other_cats  = [c for c in CATEGORIES if c != result['category']]
    all_options = [result['category']] + other_cats

    new_category = st.selectbox("Correct category", options=all_options,
                                index=0, key="override_category_select")

    if new_category != result['category']:
        new_routing = ROUTING_MAP.get(new_category, {})
        st.info(f"→ Will route to: **{new_routing.get('icon','📧')} {new_routing.get('dept','Registry')}**")

    if st.button("✅ Confirm Override", type="primary", key="btn_confirm_override"):
        if new_category == result['category']:
            st.info("No change — category is the same as AI prediction.")
        else:
            overridden_result     = {**result, 'category': new_category}
            overridden_validation = validate_result(overridden_result)
            render_override_routing_card(
                original_category=result['category'],
                new_category=new_category,
                elapsed_ms=result['elapsed_ms'],
            )
            _save_and_confirm(subject, body, overridden_result, overridden_validation,
                              was_overridden=True, original_category=result['category'])
            st.session_state['show_override'] = False
            if 'last_result' in st.session_state:
                del st.session_state['last_result']


def _save_and_confirm(subject, body, result, validation, was_overridden, original_category):
    import os
    from config.constants import LOG_FILE_PATH

    routing  = ROUTING_MAP.get(result['category'], {})
    priority = validation['priority']

    entry = add_log_entry(
        subject=subject,
        body=body,
        category=result['category'],
        confidence=result['confidence'],
        department=routing.get('dept', 'Registry'),
        priority=priority['key'],
        elapsed_ms=result['elapsed_ms'],
        was_overridden=was_overridden,
        original_category=original_category,
    )

    if os.path.exists(LOG_FILE_PATH):
        dept = routing.get('dept', 'Registry')
        if was_overridden:
            st.success(f"✅ Override confirmed. Routed to **{dept}** · ID: `{entry['id']}`")
        else:
            st.success(f"✅ Approved and routed to **{dept}** · ID: `{entry['id']}`")
        st.info("Go to **Email Log** or **Dashboard** to view it.")
    else:
        st.error(f"❌ Save failed. Could not write to: {LOG_FILE_PATH}")