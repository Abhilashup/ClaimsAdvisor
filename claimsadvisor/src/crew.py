import os
import logging
import time
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from crewai_tools import SerperDevTool
from llama_parse import LlamaParse
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from src.models import ExtractedData, FinalAuditReport

# Initialize the search tool once to avoid repeated overhead
search_tool = SerperDevTool()

@tool("brave_search")
def brave_search(query: str) -> str:
    """Useful to search the internet for Indian tax policies, limits, and HRA rules."""
    return search_tool.run(search_query=query)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Check for API Key
if not os.getenv("GROQ_API_KEY"):
    logger.warning("GROQ_API_KEY not found in environment variables.")

# Consolidate into one LLM
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.1
)


@CrewBase
class ClaimsAuditor:
    """
    Executes the Multi-Agent Workflow: 
    OCR -> Extractor Agent -> Auditor Agent -> Structured Output
    """

    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'

    @agent
    def info_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_info_extractor'],
            verbose=True, 
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=False,
            max_rpm=10 # Rate limit for Groq
        )


    @agent
    def claims_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['tax_policy_researcher'],
            verbose=True, 
            tools=[
                brave_search
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=False, 
            max_iter=3, 
            max_rpm=10 
        )

    
    @agent
    def claims_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['claims_auditor'],
            verbose=True, 
            inject_date=True,
            llm=llm,
            allow_delegation=False, 
            max_rpm=10 
        )


    @task
    def data_extraction(self) -> Task:
        return Task(
            config=self.tasks_config['data_extractor'],
            agent=self.info_extractor(),
            output_pydantic=ExtractedData # Force structured output
        )
    
    @task
    def task_researcher(self) -> Task:
        return Task(
            config=self.tasks_config['task_researcher'],
            agent=self.claims_researcher()
        )


    @task
    def claims_auditing(self) -> Task:
        return Task(
            config=self.tasks_config['claims_auditor'],
            agent=self.claims_auditor(),
            output_pydantic=FinalAuditReport # Force structured output
        )


    @crew
    def claimsresearchercrew(self) -> Crew:
        """Creates the Claims Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=False,
            memory=True, # Enable memory to reduce repeated tasks
            cache=True, # Enable caching
            step_callback=lambda step: time.sleep(10) # Reduced from 15 as max_rpm handles most of it
        )



    


