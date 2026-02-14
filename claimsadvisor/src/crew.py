import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchTool
from llama_parse import LlamaParse
from crewai.project import CrewBase, agent, crew, task
import tempfile
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Check for API Key
if not os.getenv("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not found in environment variables.")

llm = init_chat_model(
    model="llama-3.3-70b-versatile", 
    model_provider="groq"
)


@CrewBase
class ClaimsAuditor:
    """
    Executes the Multi-Agent Workflow: 
    OCR -> Extractor Agent -> Auditor Agent -> JSON Output
    """

    agents_config = './config/agents.yaml'
    tasks_config = './config/tasks.yaml'

    @agent
    def info_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_info_extractor'],
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=True
        )


    @agent
    def claims_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['tax_policy_researcher'],
            tools=[
                DuckDuckGoSearchTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
        )

    
    @agent
    def claims_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['claims_auditor'],
            inject_date=True,
            llm=llm,
            allow_delegation=True
        )


    @task
    def data_extraction(self) -> Task:
        return Task(
            config=self.tasks_config['data_extractor'],
            agent=self.info_extractor()
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
            agent=self.claims_auditor()
        )


    @crew
    def claimsresearchercrew(self) -> Crew:
        """Creates the Claims Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=llm,
        )
    


