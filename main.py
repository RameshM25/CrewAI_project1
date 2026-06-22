# ==========================================
# IMPORTING THE NECESSARY LIBRARIES
# ==========================================
import os
import base64
from dotenv import load_dotenv

from crewai import Agent, Task, LLM
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool
from openai import OpenAI

# Load API keys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# =====================================================
# CUSTOM WRAPPER TO REPLACE DALL-E TOOL
# =====================================================
class OpenAIImageTool(BaseTool):
    name: str = "OpenAI Image Generator"
    description: str = "Generate professional images using OpenAI DALL-E 3 and save them locally."

    def _run(self, prompt: str) -> str:
        client = OpenAI(api_key=OPENAI_API_KEY)
        try:
            result = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024"
            )
            
            image_data = base64.b64decode(result.data[0].b64_json)
            image_path = "linkedin_image.png"
            with open(image_path, "wb") as f:
                f.write(image_data)
                
            return f"Image successfully generated and saved to: {image_path}"
        except Exception as e:
            return f"Failed to generate image. Error: {str(e)}"

# Define Tools
web_search_tool = SerperDevTool()
youtube_search_tool = YoutubeVideoSearchTool()
image_generator_tool = OpenAIImageTool()

# ==========================================
# 1. DEFINE THE BRAIN (OPENAI ONLY)
# ==========================================
main_llm = LLM(model=OPENAI_MODEL)

# ==========================================
# 2. DEFINE AGENTS
# ==========================================
web_research_agent = Agent(
    role="Web Research Agent",
    goal="Gather high-quality, up-to-date insights and trends about {topic}.",
    backstory="You are a Senior Web Research Analyst. You hunt down unique insights, hard statistics, and real-world examples, ignoring generic fluff.",
    tools=[web_search_tool],
    llm=main_llm,
    verbose=True
)

youtube_research_agent = Agent(
    role="YouTube Research Agent",
    goal="Extract actionable frameworks and quotes from top-performing YouTube videos about {topic}.",
    backstory="You are an expert digital media analyst. You dissect videos to find unique perspectives and step-by-step frameworks, completely ignoring filler.",
    tools=[youtube_search_tool], 
    llm=main_llm,
    verbose=True
)

linkedin_post_writer_agent = Agent(
    role="LinkedIn Post Writer Agent",
    goal="Write a viral LinkedIn post about {topic} based on provided research.",
    backstory="You are a top-tier LinkedIn ghostwriter. You write posts with killer hooks, short punchy paragraphs, and a clear takeaway. You never write generic corporate fluff.",
    llm=main_llm,
    skills=["skills/linkedin-branding"],
    verbose=True
)

image_generator_agent = Agent(
    role="Creative Visual Designer",
    goal="Develop a visually striking image prompt based on the LinkedIn post about {topic}.",
    backstory="You are a world-class digital artist. You translate emotional hooks into detailed instructions for AI image generators, focusing on modern, clean aesthetics.",
    tools=[image_generator_tool],
    llm=main_llm,
    verbose=True
)

# ==========================================
# 3. DEFINE TASKS (OPTIONAL URL LOGIC APPLIED)
# ==========================================
web_research_task = Task(
    description="""Topic: {topic}
    Target URLs: {website_urls}
    
    INSTRUCTIONS:
    1. If 'Target URLs' contains actual web links, focus your research ONLY on those specific links (maximum of 3 URLs).
    2. If 'Target URLs' is empty, blank, or says 'None', autonomously search the web to find the top 3 most relevant articles about the Topic.
    3. Do NOT exceed 3 sources in total.
    
    Find the following:
    - 3-5 key insights or trends
    - Interesting statistics or data points
    - Expert opinions or case studies
    Compile the facts into a clear summary.""",
    expected_output="A detailed research brief containing key statistics and core arguments from up to 3 web sources.",
    agent=web_research_agent
)

youtube_research_task = Task(
    description="""Topic: {topic}
    Target Videos: {video_urls}
    
    INSTRUCTIONS:
    1. If 'Target Videos' contains actual YouTube links, analyze ONLY those specific videos (maximum of 3 URLs).
    2. If 'Target Videos' is empty, blank, or says 'None', autonomously search YouTube to find the top 3 most relevant videos about the Topic.
    3. Do NOT exceed 3 videos in total.
    
    Extract the following:
    - The speaker's main argument
    - 3 most valuable takeaways
    - Memorable quotes and actionable tips
    Compile into a summary document.""",
    expected_output="A summary highlighting core takeaways and actionable advice from up to 3 YouTube videos.",
    agent=youtube_research_agent
)

linkedin_post_writer_task = Task(
    description="""Using the research briefs provided, write a highly engaging, viral-style LinkedIn post about {topic}.
    
    CRITICAL BRANDING & FORMATTING RULES:
    1. MANDATORY TAG: Put the exact hashtag #AppePaiBakes at the very bottom.
    2. CTA: End with a highly specific, provocative question.
    3. NO WALLS OF TEXT: Paragraphs must never exceed two sentences.
    4. BANNED WORDS: Do not use Delve, Leverage, Synergize, or Unpack.
    5. LENGTH: Strictly UNDER 200 words. Make it punchy and fast-paced.
    
    General Post requirements:
    - Start with a strong hook
    - Include insights from both research sources
    - Add 2-3 relevant hashtags
    - Max 2-3 emojis in the entire post.""",
    expected_output="A viral LinkedIn post under 200 words, formatting correctly with a specific CTA and the #AppePaiBakes hashtag.",
    agent=linkedin_post_writer_agent,
    context=[web_research_task, youtube_research_task], # <-- FIXED: Passing data via context
    human_input=False
)

image_generator_task = Task(
    description="""Analyze the final LinkedIn post from the writer and create the perfect visual accompaniment for {topic}.
    
    The image should:
    - Visually represent the core theme and emotional hook.
    - Use a professional, clean aesthetic.
    - Contain NO text, letters, or words inside the image.
    
    Generate a detailed prompt and generate the image immediately using the OpenAIImageTool.""",
    expected_output="The URL or file path of the generated image, along with the prompt used.",
    agent=image_generator_agent,
    context=[linkedin_post_writer_task] # <-- FIXED: Passing data via context
)

image_generator_task = Task(
    description="""Analyze the final LinkedIn post from the writer and create the perfect visual accompaniment for {topic}.
    
    The image should:
    - Visually represent the core theme and emotional hook of the post.
    - Use a professional, clean aesthetic.
    - Contain NO text, letters, or words inside the image.
    
    Generate a detailed prompt and generate the image immediately using the OpenAIImageTool.""",
    expected_output="The URL or file path of the generated image, along with the prompt used.",
    agent=image_generator_agent,
    context=[linkedin_post_writer_task]
)
# ==========================================
# 4. DEFINE CREW & KICKOFF FUNCTION
# ==========================================
# ==========================================
# 4. DEFINE CREW & KICKOFF FUNCTION
# ==========================================
from crewai import Crew, Process

def generate_linkedin_post(topic, website_urls="", video_urls=""):
    """
    This function wraps the entire Crew. Streamlit will call this ONCE.
    """
    crew = Crew(
        agents=[
            web_research_agent, 
            youtube_research_agent, 
            linkedin_post_writer_agent, 
            image_generator_agent
        ],
        tasks=[
            web_research_task, 
            youtube_research_task, 
            linkedin_post_writer_task, 
            image_generator_task
        ],
        process=Process.sequential,
        verbose=True
    )

    crew.kickoff(inputs={
        "topic": topic,
        "website_urls": website_urls,
        "video_urls": video_urls
    })

    # Grab the specific outputs from the 3rd and 4th tasks
    return {
        "post": linkedin_post_writer_task.output.raw,
        "image": image_generator_task.output.raw
    }