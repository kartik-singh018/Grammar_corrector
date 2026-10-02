import streamlit as st

from grammar_checker import (
    check_grammar,
    correct_text
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="English Grammar Checker",
    page_icon="📝",
    layout="centered"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 17px;
        margin-bottom: 30px;
    }


    /* Section headings */

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 20px;
        margin-bottom: 12px;
    }


    /* Result cards */

    .result-card {
        padding: 22px;
        border-radius: 15px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .success-card {
        background: #103b29;
        border-left: 5px solid #22c55e;
    }

    .error-card {
        background: #3b2025;
        border-left: 5px solid #ff4b4b;
    }


    /* Corrected sentence */

    .corrected-text {
        font-size: 22px;
        font-weight: 600;
        line-height: 1.5;
    }


    /* Small text */

    .small-text {
        color: #a7b0bd;
        font-size: 14px;
        margin-top: 7px;
    }


    /* Error title */

    .error-title {
        font-size: 18px;
        font-weight: 650;
    }


    /* Statistics */

    .stat-box {
        padding: 15px;
        border-radius: 12px;
        background: #1f2937;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📝 English Grammar Checker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Detect common English grammar mistakes using '
    'NLP, spaCy and Part-of-Speech tagging.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INPUT
# ============================================================

st.markdown(
    '<div class="section-title">✍️ Write your sentence</div>',
    unsafe_allow_html=True
)

text = st.text_area(
    "Sentence",
    height=160,
    placeholder=(
        "Example: He go to school every day."
    ),
    label_visibility="collapsed"
)


# Character count

if text:

    st.caption(
        f"{len(text)} characters"
    )


# ============================================================
# BUTTON
# ============================================================

analyze = st.button(
    "🔎 Analyze Sentence",
    use_container_width=True
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not text.strip():

        st.warning(
            "⚠️ Please enter a sentence first."
        )

    else:

        errors, doc = check_grammar(text)

        corrected = correct_text(
            text,
            errors
        )


        # ====================================================
        # SEPARATOR
        # ====================================================

        st.divider()


        # ====================================================
        # ANALYSIS HEADER
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '📊 Analysis'
            '</div>',
            unsafe_allow_html=True
        )


        # ====================================================
        # STATISTICS
        # ====================================================

        word_count = sum(
            1
            for token in doc
            if not token.is_space
            and not token.is_punct
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                '<div class="stat-box">'
                '<div>Grammar Errors</div>'
                f'<h2>{len(errors)}</h2>'
                '</div>',
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                '<div class="stat-box">'
                '<div>Words</div>'
                f'<h2>{word_count}</h2>'
                '</div>',
                unsafe_allow_html=True
            )


        # ====================================================
        # NO ERRORS
        # ====================================================

        if not errors:

            st.success(
                "✅ No grammar errors found!"
            )

            st.caption(
                "Your sentence passed the current grammar rules."
            )


        # ====================================================
        # ERRORS FOUND
        # ====================================================

        else:

            st.markdown(
                '<div class="section-title">'
                '✨ Corrected Sentence'
                '</div>',
                unsafe_allow_html=True
            )

            # Use Streamlit's native success box.
            # This prevents HTML from appearing as text.

            st.success(corrected)


            # =================================================
            # DETECTED ERRORS
            # =================================================

            st.markdown(
                '<div class="section-title">'
                '🔍 Detected Errors'
                '</div>',
                unsafe_allow_html=True
            )


            for number, error in enumerate(
                errors,
                start=1
            ):

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### ❌ Error {number}"
                    )

                    st.write(
                        f"**Incorrect:** "
                        f"`{error['error']}`"
                    )

                    st.write(
                        f"**💡 Suggestion:** "
                        f"`{error['suggestion']}`"
                    )

                    st.write(
                        f"**📖 Explanation:** "
                        f"{error['message']}"
                    )


        # ====================================================
        # POS TAGGING
        # ====================================================

        st.markdown(
            '<div class="section-title">'
            '🏷️ POS Tagging'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "spaCy identifies the grammatical category "
            "of each word."
        )


        # Header

        pos_col1, pos_col2, pos_col3 = st.columns(
            [2, 2, 2]
        )

        with pos_col1:
            st.markdown("**Word**")

        with pos_col2:
            st.markdown("**POS**")

        with pos_col3:
            st.markdown("**Tag**")


        st.divider()


        # POS rows

        for token in doc:

            if token.is_space:
                continue

            col1, col2, col3 = st.columns(
                [2, 2, 2]
            )

            with col1:
                st.write(
                    f"**{token.text}**"
                )

            with col2:
                st.write(
                    token.pos_
                )

            with col3:
                st.write(
                    token.tag_
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "English Grammar Checker • "
    "Python • spaCy • NLP • Streamlit"
)