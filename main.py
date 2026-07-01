import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from tools import ASOScraperTool
scrape_app_data = ASOScraperTool()

# Load environment variables (like API keys)
load_dotenv()

from crewai import LLM

# Set up the LLM
llm_instance = None
if os.environ.get("GROQ_API_KEY"):
    import litellm
    original_completion = litellm.completion
    def patched_completion(*args, **kwargs):
        if "messages" in kwargs:
            for msg in kwargs["messages"]:
                if "cache_breakpoint" in msg:
                    del msg["cache_breakpoint"]
        return original_completion(*args, **kwargs)
    litellm.completion = patched_completion

    llm_instance = LLM(model="groq/llama-3.1-8b-instant", api_key=os.environ.get("GROQ_API_KEY"))
elif os.environ.get("GEMINI_API_KEY"):
    llm_instance = LLM(model="gemini/gemini-2.5-flash-lite", api_key=os.environ.get("GEMINI_API_KEY"))
elif os.environ.get("OPENAI_API_KEY"):
    llm_instance = LLM(model="gpt-3.5-turbo", api_key=os.environ.get("OPENAI_API_KEY"))
else:
    print("Warning: No API key found. Please create a .env file and add your GROQ_API_KEY, OPENAI_API_KEY or GEMINI_API_KEY.")

# Define Agents
researcher = Agent(
    role='App Store Optimization (ASO) Researcher',
    goal='Identify trending keywords and analyze competitor app descriptions in the market.',
    backstory='You are an expert market analyst specializing in App Store Optimization. '
              'You know how to extract insights from competitors and find high-volume, low-competition keywords.',
    verbose=True,
    allow_delegation=False,
    llm=llm_instance,
    tools=[scrape_app_data]
)

copywriter = Agent(
    role='ASO Copywriter',
    goal='Write an attractive, high-converting app title and description using the research provided.',
    backstory='You are a master copywriter who specializes in writing compelling marketing copy for apps. '
              'You know how to seamlessly weave in target keywords while keeping the text engaging to users.',
    verbose=True,
    allow_delegation=False,
    llm=llm_instance
)

marketing_strategist = Agent(
    role='Zero-Budget Organic Growth Hacker',
    goal='Generate explosive initial growth for the app using ONLY free, organic traffic channels like TikTok, Shorts, and Communities.',
    backstory='You are a top-tier Organic Growth Hacker. Your expertise lies in launching apps without a marketing budget. You know exactly how to craft viral TikTok/Reels/Shorts scripts, engaging Reddit/Quora posts, and solid zero-budget launch plans to get 1000+ downloads purely organically.',
    verbose=True,
    allow_delegation=False,
    llm=llm_instance
)

ui_ux_designer = Agent(
    role='App Store UI/UX Designer',
    goal='Generate compelling App Store screenshot concepts and design layouts.',
    backstory='You are a top-tier UI/UX Designer with a strong track record of designing App Store screenshots that maximize conversion rates. You know exactly what visual elements and copy to include in each screenshot.',
    verbose=True,
    allow_delegation=False,
    llm=llm_instance
)

def run_aso_process(competitor_app_ids: list, target_niche: str):
    competitors_str = ", ".join(competitor_app_ids)
    
    # Define Tasks
    research_task = Task(
        description=f'1. Analyze the competitor apps with IDs "{competitors_str}" to understand their positioning. Use your tool to scrape data for each app ID separately.\n'
                    f'2. Identify 5-10 high-value keywords for an app in the "{target_niche}" niche.\n'
                    f'3. Summarize the competitors\' strengths and weaknesses in their current app store listings.',
        expected_output='A report containing competitor analysis, a list of 5-10 high-value keywords, and a summary of strengths/weaknesses.',
        agent=researcher
    )

    writing_task = Task(
        description=f'Using the research from the previous task, write a highly optimized ASO copy for a new app in the "{target_niche}" niche.\n'
                    f'Requirements:\n'
                    f'- 3 App Title Options (max 30 characters each)\n'
                    f'- 1 Short Description (max 80 characters)\n'
                    f'- 1 Long Description (using the target keywords naturally, highlighting key features)\n',
        expected_output='A well-formatted document containing 3 Title options, a Short Description, and a Long Description.',
        agent=copywriter
    )

    marketing_task = Task(
        description=f'Using the App Title and Description written by the copywriter, formulate a massive zero-budget organic launch strategy.\n'
                    f'Requirements:\n'
                    f'- Write 3 highly engaging Community Posts (for Reddit, Facebook Groups, or Quora) to drive free traffic without sounding spammy.\n'
                    f'- Write 3 viral video scripts (under 30 seconds each) for TikTok/Instagram Reels/YouTube Shorts.\n'
                    f'- Provide a bulleted 3-day step-by-step Zero-Budget launch plan to achieve 1,000+ downloads organically.',
        expected_output='A full Organic App Launch Marketing Suite document containing Community Posts, Viral Video Scripts, and a Zero-Budget 3-Day Launch Plan.',
        agent=marketing_strategist
    )

    design_task = Task(
        description=f'Using the App Title and Description written by the copywriter, conceptualize the App Store Screenshots.\n'
                    f'Requirements:\n'
                    f'- Provide detailed concepts for 5 App Store screenshots.\n'
                    f'- For each screenshot, specify the main headline text, any subtext, and describe the visual design/layout.\n'
                    f'- The first screenshot should be the most impactful "hero" image.',
        expected_output='A document outlining 5 screenshot concepts with specific copy and design descriptions for each.',
        agent=ui_ux_designer
    )

    # Assemble the Crew
    crew = Crew(
        agents=[researcher, copywriter, marketing_strategist, ui_ux_designer],
        tasks=[research_task, writing_task, marketing_task, design_task],
        process=Process.sequential
    )

    print(f"Starting ASO Crew Process for niche '{target_niche}' against competitors '{competitors_str}'...\n")
    result = crew.kickoff()
    
    # Extract individual task outputs safely
    def get_output(task):
        if hasattr(task, 'output') and task.output is not None:
            if hasattr(task.output, 'raw'):
                return str(task.output.raw)
            return str(task.output)
        return ""
    
    return {
        "aso_copy": get_output(writing_task),
        "marketing": get_output(marketing_task),
        "design": get_output(design_task),
        "full_result": str(result)
    }

if __name__ == "__main__":
    # Example usage for direct testing:
    target_competitors = ['com.adobe.scan.android', 'com.intsig.camscanner']
    niche = 'OCR Scanner'
    
    results = run_aso_process(target_competitors, niche)
    print(results["full_result"])
