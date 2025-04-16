import argparse
from research import ResearchModule
from dotenv import load_dotenv

load_dotenv()
from database import init_db, safe_commit
from database import ResearchDataDB, ReportFragmentDB, SessionContextDB
from datetime import datetime

class AISystem:
    def __init__(self):
        self.db_session = init_db()
        self.research_module = ResearchModule()
        
    async def run(self, query: str):
        print(f"Starting research on: {query}")
        # Initialize research pipeline
        self.research_module.setup_agents()
        
        # Execute research pipeline
        research_results = await self.research_module.execute_research(query)
        
        # Generate structured content
        report_content = await self.research_module.generate_content(research_results)
        
        # Validate and refine output
        validated_content = self.research_module.perform_quality_checks(report_content)
        
        # Save to database
        try:
            self.db_session.add(ResearchDataDB(
                source_url=query,
                extracted_content=str(research_results),
                credibility_score=0.9,
                freshness=datetime.now(),
                topics=[]
            ))
            if not safe_commit(self.db_session):
                raise Exception("Database commit failed")
        finally:
            self.db_session.remove()
        
        # Generate final report
        self.generate_markdown_report(validated_content['content'])

    def generate_markdown_report(self, content: str):
        """Generate structured Markdown report from validated content"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.md"
            
            report = (
                f"# Research Report\n\n"
                f"## Executive Summary\n{content['content'].get('summary', '')}\n\n"
                f"## Key Findings\n{content['content'].get('findings', '')}\n\n"
                f"## Methodology\n{content['content'].get('methodology', '')}\n\n"
                f"## References\n{'- ' + '\n- '.join(content['content'].get('references', []))}"
            )
            
            with open(filename, "w") as f:
                f.write(report)
            print(f"Report generated at {filename}")
        except Exception as e:
            print(f"Report generation failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Research System')
    parser.add_argument('--query', type=str, required=True, help='Research topic')
    args = parser.parse_args()
    
    system = AISystem()
    import asyncio
    asyncio.run(system.run(args.query))