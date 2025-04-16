from weasyprint import HTML
from markdown2 import markdown
import tempfile
import os

class PDFGenerator:
    def __init__(self):
        self.css = '''
        @page { margin: 2cm; }
        body { font-family: Arial; line-height: 1.6; }
        h1 { font-size: 22pt; }
        h2 { font-size: 18pt; margin-top: 15px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; }
        .metadata { font-size: 10pt; color: #666; }
        '''

    def generate_pdf(self, markdown_content: str, output_path: str = None):
        """Convert markdown content to styled PDF report"""
        html = markdown(markdown_content, extras=['tables'])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            f.write(html.encode('utf-8'))
            temp_html = f.name

        pdf_output = output_path or f'research_report_{os.getpid()}.pdf'
        HTML(filename=temp_html).write_pdf(
            pdf_output,
            stylesheets=[self.css],
            presentational_hints=True
        )
        
        os.unlink(temp_html)
        return pdf_output