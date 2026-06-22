import streamlit as st
from main import run_crew

st.set_page_config(page_title="AI LinkedIn Generator", layout="centered")

st.title("🚀 AI LinkedIn Post Generator (CrewAI)")

st.markdown("Generate viral LinkedIn posts using multi-agent AI system")

# Sidebar (clean professional UI)
st.sidebar.header("Inputs")

topic = st.sidebar.text_input("Topic", "Running a Successful Bakery Business")

website_urls = st.sidebar.text_area("Website URL(s)")

video_urls = st.sidebar.text_area("YouTube URL(s)")

# Main action button
generate = st.button("✨ Generate LinkedIn Post")

if generate:

    with st.spinner("🕵️ Web Research Agent is working..."):
        pass

    with st.spinner("📺 YouTube Research Agent is working..."):
        pass

    with st.spinner("✍️ Writing LinkedIn Post..."):
        pass

    with st.spinner("🎨 Generating Image..."):
        result = run_crew(topic, website_urls, video_urls)

    st.success("Done!")

    st.markdown("## 📝 Output")
    st.write(result.raw)

    st.success("Done!")

    # Output section (clean cards style)
    st.subheader("📝 Generated LinkedIn Post")

    st.markdown(
        f"""
        <div style="background-color:#0A66C2;padding:15px;border-radius:10px;color:white">
        {result.raw}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🎨 Image Output")
    st.write(result.raw)