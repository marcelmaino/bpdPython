import streamlit as st

def insert_google_analytics():
    st.markdown(
        f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-DY8SSHYRR1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', 'G-DY8SSHYRR1');
        </script>
        """,
        unsafe_allow_html=True
    )
