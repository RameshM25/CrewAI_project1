# importing the necessary libraries
import os
import base64
from dotenv import load_dotenv

from crewai import Agent, Crew, Task, Process, LLM
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool
from openai import OpenAI  # Added this for the custom tool

# Load API keys and config from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Pull specific models from the .env file
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# =====================================================
# CUSTOM WRAPPER TO REPLACE DALL-ETOOL
# =====================================================
class OpenAIImageTool(BaseTool):
    name: str = "OpenAI Image Generator"
    description: str = (
        "Generate professional images using OpenAI GPT-Image-1 and save them locally."
    )

    def _run(self, prompt: str) -> str:
        client = OpenAI(api_key=OPENAI_API_KEY)
        try:
            # Attempt generation
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1536"
            )
            
            # Save the image locally
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
image_generator_tool = OpenAIImageTool() # Using our custom wrapper instead of DallETool()

# ==========================================
# 1. DEFINE THE BRAIN (OPENAI ONLY)
# ==========================================
main_llm = LLM(model=OPENAI_MODEL)

# ==========================================
# 2. DEFINE AGENTS
# ==========================================
web_research_agent = Agent(
    role="Web Research Agent",
    goal="Find the most valuable, up-to-date insights, statistics, and trends about {topic} from top-tier web sources.",
    backstory="""You are a Senior Web Research Analyst who excels at uncovering high-quality, recent information from the internet. You specialize in hunting down unique insights, hard statistics, expert opinions, and real-world examples that make for highly engaging LinkedIn posts. You completely ignore generic corporate fluff, digging deep to find the actual substance that audiences care about.""",
    tools=[web_search_tool], 
    llm=main_llm,
    verbose=True
)

youtube_research_agent = Agent(
    role="YouTube Research Agent",
    goal="Extract the most valuable insights, quotes, and actionable frameworks from top-performing YouTube videos about {topic}.",
    backstory="""You are an expert digital media analyst specializing in video content. You excel at dissecting high-performing YouTube videos and extracting the key takeaways that audiences find most valuable. You focus on finding unique perspectives, memorable quotes, step-by-step frameworks, and actionable advice. You expertly capture the speaker's main argument and supporting points, completely ignoring filler and focusing purely on high-impact substance.""",
    tools=[youtube_search_tool], 
    llm=main_llm,
    verbose=True
)

linkedin_post_writer_agent = Agent(
    role="LinkedIn Post Writer Agent",
    goal="Write a viral LinkedIn post about {topic} that gets high engagement and shares based on the insights from the web and YouTube",
    backstory="""You are a top-tier LinkedIn ghostwriter who has written viral posts for tech founders and industry leaders, generating millions of impressions. You know that great LinkedIn posts start with a killer, scroll-stopping hook in the first line. You use short, punchy paragraphs with plenty of white space, tell a compelling story or share a strong opinion, and always end with a clear takeaway or engaging question. You never write generic corporate fluff—every single post has personality, edge, and feels authentically human.""",
    llm=main_llm,
    skills=["skills/linkedin-branding"],  
    verbose=True
)

image_generator_agent = Agent(
    role="Creative Visual Designer",
    goal="Develop a visually striking, high-converting image prompt and concept based on the LinkedIn post about {topic}.",
    backstory="""You are a world-class digital artist and social media graphic designer. You understand that a great LinkedIn post needs a powerful visual to stop users from scrolling. You specialize in analyzing written articles or posts, extracting the emotional hook, and translating it into highly descriptive, detailed prompt instructions for AI image generators. You focus on modern, professional, and clean aesthetics, avoiding cheesy stock photo concepts completely.""",
    tools=[image_generator_tool],
    llm=main_llm,
    verbose=True
)

# ==========================================
# 3. DEFINE TASKS (WITH URL PLACEHOLDERS)
# ==========================================
web_research_task = Task(
    description="""Analyze this specific webpage: {website_urls}. 
    Find the following regarding {topic}:
    - 3-5 key insights or trends
    - Any interesting statistics or data points
    - Expert opinions or hot takes
    - Real-world examples or case studies
    Compile the most interesting facts into a clear summary.""",
    expected_output="A detailed research brief containing key statistics and core arguments from the provided webpage.",
    agent=web_research_agent
)

youtube_research_task = Task(
    description="""Analyze this specific YouTube video: {video_urls}. 
    Extract the following regarding {topic}:
    - The speaker's main argument or thesis
    - 3 most valuable takeaways from the video
    - Any memorable quotes or frameworks mentioned
    - Practical advice or actionable tips shared
    This research will be used to write a LinkedIn post.""",
    expected_output="A summary document highlighting core takeaways, memorable quotes, and actionable advice from the provided video.",
    agent=youtube_research_agent
)

linkedin_post_writer_task = Task(
    description="""Using the research briefs from the web and YouTube agents, write a highly engaging, viral-style LinkedIn post about {topic}.
    
    CRITICAL BRANDING & FORMATTING RULES:
    1. THE MANDATORY TAG: You MUST put the exact hashtag #AppePaiBakes at the very bottom of the post.
    2. THE CTA: End with a highly specific, provocative question. NEVER ask generic questions like "What do you think?".
    3. NO WALLS OF TEXT: Paragraphs must never exceed two sentences.
    4. BANNED WORDS: Do not use Delve, Leverage, Synergize, Unpack, or generic conclusions.
    5. LENGTH & TONE: The entire post MUST be strictly between 150 and 200 words. Make it sharp, highly interesting, and concise.
    
    General Post requirements:
    - Start with a strong hook (first line should stop the scroll)
    - Include insights from both the web search and the video
    - Add 2-3 other relevant hashtags alongside the mandatory brand tag
    - Tone: professional but conversational, opinionated, not generic
    - Emojis: Max 2-3 emojis in the entire post.""",
    expected_output="A highly interesting, formatted LinkedIn post strictly between 150-200 words, with a strong hook, concise paragraphs, emojis, a specific CTA, and the #AppePaiBakes hashtag.",
    agent=linkedin_post_writer_agent,
    human_input=True,  
    output_file="linkedin_post.md",
    context=[web_research_task, youtube_research_task]
)

image_generator_task = Task(
    
    description=(
        "Analyze the final LinkedIn post written by the LinkedIn Post Writer Agent. "
        "Create the perfect visual accompaniment to represent the core theme of the post.\n\n"
        "The image should:\n"
        "- Visually represent the core theme and emotional hook of the post regarding: {topic}.\n"
        "- Use a professional, high-quality, and clean aesthetic.\n"
        "- Be formatted in a 4:5 aspect ratio.\n"
        "- IMPORTANT: Contain NO text, letters, or words inside the image.\n"
        "- Be eye-catching enough to stop someone from scrolling.\n\n"
        "Generate a detailed prompt for DALL-E and generate this image immediately using the OpenAIImageTool."
    ),
    expected_output="The URL or file path of the generated image, along with the OpenAIImage prompt that was used to create it.",
    agent=image_generator_agent,
    context=[linkedin_post_writer_task]
)

def run_crew(topic, website_urls, video_urls):
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
        process=Process.sequential
    )

    result = crew.kickoff(inputs={
        "topic": topic,
        "website_urls": website_urls,
        "video_urls": video_urls
    })

    return result