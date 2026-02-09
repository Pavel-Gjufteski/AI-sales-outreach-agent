# AI Outreach Agent for Meeting Generation

An automated AI-powered research agent that analyzes company websites, assesses their fit for AI services, and generates personalized outreach content (emails and LinkedIn messages) to book meetings. The agent uses advanced web scraping, AI analysis, and PDF report generation to streamline your sales outreach process.

For a full video walkthrough, visit: https://www.loom.com/share/feb40eca732e4ea9b24406d68ed85fb7

## Features

- **Intelligent Web Scraping**: Uses Selenium to fetch and parse company websites, handling JavaScript-rendered content
- **LinkedIn Profile Discovery**: Automatically extracts LinkedIn profile URLs from company websites
- **AI-Powered Analysis**: Leverages OpenAI GPT-4o-mini to:
  - Analyze company products, services, and industry
  - Assess fit for AI services (specifically FermanIQ)
  - Identify company pain points
  - Generate personalized outreach content
- **Automated Outreach Generation**: Creates ready-to-use:
  - Email subject lines
  - Email content with Calendly links
  - LinkedIn messages with Calendly links
- **Professional PDF Reports**: Generates formatted PDF documents with all research findings and outreach content
- **Structured Output**: Returns structured JSON data for easy integration

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed (for Selenium)
- OpenAI API key
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-Outreach-Agent-for-Meeting-Generation
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Configuration

The agent is configured for **FermanIQ** by default, which builds custom AI agents that automate workflows, improve productivity, and create real business impact using chatbots, agentic workflows, and RAG systems.

To customize for your own company:
1. Edit the prompt template in `prompt.py` (lines 60-62)
2. Update the Calendly link in `prompt.py` (line 58) with your own scheduling link

## Usage

1. **Activate your virtual environment** (if not already activated)

2. **Run the main script**:
   ```bash
   python main.py
   ```

3. **Enter a company website URL** when prompted:
   ```
   Enter the company website URL (e.g., https://example.com):
   ```
   You can enter URLs with or without `https://` - the script will handle it automatically.

4. **Wait for processing**:
   - The script will fetch the website using Selenium
   - Extract LinkedIn profiles
   - Analyze the company using AI
   - Generate outreach content
   - Create a PDF report

5. **Review the output**:
   - JSON output will be displayed in the console
   - LinkedIn profiles found will be listed
   - PDF report will be saved in the `output/` directory

## Project Structure

```
AI-Outreach-Agent-for-Meeting-Generation/
│
├── main.py                 # Main entry point
├── scrape.py               # Web scraping functions (Selenium, BeautifulSoup)
├── prompt.py               # AI prompt templates and LLM integration
├── pdf_converter.py        # PDF report generation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
└── output/                # Generated PDF reports (created automatically)
    └── CompanyName_YYYYMMDD_HHMMSS.pdf
```

## How It Works

1. **Web Scraping** (`scrape.py`):
   - Uses Selenium with headless Chrome to fetch website content
   - Extracts visible text while removing scripts, styles, and navigation elements
   - Finds and extracts LinkedIn profile URLs

2. **AI Analysis** (`prompt.py`):
   - Sends website content to OpenAI GPT-4o-mini
   - Analyzes company information, industry, and products/services
   - Determines fit for AI services
   - Generates personalized outreach content

3. **PDF Generation** (`pdf_converter.py`):
   - Creates professional PDF reports using ReportLab
   - Includes all research findings and outreach content
   - Saves files with timestamps in the `output/` directory

## Dependencies

- **langchain** (1.2.3) - LLM framework
- **langchain-openai** (1.1.7) - OpenAI integration
- **openai** (2.15.0) - OpenAI API client
- **selenium** - Web scraping
- **webdriver-manager** - ChromeDriver management
- **beautifulsoup4** (4.14.3) - HTML parsing
- **reportlab** (4.2.5) - PDF generation
- **python-dotenv** (1.2.1) - Environment variable management
- **requests** (2.32.5) - HTTP requests

## Output Format

The agent returns an `AgentOutput` object with the following fields:

- `fit_for_outreach` (bool): Whether the company is a good fit
- `company_name` (str): Company name
- `company_website` (str): Website URL
- `company_industry` (str): Industry classification
- `company_products_or_services` (str): Products/services description
- `company_linkedin` (str): LinkedIn company page URL
- `company_painpoints` (str): Identified pain points
- `email_subject` (str): Generated email subject line
- `email_content` (str): Generated email body (includes Calendly link)
- `linkedin_message` (str): Generated LinkedIn message (includes Calendly link)
- `reasoning` (str): Explanation of fit assessment

## Troubleshooting

**ModuleNotFoundError**  
If you encounter import errors, ensure your virtual environment is activated and all dependencies are installed: `pip install -r requirements.txt`

**ChromeDriver Issues**  
ChromeDriver is automatically managed by `webdriver-manager`. Ensure Chrome browser is installed and up to date. If issues persist, manually install ChromeDriver and add it to your PATH.

**OpenAI API Errors**  
Verify your API key is set in the `.env` file, check your OpenAI account has sufficient credits, and ensure the API key has access to the GPT-4o-mini model.

**PDF Generation Errors**  
Ensure the `output/` directory is writable and that `reportlab` is properly installed.

---

**Note**: This agent is specifically configured for FermanIQ's AI services. Modify the prompt template in `prompt.py` to customize for your own use case.