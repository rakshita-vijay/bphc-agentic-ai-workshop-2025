"""
Task:
Generate an article, based on a 'theme' provided by the user
"""

import importlib.util

import sys

# Check Python version compatibility
if not (sys.version_info >= (3, 10) and sys.version_info < (3, 14)):
  print("Error: CrewAI requires Python >=3.10 and <3.14")
  print(f"Your Python version: {sys.version}")
  sys.exit(1)

import subprocess

# Install CrewAI if missing
try:
  import crewai
except ImportError:
  print("CrewAI not found. Installing...")
  try:
    # Use pip to install CrewAI
    subprocess.check_call([sys.executable, "-m", "pip", "install", "crewai"])
    import crewai
    print("CrewAI installed successfully")
  except subprocess.CalledProcessError as e:
    print(f"Installation failed: {e}")
    sys.exit(1)

# this tells the code to ignore/disregard any warnings that appear
import warnings
warnings.filterwarnings('ignore')

import os
from crewai import Agent, Task, Crew, LLM

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
  raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it as a secret in your GitHub repository. If in command line/terminal, run the command: export GOOGLE_API_KEY='YOUR_API_KEY' ")

llm = LLM(
  model="gemini/gemini-2.0-flash",
  temperature=0.8,                 # or your preferred value
  api_key=GOOGLE_API_KEY
)

# To get the theme of the topics to be decided

topik = os.environ.get("TOPIC")
if not topik:
  topik = input("Enter the topic: ")

print()
print("The topic chosen is: {}".format(topik))

"""
Now, we create the agents.

What all agents are we looking for? We need one agent each for:
- planning, and making a list of theme-related topics
- researching each topic
- generating an article
- collecting the sources used for researching
- fact checking

Total: 6 agents
"""

planner = Agent(
  role = "Topic Planner",
  goal = f"To collect engaging ideas related to the topic: {topik}, addressed to an academic audience",
  backstory = f"You have been given a topic - {topik} - and you must collect many subdivisions related to the topic, for people to use when writing the article. It can be in-depth core subdivisions related to the topic, or informatory subtopics as well. Your work is the basis for the user to write an article (college graduate level) on these subheadings.",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = False
)

researcher = Agent(
  role = "Topic Researcher",
  goal = f"To collect in-depth information (and their sources) on the {topik}-related subtopics provided by the Topic Planner",
  backstory = f"For each subtopic given by the Topic Planner, you will do in-depth research into each, collect information and their source links, and send the links to the Link Collector. Also, you send the relevant informaton you have collected to the Article Generator.",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = True
)

collector = Agent(
  role = "Link Collector",
  goal = "To collect all the links of the material that were used as sources by the Topic Researcher",
  backstory = "You will take all the links from the researcher, and show them to the user at the end of the response under the title: 'Resources Used:'",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = False
)

generator = Agent(
  role = "Article Generator",
  goal = f"Take the structured subtopic outlines from the Topic Planner,curated links and source material from the Link Collector, and score of factual accuracy from the Fact Checker, and write a full-length, polished and engaging article in 500-750 words",
  backstory = "You must write a well-structured, clear article which is at par with college graduates's work, while maintaining cohesion and a formal tone. Also cite key references from the Link Collector. After generating the article, you should consider feedback from the Fact Checker to refine and improve your drafts for final submission.",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = False
)

factchecker = Agent(
  role = "Fact Checker",
  goal = "To verify the factual accuracy of each article produced by the Article Generator using trusted and verifiable sources. Flag any misleading, outdated, or unsupported claims, and suggest accurate replacements wherever needed.",
  backstory = "You are a meticulous fact-checking specialist with expertise in academia and journalism. Your focus is ensuring that every statement made in the generated article aligns with credible, up-to-date sources. You help maintain accuracy and reliability before the article reaches the final compilation stage. Replace outdated or wrong reference links with your own credible sources, if and when a factual error is found.",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = False
)

writer = Agent(
  role = "Final Article Compiler and Formatter",
  goal = f"""To take the subtopics the Topic Planner has generated, give the elaborate article prompt the Article Generator has generated for the same, and then the links the Link Collector has collected for the same topic in the following format:
  # HEADING / TITLE
  1. Introduction
  2. Crticle
  3. Conclusion

  ## Resouces Used:
  1. <exact link here>""",
  backstory = f"The Topic Planner has sent {numberOfTopics} topics to the Topic Researcher, who sent the information to the Article Generator and the research links to the Link Collector, who have all sent their information chunks to you, who orders it and shows it to the user.",
  llm = llm,
  max_iter = 100,
  verbose = False,
  allow_delegation = False
)

"""
role: The role of the agent.
goal: The objective of the agent.
backstory: The backstory of the agent.

knowledge: The knowledge base of the agent.
config: Dict representation of agent configuration.

llm: The language model that will run the agent.

function_calling_llm: The language model that will handle the tool calling for this agent, it overrides the crew function_calling_llm.

max_iter: Maximum number of iterations for an agent to execute a task.

max_rpm: Maximum number of requests per minute for the agent execution to be respected.

verbose: Whether the agent execution should be in verbose mode.
allow_delegation: Whether the agent is allowed to delegate tasks to other agents.

tools: Tools at agents disposal
step_callback: Callback to be executed after each step of the agent execution.
knowledge_sources: Knowledge sources for the agent.
embedder: Embedder configuration for the agent.
"""

"""
Because there are 6 agents, there must be 5 tasks, namely:
- planner : plan
- researcher : research
- collector : collectLinks
- generator : generateArticle
- factchecker: checkFacts
- writer : chunkJoin

## Total: **6** tasks
"""

plan = Task(
  name='Planning',
  agent = planner,
  description = f'''
  1. Identify the latest trends related to {topik}, along with key players and noteworthy news \n
  2. Identify the target audience based on {topik} and collect relevant headlines/topics \n
  3. Develop a {topik}-related title list of {numberOfTopics} items \n
  4. Format the output as a numbered list with no additional commentary \n
  5. Example: \n
    1. Topic One \n
    2. Topic Two \n
    3. Topic Three \n
  6. Send the list to the Topic Researcher''',
  expected_output=f"A {numberOfTopics}-item numbered list of {topik}-related topics with no extra text"
)

"""
agent: Agent responsible for task execution. Represents entity performing task.
<br>async_execution: Boolean flag indicating asynchronous task execution.
<br>callback: Function/object executed post task completion for additional actions.
<br>config: Dictionary containing task-specific configuration parameters.
<br>context: List of Task instances providing task context or input data.
<br>description: Descriptive text detailing task's purpose and execution.
<br>expected_output: Clear definition of expected task outcome.
<br>output_file: File path for storing task output.
<br>output_json: Pydantic model for structuring JSON output.
<br>output_pydantic: Pydantic model for task output.
<br>security_config: Security configuration including fingerprinting.
<br>tools: List of tools/resources limited for task execution.
"""

research = Task(
  name='Researching',
  agent=researcher,
  description=f'''
  For each topic received from the Topic Planner:
  1. Conduct in-depth research on the topic
  2. Use at least 5-6 sources,use  only verified sources if fewer exist use only those
  3. Collect information and and separately list source links
  4. Format research content as:
     Heading: "Research Findings"
     Bullet points with bolded subheadings
  5. Format source links as:
     Heading: "Source Links"
     Numbered list of exact URLs
  6. Example:
     Research Findings
     Key Discovery: Explanation of discovery
     Important Fact: Detailed fact

     Source Links
    1. <exact link here>
    2. <exact link here>
  7. Send the research findings to the Article Generator''',
  expected_output="Structured research findings with exact source links for all topics"
)
linkCollection = Task(
  name='Link Collecting',
  agent=collector,
  description=f'''
  1. Collect all source links from Topic Research
  2. Format as:
     Heading: "Resources Used"
     Numbered list of exact URLs
  3. Preserve original link formatting
  4. Do not modify or shorten URLs
  5. Example:
   Resources Used
    1. https://www.nature.com/articles/bci-technology
    2. https://ieeexplore.ieee.org/document/123456''',
  expected_output="Numbered list of exact source URLs under heading"
)

articleGenerate = Task(
  name='Article Generation',
  agent=generator,
  description=f'''
  1. Receive the structured research content from the Topic Researcher.
  2. Use the research findings and source links to generate a cohesive and well-structured article (400–600 words).
  3. Maintain a formal, academic and accessible tone suitable for college graduates.
  4. Maintain clear section headings and ensure logical flow.
  5. Paraphrase and synthesize information from research — avoid direct copying
  6. Highlight important insights and data points with proper citations.
  7. Example:
     [Topic Name]
     Introduction
    A concise overview of the topic.
     Key Insights
     Summarized and analyzed points.
     Conclusion
    A brief wrap-up with relevance or implications.
  8. Send the generated article to the Fact Checker for feedback.''',

  expected_output="A polished, well-structured markdown article (400–600 words) per topic based on research content."
)

"""
agent: Agent responsible for generating the main article draft using Topic Researcher data.
<br>async_execution: False (sequential task — follows researcher output).
<br>callback: None (evaluation handled by the next agent).
<br>config: Includes tone and structure preferences from Topic Planner.
<br>context: Takes research findings and collected links as input.
<br>description: Defines how to synthesize and write the final article.
<br>expected_output: Markdown-formatted, structured article draft.
<br>tools: LLM model specified in the Agent definition.
"""

factCheck = Task(
    name='Fact Checking',
    agent=factchecker,
    description=f'''
    1. Review each generated article from the Article Generator carefully.
    2. Identify any factual inaccuracies, unsupported claims, or ambiguous data points.
    3. Cross-verify these points using reliable sources such as academic journals, government data, and credible news sites.
    4. For each issue found, provide a correction suggestion and cite the source used for verification.
    5. Repeat this process separately for each topic.
    6. Format your findings as:
        Fact Check Report
         Checked Statement:(quote from article)
         Verdict:(Accurate / Needs Correction)
         Correct Information:(if correction is required)
         Verified Source:(URL)
    7. End with a short summary highlighting the overall factual accuracy rate (e.g., “8 out of 10 statements verified as accurate”).
    8. Send this report internally to the Article Generator for factual refinements.''',
    expected_output="A detailed markdown report highlighting verified facts, correction notes, and accuracy summary per article."
)

# Note: 'chunkJoin' task is mentioned in the crew definition in the original code but not defined.
# I will define it here as the final task in the sequence based on its role in the crew definition.
chunkJoin = Task(
    name='Final Article Compilation and Formatting',
    agent=writer,
    description=f'''
    1. Receive the topics from the Topic Planner, the generated articles from the Article Generator (potentially after fact-checking refinements), and the source links from the Link Collector.
    2. For each topic, compile the generated article text and the corresponding list of source links.
    3. Format the output clearly, presenting each topic's article followed by its resources.
    4. Ensure the final output is well-organized and easy to read.
    5. The final output should present each topic's article and its corresponding source links.
    ''',
    expected_output=f"A compiled and formatted document containing the generated article and source links for each of the {numberOfTopics} topics."
)
crewww = Crew(
  agents = [planner, researcher, collector, generator, factchecker, writer],
  tasks = [plan, research, linkCollection, articleGenerate, factCheck, chunkJoin],
  process = "sequential",
  verbose = False,
  memory = False,
  share_crew = True,
  planning = False,
  chat_llm = llm
)


"""
agents: Ordered list of all agents participating in the workflow.
<br>tasks: Sequential mapping of tasks — each corresponding to an agent.
<br>process: 'sequential' ensures linear execution (Planner → Writer).
<br>verbose: False to suppress LLM token-by-token logging.
<br>memory: Disabled — avoids storing intermediate chat history.
<br>share_crew: True — allows agents to share context and results.
<br>planning: False — bypasses auto-planning (explicit flow control).
<br>chat_llm: Primary LLM used for conversational reasoning and content generation.
"""

from IPython.display import Markdown, display, display_markdown

# now to get and print what the crew has produced

# resp = await crewww.kickoff_async(inputs={"theme": topik, "number of topics": numberOfTopics})
# display(Markdown(resp.raw.strip("`")))

# import asyncio - because shifted above, to the import statements block

def get_downloads_folder():
  downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
  if os.path.isdir(downloads_path):
    pass
  else:
    # making our own path
    os.makedirs(os.path.join(os.path.expanduser("~"), "Downloads"), exist_ok=True)
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

  return downloads_path

downloads_folder = get_downloads_folder()
print("\nDownloads folder is:", downloads_folder)

import asyncio
import datetime
r = datetime.datetime.today()
rn = f"{r.day}-{r.month}-{r.year}_{r.hour}-{r.minute}-{r.second}"

async def main():
  print("\nPreparing setup... ")
  resp = await crewww.kickoff_async(inputs={"theme": topik, "number of topics": numberOfTopics})

  print("\nPrinting the topics collected: \n")
  # If you want to display markdown in a notebook, use display(Markdown(resp.raw.strip("`")))
  # For a .py script, just print the result:
  if resp and resp.raw:
    print(resp.raw)  # or print(resp) if .raw is not available
  else:
    print("No data received from the LLM. Nothing to write.")

  print("\nDownloading the topics collected as a .md file: ")

  file_writer = f"Article_Topic_Generated_{rn}.md"
  fw = os.path.join(downloads_folder, file_writer)

  f = open(fw, 'w')
  f.write(f"# Theme: {topik} \n\n---\n\n")
  f.close()

  f = open(fw, 'a')
  f.write(resp.raw)
  f.close()

  print("\nDownload complete! Check your downloads folder, and happy writing! :)")

if __name__ == "__main__":
  asyncio.run(main())
