import streamlit as st
from main import generate_linkedin_post

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CrewAI LinkedIn Generator",
    layout="centered"
)

# =========================
# HEADER
# =========================
st.title("🧠 Autonomous LinkedIn Generator")
st.caption("Multi-agent AI system: Research → Writing → Image Generation")

# =========================
# INPUT SECTION
# =========================
topic = st.text_input("🎯 Topic", "Agentic AI")

st.info("💡 **Pro Tip:** Leave the URLs blank to let the AI search autonomously, or paste specific links to force the AI to read them.")

website_urls = st.text_area("🌐 Website URL(s) (Optional)")
video_urls = st.text_area("📺 YouTube URL(s) (Optional)")

# =========================
# RUN BUTTON
# =========================
if st.button("🚀 Generate Content"):

    with st.spinner("🧠 AI Agents are researching and writing... check your terminal for live updates!"):
        # Returns our dictionary containing ["post"] and ["image"]
        result_dict = generate_linkedin_post(topic, website_urls, video_urls)

    st.success("✅ Generation Complete!")

    # =========================
    # OUTPUT SECTION
    # =========================
    st.subheader("📝 LinkedIn Post")

    st.markdown(
        f"""
        <div style="
            background-color:#0A66C2;
            padding:20px;
            border-radius:10px;
            color:white;
            font-size:16px;
            line-height:1.6;
        ">
        {result_dict["post"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🎨 Image Generation Result")
    st.info(result_dict["image"])