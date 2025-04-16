from crewai import Agent, Task, Crew, Process
from crewai_tools import SeleniumScrapingTool
import os
import google.generativeai as genai
from data_models import ResearchData
from database import SessionContextDB
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class ResearchModule:
    def __init__(self):
        self.session = SessionContextDB()
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.selenium_tool = SeleniumScrapingTool()
        self.llm = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            generation_config=genai.GenerationConfig(temperature=0.3)
        )

    def setup_agents(self):
        """Initialize CrewAI agents with detailed prompts"""
        # Core research team
        self.research_coordinator = Agent(
            role='Research Coordinator',
            goal='Oversee comprehensive research process ensuring quality and relevance',
            backstory="""Expert in managing research projects with strong organizational skills.
            Skilled in breaking down complex questions into actionable research tasks.""",
            llm=self.llm,
            verbose=True
        )

        self.web_researcher = Agent(
            role='Advanced Web Researcher',
            goal='Extract content from JS-heavy sites using advanced browser automation',
            backstory="""Expert in scraping modern web applications using headless browsers.
            Specializes in handling JavaScript-rendered content and complex site structures.""",
            tools=[self.selenium_tool],
            llm=self.llm,
            verbose=True
        )

        self.content_strategist = Agent(
            role='Content Strategy Expert',
            goal='Transform research findings into well-structured, publication-ready content',
            backstory="""Award-winning technical writer with expertise in creating
            comprehensive research reports and executive summaries.""",
            llm=self.llm,
            verbose=True
        )

        self.quality_analyst = Agent(
            role='Web Research Specialist',
            goal='Gather accurate and relevant information from web sources',
            backstory="""Seasoned internet researcher with expertise in finding
            reliable sources and extracting key information efficiently.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )

        self.data_analyst = Agent(
            role='Data Analysis Expert',
            goal='Transform raw data into meaningful insights',
            backstory="""Analytical thinker with strong background in data interpretation
            and pattern recognition.""",
            llm=self.llm,
            verbose=True
        )

    def create_research_tasks(self, query):
        """Define research workflow tasks"""
        return [
            Task(
                description=f"""Break down the research topic: {query}
                into specific sub-questions and research objectives""",
                agent=self.research_coordinator,
                expected_output='Clear research plan with specific questions to investigate'
            ),
            Task(
                description="""Conduct thorough web research using available resources
                to gather relevant information""",
                agent=self.web_researcher,
                expected_output='Comprehensive research findings with source references',
                context=[self.research_coordinator]
            ),
            Task(
                description="""Analyze collected data and identify key patterns,
                insights, and relationships""",
                agent=self.data_analyst,
                expected_output='Detailed analysis report with clear insights and data visualizations',
                context=[self.web_researcher]
            )
        ]

    async def execute_research(self, query: str):
        """Execute full research workflow using CrewAI"""
        self.setup_agents()
        research_crew = Crew(
            agents=[
                self.research_coordinator,
                self.web_researcher,
                self.data_analyst
            ],
            tasks=self.create_research_tasks(query),
            process='sequential',
            verbose=2
        )

        return await research_crew.kickoff(inputs={'query': query})

    async def generate_content(self, research_data):
        """Generate structured report content"""
        report_structure = await self.writing_agent.outline_report()
        structured_content = {
            'summary': await self.writing_agent.write_summary(research_data),
            'findings': await self.writing_agent.write_findings(research_data),
            'methodology': await self.writing_agent.write_methodology(),
            'references': await self.writing_agent.collect_sources(research_data)
        }
        return {'content': structured_content}

    def perform_quality_checks(self, content):
        """Validate content quality"""
        checker = self.QualityChecker()
        return checker.validate(
            content,
            checks=[
                "source_diversity", 
                "citation_integrity",
                "content_coverage",
                "argument_structure"
            ]
        )

    class QualityChecker:
        def validate(self, content, checks):
            # Implement PRD quality checks
            issues = []
            
            if 'citation_integrity' in checks:
                if not self._validate_citations(content['references']):
                    issues.append('Missing required citations')
            
            if 'statistical_significance' in checks:
                if not self._check_stats(content['findings']):
                    issues.append('Insufficient statistical data')
            
            return {
                'status': 'approved' if not issues else 'revisions_needed',
                'issues': issues,
                'content': content
            }
        
        def _validate_citations(self, references):
            return len(references) >= 20  # PRD requirement
        
        def _check_stats(self, findings):
            return any(isinstance(d, (int, float)) for d in findings)

    # Add Report Writer agent with dynamic prompts
    def setup_agents(self):
        """Initialize CrewAI agents with detailed prompts"""
        # Core research team
        self.research_coordinator = Agent(
            role='Research Coordinator',
            goal='Oversee comprehensive research process ensuring quality and relevance',
            backstory="""Expert in managing research projects with strong organizational skills.
            Skilled in breaking down complex questions into actionable research tasks.""",
            llm=self.llm,
            verbose=True
        )

        self.web_researcher = Agent(
            role='Advanced Web Researcher',
            goal='Extract content from JS-heavy sites using advanced browser automation',
            backstory="""Expert in scraping modern web applications using headless browsers.
            Specializes in handling JavaScript-rendered content and complex site structures.""",
            tools=[self.selenium_tool],
            llm=self.llm,
            verbose=True
        )

        self.content_strategist = Agent(
            role='Content Strategy Expert',
            goal='Transform research findings into well-structured, publication-ready content',
            backstory="""Award-winning technical writer with expertise in creating
            comprehensive research reports and executive summaries.""",
            llm=self.llm,
            verbose=True
        )

        self.quality_analyst = Agent(
            role='Web Research Specialist',
            goal='Gather accurate and relevant information from web sources',
            backstory="""Seasoned internet researcher with expertise in finding
            reliable sources and extracting key information efficiently.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )

        self.data_analyst = Agent(
            role='Data Analysis Expert',
            goal='Transform raw data into meaningful insights',
            backstory="""Analytical thinker with strong background in data interpretation
            and pattern recognition.""",
            llm=self.llm,
            verbose=True
        )

        self.report_writer = Agent(
            role='Pulitzer-grade Journalist',
            goal=f"""Create comprehensive reports that:
            1. Start with executive summary
            2. Follow inverted pyramid structure
            3. Include 5+ perspectives
            4. Maintain academic rigor
            5. Use Markdown formatting""",
            backstory="Award-winning writer with 20+ years investigative experience",
            llm=self.llm,
            verbose=True
        )
    async def crawl(self, url):
        try:
            # First attempt: Selenium for JS-heavy sites
            js_content = await self.selenium_tool.scrape(url)
            soup = BeautifulSoup(js_content, 'html.parser')
        except Exception as e1:
            try:
                # Fallback 1: Standard requests
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e2:
                try:
                    # Fallback 2: Alternative parser
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url)
                        soup = BeautifulSoup(response.text, 'html.parser')
                except Exception as e3:
                    return {'error': f"All parsers failed: {e1}, {e2}, {e3}"}
        
        # Existing metadata and storage logic
        encrypted_data = self._encrypt_data({
            'content': soup.get_text(),
            'metadata': {
                'headers': dict(response.headers),
                'timestamp': datetime.now().isoformat()
            }
        })
        return encrypted_data

    def _encrypt_data(self, data):
        # Placeholder for encryption implementation
        return data

    def store_research(self, data: ResearchData):
        encrypted_data = self._encrypt_data(data.dict())
        self.session.add(encrypted_data)
        self.session.commit()