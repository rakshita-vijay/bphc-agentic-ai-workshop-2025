"""
## Task:
Make an article topic generator, based on a 'theme' provided by the user
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

def gen_summary():
  GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
  if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it as a secret in your GitHub repository. If in command line/terminal, run the command: export GOOGLE_API_KEY='YOUR_API_KEY' ")

  llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.8,                 # or your preferred value
    api_key=GOOGLE_API_KEY
  )

  # To get the theme of the topics to be decided
  # theam = input("Enter the theme: ")

  theam = os.environ.get("THEME")
  if not theam:
    theam = input("Enter the theme: ")

  from random import randint
  numberOfTopics = randint(5, 9)

  print()
  print("The theme chosen is: {}".format(theam))
  print("The number of topics that will be generated is: {}".format(numberOfTopics))

  """
  Now, we create the agents.

  What all agents are we looking for? We need one agent each for:
  - planning, and making a list of theme-related topics
  - researching each topic
  - condensing each topic into bullet points
  - collecting the sources used for researching
  - one for writing a small info para about each

  ## Total: **5** agents
  """

  planner = Agent(
    role = "Topic Planner",
    goal = f"To collect {numberOfTopics} engaging topics related to the theme: {theam}, addressed to an academic audience",
    backstory = f"You have been given a theme - {theam} - and you must collect {numberOfTopics} topics related to the theme, for people to write articles about. It can be in-depth core topics related to the theme, or informatory topics as well. Your work is the basis for the user to write an article (college graduate level) on these topics.",
    llm = llm,
    max_iter = 100,
    verbose = False,
    allow_delegation = False
  )

  condenser = Agent(
    role = "Summary Generator",
    goal = f"To condense paragraphs of information into a title-one liner duo and show it to the user",
    backstory = "You will take the information the Topic Researcher, and split it into small chunks - at least 3. Then you will condense it into a bullet point-worth of information and title each of these bullets. The user will elaborate on each point, by themselves, as they see fit. This should be shown to the user under the title 'Condensed Information Points:'",
    llm = llm,
    max_iter = 100,
    verbose = False,
    allow_delegation = False
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

  researcher = Agent(
    role = "Topic Researcher",
    goal = f"To collect in-depth information (and their sources) on the {numberOfTopics} {theam}-related topics provided by the Topic Planner",
    backstory = f"For each topic given by the Topic Planner, you will do in-depth research into each, collect information and their source links, and send the links to the Link Collector. Also, you send the relevant informaton you have collected to the Summary Generator.",
    llm = llm,
    max_iter = 100,
    verbose = False,
    allow_delegation = True
  )

  """```
  role: The role of the agent.
  goal: The objective of the agent.
  backstory: The backstory of the agent.
  ```
  knowledge: The knowledge base of the agent.
  config: Dict representation of agent configuration.
  ```
  llm: The language model that will run the agent.
  ```
  function_calling_llm: The language model that will handle the tool calling for this agent, it overrides the crew function_calling_llm.
  ```
  max_iter: Maximum number of iterations for an agent to execute a task.
  ```
  max_rpm: Maximum number of requests per minute for the agent execution to be respected.
  ```
  verbose: Whether the agent execution should be in verbose mode.
  allow_delegation: Whether the agent is allowed to delegate tasks to other agents.
  ```
  tools: Tools at agents disposal
  step_callback: Callback to be executed after each step of the agent execution.
  knowledge_sources: Knowledge sources for the agent.
  embedder: Embedder configuration for the agent.
  """

  writer = Agent(
    role = "Article Prompt Writer",
    goal = f"To take each topic from the {numberOfTopics} topics the Topic Planner has generated, give the condensed article prompt the Summary Generator has generated for the same, and then the links the Link Collector has collected for the same topic, and repeat the steps for the rest of the topics",
    backstory = f"The Topic Planner has sent {numberOfTopics} topics to the Topic Researcher, who sent the information to the Summary Generator and the research links to the Link Collector, who have all sent their information chunks to you, who orders it and shows it to the user.",
    llm = llm,
    max_iter = 100,
    verbose = False,
    allow_delegation = False
  )

  """
  Because there are 5 agents, there must be 5 tasks, namely:
  - planner : plan
  - condenser : textCondense
  - collector : linkCollection
  - researcher : research
  - writer : chunkJoin

  ## Total: **5** tasks
  """

  plan = Task(
    name='Planning',
    agent = planner,
    description = f'''
    1. Identify the latest trends related to {theam}, along with key players and noteworthy news \n
    2. Identify the target audience based on {theam} and collect relevant headlines/topics \n
    3. Develop a {theam}-related title list of {numberOfTopics} items \n
    4. Format the output as a numbered list with no additional commentary \n
    5. Example: \n
      1. Topic One \n
      2. Topic Two \n
      3. Topic Three \n
    6. Send the list to the Topic Researcher''',
    expected_output=f"A {numberOfTopics}-item numbered list of {theam}-related topics with no extra text"
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
    2. Use at least 5-6 sources
    3. Collect information and source links
    4. Format research content as:
      - Heading: "### Research Findings"
      - Bullet points with bolded subheadings
    5. Format source links as:
      - Heading: "### Source Links"
      - Numbered list of exact URLs
    6. Example:
      ### Research Findings
      - **Key Discovery:** Explanation of discovery
      - **Important Fact:** Detailed fact

      ### Source Links
      1. <exact link here>
      2. <exact link here>
    7. Send the research findings to the Summary Generator''',
    expected_output="Structured research findings with exact source links for all topics"
  )

  textCondense = Task(
    name='Condensing',
    agent=condenser,
    description=f'''
    1. Receive research content from Topic Researcher
    2. For each logical chunk:
      a. Create a bolded heading (1-3 words)
      b. Add colon followed by 1-sentence summary
    3. Output as:
      - Heading: "### Condensed Information Points"
      - Bullet points with headings
    4. Do not add commentary
    5. Example:
    ### Condensed Information Points
    - **Brain-Computer Interface:** Direct pathway between brain and external devices
    - **Neural Signals:** BCIs interpret signals to control computers''',
    expected_output = "Markdown section with bolded headings and colon-separated summaries"
  )

  linkCollection = Task(
    name='Link Collecting',
    agent=collector,
    description=f'''
    1. Collect all source links from Topic Researcher
    2. Format as:
      - Heading: "### Resources Used"
      - Numbered list of exact URLs
    3. Preserve original link formatting
    4. Do not modify or shorten URLs
    5. Example:
    ### Resources Used
      1. https://www.nature.com/articles/bci-technology
      2. https://ieeexplore.ieee.org/document/123456''',
    expected_output="Numbered list of exact source URLs under heading"
  )

  chunkJoin = Task(
    name='Joining, Formatting, and Writing',
    agent=writer,
    description=f'''
    For each of the {numberOfTopics} topics:
    1. Start with H2 heading: "## [Topic Name]"
    2. Include condensed points from Summary Generator
    3. Include resource links from Link Collector
    4. Maintain exact formatting:
      ## Topic <Number>: <Topic Title>
      ### Condensed Information Points
      - **heading:** summary (from condenser / Summary Generator)
      ### Resources Used
      1. <exact link here>
    5. Do not add commentary or summaries''',
    expected_output=f"Structured output with headings, bullet points, and exact links for all topics"
  )

  # forming the crew
  crewww = Crew(
    agents = [planner, researcher, condenser, collector, writer],
    tasks = [plan, research, textCondense, linkCollection, chunkJoin],
    process = "sequential",
    verbose = False,
    memory = False,
    share_crew = True,
    planning = False,
    chat_llm = llm
  )

  """
  tasks: List of tasks assigned to the crew.
  <br>agents: List of agents part of this crew.
  <br>manager_llm: The language model that will run manager agent.
  <br>manager_agent: Custom agent that will be used as manager.
  <br>memory: Whether the crew should use memory to store memories of it's execution.
  <br>memory_config: Configuration for the memory to be used for the crew.
  <br>cache: Whether the crew should use a cache to store the results of the tools execution.
  <br>function_calling_llm: The language model that will run the tool calling for all the agents.
  <br>process: The process flow that the crew will follow (e.g., sequential, hierarchical).
  <br>verbose: Indicates the verbosity level for logging during execution.
  <br>config: Configuration settings for the crew.
  <br>max_rpm: Maximum number of requests per minute for the crew execution to be respected.
  <br>prompt_file: Path to the prompt json file to be used for the crew.
  <br>id: A unique identifier for the crew instance.
  <br>task_callback: Callback to be executed after each task for every agents execution.
  <br>step_callback: Callback to be executed after each step for every agents execution.
  <br>share_crew: Whether you want to share the complete crew information and execution with crewAI to make the library better, and allow us to train models.
  <br>planning: Plan the crew execution and add the plan to the crew.
  <br>chat_llm: The language model used for orchestrating chat interactions with the crew.
  <br>security_config: Security configuration for the crew, including fingerprinting.
  """

  from IPython.display import Markdown, display, display_markdown

  print("\nPreparing setup... ")
  resp = crewww.kickoff(inputs={"theme": theam, "number of topics": numberOfTopics})

  print("\nPrinting the article: \n")
  # If you want to display markdown in a notebook, use display(Markdown(resp.raw.strip("`")))
  # For a .py script, just print the result:
  if resp:
    print(resp)  # or print(resp) if .raw is not available
  else:
    print("No data received from the LLM. Nothing to write.")

  print("\nDownloading the article as a .md file: ")

  from _101_download_to_device import find_downloads_folder

  downloads_folder = find_downloads_folder()
  print("\nDownloads folder is:", downloads_folder)

  import datetime
  r = datetime.datetime.today()
  rn = f"{r.day}-{r.month}-{r.year}_{r.hour}-{r.minute}-{r.second}"

  file_writer = f"Article_Topic_Generated_{rn}.md"
  fw = os.path.join(downloads_folder, file_writer)

  f = open(fw, 'w')
  hyphens = "-" * len(f"# Theme: {theam}")
  f.write(f"# Theme: {theam} \n\n{hyphens}\n\n")
  f.close()

  f = open(fw, 'a')
  f.write(resp.raw)
  f.close()

  print("\nDownload complete! Check your downloads folder, and happy writing! :)")

if __name__ == "__main__":
  gen_summary()
