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
if os.environ.get("GEMINI_API_KEY"):
    llm_instance = LLM(model="gemini/gemini-2.5-flash", api_key=os.environ.get("GEMINI_API_KEY"))
elif os.environ.get("OPENAI_API_KEY"):
    llm_instance = LLM(model="gpt-3.5-turbo", api_key=os.environ.get("OPENAI_API_KEY"))
else:
    print("Warning: No API key found. Please create a .env file and add your OPENAI_API_KEY or GEMINI_API_KEY.")

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
    role='App Launch Marketing Strategist',
    goal='Generate explosive initial growth for the app using the ASO copy and niche details.',
    backstory='You are a top-tier Growth Hacker and Marketing Strategist. Your expertise lies in launching apps '
              'and getting 1000+ downloads within the first 3 days. You craft viral TikTok scripts, highly converting '
              'Facebook/Instagram Ads, and solid 3-day launch plans.',
    verbose=True,
    allow_delegation=False,
    llm=llm_instance
)

def run_aso_process(competitor_app_id: str, target_niche: str):
    # Define Tasks
    research_task = Task(
        description=f'1. Analyze the competitor app with ID "{competitor_app_id}" to understand their positioning.\n'
                    f'2. Identify 5-10 high-value keywords for an app in the "{target_niche}" niche.\n'
                    f'3. Summarize the competitor\'s strengths and weaknesses in their current app store listing.',
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
        description=f'Using the App Title and Description written by the copywriter, formulate a massive initial launch strategy.\n'
                    f'Requirements:\n'
                    f'- Write 3 high-converting Ad Copies for Facebook/Instagram.\n'
                    f'- Write 2 viral video scripts (under 30 seconds each) for TikTok/Reels/Shorts influencers.\n'
                    f'- Provide a bulleted 3-day step-by-step launch plan to achieve 1,000+ downloads immediately.',
        expected_output='A full App Launch Marketing Suite document containing Ad Copies, Video Scripts, and a 3-Day Launch Plan.',
        agent=marketing_strategist
    )

    # Assemble the Crew
    crew = Crew(
        agents=[researcher, copywriter, marketing_strategist],
        tasks=[research_task, writing_task, marketing_task],
        process=Process.sequential
    )

    print(f"Starting ASO Crew Process for niche '{target_niche}' against competitor '{competitor_app_id}'...\n")
    result = crew.kickoff()
    
    print("######################")
    print("FINAL ASO RESULT")
    print("######################")
    
    # Safely print to console avoiding UnicodeEncodeError on Windows
    try:
        print(str(result).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    except Exception:
        print("Result generated successfully (printing skipped due to terminal encoding).")
    
    # Save to a file
    with open("aso_results.txt", "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("      ASO COPY (Title, Short & Long Description)  \n")
        f.write("==================================================\n\n")
        f.write(str(writing_task.output.raw if hasattr(writing_task.output, 'raw') else writing_task.output))
        f.write("\n\n\n==================================================\n")
        f.write("      MARKETING LAUNCH SUITE (Ads & Strategy)     \n")
        f.write("==================================================\n\n")
        f.write(str(marketing_task.output.raw if hasattr(marketing_task.output, 'raw') else marketing_task.output))
        
    print("\nResults saved to aso_results.txt")

    # Send result via email if configured
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if receiver_email and sender_email and sender_password:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"ASO Results for {target_niche} App"
            
            msg.attach(MIMEText(str(result), 'plain', 'utf-8'))
            
            # Using Gmail SMTP as default
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            print(f"\nSuccessfully sent the results to {receiver_email}")
        except Exception as e:
            print(f"\nFailed to send email: {e}")
    else:
        print("\nEmail configuration not found in .env. Skipping email delivery.")

if __name__ == "__main__":
    # Example usage:
    # Let's analyze a popular app, e.g., 'com.whatsapp' for a messaging app niche.
    target_competitor = 'com.adobe.scan.android'
    niche = 'OCR Scanner'
    
    run_aso_process(target_competitor, niche)
