import os
import re
import uuid
import tempfile
from datetime import datetime
from colorpaws import ColorPaws
from google import generativeai as genai
from markdown_pdf import MarkdownPdf, Section

class KhutbahMaker:
    """Copyright (C) 2025 Ikmal Said. All rights reserved"""
    
    def __init__(self, mode='default', api_key=None, model='gemini-2.0-flash-thinking-exp-01-21'):
        """
        Initialize KhutbahMaker module.
        
        Parameters:
            mode (str): Startup mode ('default', 'webui', or 'api')
            api_key (str): API key for AI services
            model (str): AI model to use
        """
        self.logger = ColorPaws(name=self.__class__.__name__, log_on=True, log_to=None)
        self.aigc_model = model
        self.api_key = api_key
        
        self.logger.info("KhutbahMaker is ready!")
        
        if mode != 'default':
            if mode == 'webui':
                self.start_wui()
            else:
                raise ValueError(f"Invalid startup mode: {mode}")

    def __clean_markdown(self, text):
        """Clean up markdown text"""
        text = re.sub(r'```[a-zA-Z]*\n', '', text)
        text = re.sub(r'```\n?', '', text)
        return text.strip()

    def __generate_khutbah(self, topic, length, tone, language, task_id):
        """Generate khutbah content using AI"""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            
            self.logger.info(f"[{task_id}] Generating khutbah on topic: {topic}")
            
            # Create prompt based on parameters
            prompt = f"""You are an expert Islamic scholar tasked with writing a {length} Friday khutbah (sermon) in {language} on the topic: {topic} with tone: {tone}. Create a complete, well-structured Islamic khutbah that includes: 1. An appropriate title 2. Opening with praise to Allah and salutations on Prophet Muhammad (peace be upon him) 3. Introduction to the topic with relevant Quranic verses and Hadith 4. Main body with clear points, explanations, and guidance 5. Practical advice for the audience 6. Conclusion with a summary of key points 7. Closing duas (prayers) The khutbah should be scholarly yet accessible, with proper citations of Quranic verses and authentic Hadith. Format in Markdown with appropriate headings, paragraphs, and emphasis. For Arabic text, include both Arabic script and transliteration where appropriate."""

            model = genai.GenerativeModel(self.aigc_model)
            response = model.generate_content(prompt)
            
            return self.__clean_markdown(response.text)

        except Exception as e:
            self.logger.error(f"[{task_id}] Khutbah generation failed: {str(e)}")
            return None

    def __khutbah_to_pdf(self, markdown_text, topic, language, task_id):
        """Convert khutbah markdown to PDF"""
        try:
            clean_topic = re.sub(r'[^\w\-]', '_', topic)
            clean_filename = f"{clean_topic}_khutbah_{language.lower().replace(' ', '_')}"
            pdf_path = os.path.join(tempfile.gettempdir(), f"{clean_filename}.pdf")
            
            self.logger.info(f"[{task_id}] Generating Khutbah PDF: {pdf_path}")
            pdf = MarkdownPdf(toc_level=3)
            
            # Add main content section with custom CSS
            css = """            
            body {
                font-family: 'Amiri', 'Segoe UI', sans-serif;
                text-align: justify;
                text-justify: inter-word;
                line-height: 1.5;
            }
            
            /* Arabic text specific */
            [lang='ar'] {
                direction: rtl;
                font-family: 'Amiri', serif;
                font-size: 1.6em;
                line-height: 1.8;
            }
            
            h1 {
                text-align: center;
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
                font-size: 1.5em;
                font-weight: 600;
            }
            
            h2, h3, h4, h5, h6 {
                color: #34495e;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
            }
            
            blockquote {
                background-color: #f9f9f9;
                border-left: 4px solid #4CAF50;
                padding: 10px 15px;
                margin: 15px 0;
                font-style: italic;
            }
            
            p {
                margin: 0.8em 0;
            }
            """
            
            # Add the main content section
            main_section = Section(markdown_text, toc=True)
            pdf.add_section(main_section, user_css=css)
            
            # Ensure the content starts with a level 1 header
            if not markdown_text.startswith('# '):
                title = f"Khutbah on {topic}"
                markdown_text = f"# {title}\n\n{markdown_text}"
            
            # Set PDF metadata with Unicode support
            pdf.meta["title"] = title
            pdf.meta["subject"] = f"Islamic Khutbah on {topic}"
            pdf.meta["author"] = "Ikmal Said"
            pdf.meta["creator"] = "KhutbahMaker"
            
            # Save the PDF
            pdf.save(pdf_path)
            return pdf_path

        except Exception as e:
            self.logger.error(f"[{task_id}] Khutbah PDF generation failed: {str(e)}")
            return None

    def __get_taskid(self):
        """
        Generate a unique task ID for request tracking.
        Returns a combination of timestamp and UUID to ensure uniqueness.
        Format: YYYYMMDD_HHMMSS_UUID8
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uuid_part = str(uuid.uuid4())[:8]
        task_id = f"{timestamp}_{uuid_part}"
        return task_id
    
    def generate_khutbah(self, topic, length="Short", tone="Inspirational", language="Bahasa Malaysia"):
        """Generate an Islamic khutbah based on specified parameters.
        
        Parameters:
            topic (str): The main topic or theme of the khutbah
            length (str): Desired length ('Short' | 'Long')
            tone (str): Tone of the khutbah ('Scholarly' | 'Inspirational' | 'Practical' | 'Reflective' | 'Motivational' | 'Educational' | 'Historical' | 'Narrative')
            language (str): Target language ('Bahasa Malaysia' | 'Arabic' | 'English' | 'Mandarin' | 'Tamil')
        """
        if not topic or topic == "":
            self.logger.error("Topic is required!")
            return None, None
        
        task_id = self.__get_taskid()
        self.logger.info(f"[{task_id}] Khutbah generation started!")
        
        try:           
            markdown_text = self.__generate_khutbah(topic, length, tone, language, task_id)
            if not markdown_text:
                return None, None

            pdf_file = self.__khutbah_to_pdf(markdown_text, topic, language, task_id)
            if not pdf_file:
                return None, None
            
            self.logger.info(f"[{task_id}] Khutbah generation complete!")
            return pdf_file, markdown_text
            
        except Exception as e:
            self.logger.error(f"[{task_id}] Khutbah generation failed: {str(e)}")
            return None, None
        
    def start_wui(self, host: str = "0.0.0.0", port: int = 5488, browser: bool = True,
                  upload_size: str = "4MB", public: bool = False, limit: int = 10):
        """
        Start Citrailmu WebUI with all features.
        
        Parameters:
        - host (str): Server host (default: "0.0.0.0")
        - port (int): Server port (default: 5488) 
        - browser (bool): Launch browser automatically (default: True)
        - upload_size (str): Maximum file size for uploads (default: "4MB")
        - public (bool): Enable public URL mode (default: False)
        - limit (int): Maximum number of concurrent requests (default: 10)
        """
        from .webui import KhutbahMakerWebUI
        KhutbahMakerWebUI(self, host=host, port=port, browser=browser,
                          upload_size=upload_size, public=public, limit=limit)