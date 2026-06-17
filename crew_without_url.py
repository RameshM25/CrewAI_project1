# ==========================================
# IMPORTING THE NECESSARY LIBRARIES
# ==========================================

import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, Process, LLM
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool

# Load API keys and config from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# Define Tools
web_search_tool = SerperDevTool()
youtube_search_tool = YoutubeVideoSearchTool()


# ==========================================
# 1. DEFINE THE BRAIN USING OPENAI'S FAST, AND CHEAP MODEL
# ==========================================

my_llm = LLM(model=MODEL)

# ==========================================
# 1. DEFINE AGENTS
# ==========================================
web_research_agent = Agent(
    role="Web Research Agent",
    goal="Find the most valuable, up-to-date insights, statistics, and trends about {topic} from top-tier web sources.",
    backstory="""You are a Senior Web Research Analyst who excels at uncovering high-quality, recent information from the internet. You specialize in hunting down unique insights, hard statistics, expert opinions, and real-world examples that make for highly engaging LinkedIn posts. You completely ignore generic corporate fluff, digging deep to find the actual substance that audiences care about.""",
    tools=[web_search_tool],
    llm=my_llm,
    verbose=True
)

youtube_research_agent = Agent(
    role="YouTube Research Agent",
    goal="Extract the most valuable insights, quotes, and actionable frameworks from top-performing YouTube videos about {topic}.",
    backstory="""You are an expert digital media analyst specializing in video content. You excel at dissecting high-performing YouTube videos and extracting the key takeaways that audiences find most valuable. You focus on finding unique perspectives, memorable quotes, step-by-step frameworks, and actionable advice. You expertly capture the speaker's main argument and supporting points, completely ignoring filler and focusing purely on high-impact substance.""",
    tools=[youtube_search_tool], 
    llm=my_llm,
    verbose=True
)

linkedin_post_writer_agent = Agent(
    role="LinkedIn Post Writer Agent",
    goal="Write a viral LinkedIn post about {topic} that gets high engagement and shares based on the insights from the web and YouTube",
    backstory="""You are a top-tier LinkedIn ghostwriter who has written viral posts for tech founders and industry leaders, generating millions of impressions. You know that great LinkedIn posts start with a killer, scroll-stopping hook in the first line. You use short, punchy paragraphs with plenty of white space, tell a compelling story or share a strong opinion, and always end with a clear takeaway or engaging question. You never write generic corporate fluff—every single post has personality, edge, and feels authentically human.""",
    llm=my_llm,
    verbose=True
)

image_generator_agent = Agent(
    role="Creative Visual Designer",
    goal="Develop a visually striking, high-converting image prompt and concept based on the LinkedIn post about {topic}.",
    backstory="""You are a world-class digital artist and social media graphic designer. You understand that a great LinkedIn post needs a powerful visual to stop users from scrolling. You specialize in analyzing written articles or posts, extracting the emotional hook, and translating it into highly descriptive, detailed prompt instructions for AI image generators. You focus on modern, professional, and clean aesthetics, avoiding cheesy stock photo concepts completely.""",
    llm=my_llm,
    verbose=True
)

# ==========================================
# 2. DEFINE TASKS (AUTONOMOUS - NO URLS)
# ==========================================
web_research_task = Task(
    description="""Search the web to find the latest trends, statistics, and news articles related to {topic}. Read and analyze ONLY the top 3 most relevant web pages. 
    Find:
    - 3-5 key insights or trends about this Topic
    - Any interesting statistics or data points
    - Expert opinions or hot takes
    - Real-world examples or case studies
    Compile the most interesting facts into a clear summary.""",
    expected_output="A detailed research brief containing at least 3 strong statistics and 2 unique perspectives on {topic}, sourced from a maximum of 3 articles.",
    agent=web_research_agent
)

youtube_research_task = Task(
    description="""Search YouTube for videos about {topic}. Find and analyze ONLY the top 3 most relevant videos.
    Extract:
    - The speaker's main argument or thesis
    - 3 most valuable takeaways from the videos
    - Any memorable quotes or frameworks mentioned
    - Practical advice or actionable tips shared
    This research will be used to write a LinkedIn post.""",
    expected_output="A summary document highlighting core takeaways, memorable quotes, and actionable advice from exactly 3 YouTube videos on {topic}.",
    agent=youtube_research_agent
)

linkedin_post_writer_task = Task(
    description="""Using the research briefs from the web and YouTube agents, write a highly engaging, viral-style LinkedIn post about {topic}.
    Post requirements:
    - Start with a strong hook (first line should stop the scroll)
    - Keep it between 150-300 words
    - Use short paragraphs (1-2 sentences each)
    - Include insights from both the web search and the video
    - End with a question or call-to-action to drive comments
    - Add 3-5 relevant hashtags at the end
    - Tone: professional but conversational, opinionated, not generic
    Do not use emojis excessively. Max 2-3 emojis in the entire post.""",
    expected_output="A formatted LinkedIn post (under 300 words) with a strong hook, concise paragraphs, emojis, and a clear call-to-action.",
    agent=linkedin_post_writer_agent,
    human_input=True,
    output_file="linkedin_post.md",
    context=[web_research_task, youtube_research_task]
)

image_generator_task = Task(
    description="""Analyze the final LinkedIn post created by the writer. Create a detailed, highly specific visual prompt for an AI image generator (like Midjourney or DALL-E) to create the perfect accompanying image.
    
    Prompt requirements:
    - Specify the core subject and background scene
    - Define the artistic style (e.g., cinematic photography, minimalist vector art, isometric 3D render)
    - Include details about lighting, colors, and mood (e.g., bright and optimistic, moody and dramatic)
    - Specify the aspect ratio for LinkedIn (e.g., aspect ratio 4:5 or 16:9)
    - IMPORTANT: Explicitly state that there should be NO text, letters, or words inside the image (AI image generators struggle with spelling).
    
    The visual concept must perfectly match the tone and hook of the LinkedIn post.""",
    expected_output="Exactly ONE highly descriptive, professional image generation prompt (under 100 words) formatted and ready to be copy-pasted into an AI image generator.",
    agent=image_generator_agent,
    context=[linkedin_post_writer_task]  # <-- This line is crucial!
)
# ==========================================
# 3. DEFINE CREW & KICKOFF
# ==========================================
crew = Crew(
    agents=[web_research_agent, youtube_research_agent, linkedin_post_writer_agent, image_generator_agent],
    tasks=[web_research_task, youtube_research_task, linkedin_post_writer_task, image_generator_task],
    process=Process.sequential
)

# Because our tasks only ask for {topic}, we only provide {topic} here!
result = crew.kickoff(inputs={
    "topic": "AI Agents"
})

print("########################################")
print("✅ SUCCESS! LinkedIn post saved to 'linkedin_post.md'")
print("########################################")
print("🎨 FINAL IMAGE GENERATION PROMPT:")
print(result.raw)