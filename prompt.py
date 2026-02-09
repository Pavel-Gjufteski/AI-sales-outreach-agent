from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import re

from scrape import fetch_html_with_selenium, extract_visible_text, truncate_text, extract_linkedin_profiles

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


class AgentOutput(BaseModel):
    fit_for_outreach: bool
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_industry: Optional[str] = None
    company_products_or_services: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_ceo: Optional[str] = None
    company_painpoints: Optional[str] = None
    company_outcomes: Optional[str] = None
    representative_results: Optional[str] = None
    email_subject: Optional[str] = None
    email_content: Optional[str] = None
    linkedin_message: Optional[str] = None
    reasoning: str = Field(
        description="REQUIRED: Explanation of why the company is or isn't suitable for FermanIQ's services. This field MUST be included in every output and cannot be null or empty."
    )


output_parser = PydanticOutputParser(pydantic_object=AgentOutput)


def extract_json_from_content(content: str) -> dict:
    """
    Extract JSON from LLM content, handling markdown code blocks and other formatting.
    """
    if not content or not content.strip():
        raise ValueError("Content is empty")


    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)


    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        content = json_match.group(0)

   
    return json.loads(content)



prompt = PromptTemplate(
    input_variables=[
        "user_input",
        "format_instructions",
    ],
    template="""
You're a senior sales consultant for FermanIQ.
Your task is to analyze a company based on the following input:

{user_input}

Your goals:
1. Identify what the company does, its products/services, and target customers.
2. Determine the company's industry and business model.
3. Assess whether the company is a good fit for FermanIQ's AI services.
4. ALWAYS generate the "reasoning" field: Explain why the company is or isn't suitable for FermanIQ's services. This field is REQUIRED and must be included in every output.
5. If the company is a good fit, generate all outreach fields.
6. If not a good fit, set fit_for_outreach to False and explain why in the reasoning field.
7. CEO Identification:
   - If a CEO/founder is mentioned in the website content, extract their name.
   - If not mentioned AND the company is well-known, you may use training data to identify leadership
   - For smaller/unknown companies, leave as null rather than guessing
   - Never fabricate CEO information for companies you don't have reliable data about
8. Generate company_outcomes: Based on the identified painpoints and industry, generate 3-5 specific outcomes that teams like this company typically achieve with AI agents.
Each outcome should be a concrete benefit (e.g., "Automated CV screening that processes 100+ resumes in minutes instead of hours"). Format as a newline-separated string where each line is one outcome.
9. Generate representative_results: Based on the company's industry and painpoints, generate 3 quantifiable results that similar companies have achieved.
These should be DIFFERENT from company_outcomes - they should be measurable results with numbers, percentages, timeframes, or dollar amounts (e.g., "30% reduction in logistics processing time through automated workflows", "15 hours/week saved in supply chain coordination tasks", "$1M in cost savings identified"). Format as a newline-separated string where each line is one result.


Important rules:
- Use ONLY the provided website content.
- Do NOT hallucinate missing information.
- If information is insufficient, say so clearly.
- Be concise and professional.



Email Content Guidelines:
Subject:
- Put email_subject in this format: Company Name x AI? (e.g. "Mercer x AI?")
Email Body:
CRITICAL - Spacing Format (MUST FOLLOW EXACTLY):
- Use exactly TWO newlines (\n\n) between all paragraphs/sentences to create one blank line
- Format: "Hi [Company] Team,\n\nParagraph 1\n\nParagraph 2\n\nParagraph 3\n\nQuestion\n\nBest regards,\nFermanIQ Team"
- Each paragraph/sentence should be separated by exactly \n\n (one blank line)
- EXCEPTION: "Best regards," and "FermanIQ Team" should use only ONE newline (\n) between them (no blank line)
- Do NOT use 3+ newlines (\n\n\n) - only use \n\n between paragraphs, and \n between "Best regards," and "FermanIQ Team"
- Strip any leading/trailing whitespace from company_name and industry variables before using them

Structure (follow this exact format - KEEP IT SHORT AND FOCUS ON PDF):
1. ALWAYS start with: "Hi [Company Name] Team," (use the exact company_name from your output)
2. First paragraph (1 sentence): State what FermanIQ does for their industry. Format: "We help [industry/type] organizations [benefit] using custom AI agents."
   Example: "We help HR outsourcing organizations streamline operations using custom AI agents."
3. Second paragraph (1 sentence): Connect to their specific situation. Format: "For teams like yours, this typically means [specific actions related to their painpoints]."
   Example: "For teams like yours, this typically means automating payroll, benefits administration, and compliance management tasks."
4. Third paragraph (1 sentence): Mention the PDF attachment - THIS IS IMPORTANT. Format: "I've attached a short PDF with 3 concrete AI use cases we're deploying in [industry] teams today."
   Example: "I've attached a short PDF with 3 concrete AI use cases we're deploying in HR teams today."
   Use the company's industry (e.g., "HR teams", "logistics teams", "healthcare teams", "manufacturing teams")
5. On a NEW LINE, ask one simple question. Format: "Worth a quick look?"
6. Always end with: "Best regards,\nFermanIQ Team"

7. Keep the email under 60 words (very short - let the PDF do the explaining)
Do not:
- Mention pricing
- Over-explain AI
- Use marketing language
- Use more than one question
- Use generic challenges - always reference the specific company_painpoints you identified
- Use vague AI descriptions - always use specific workflows from company_outcomes that match their painpoint
Tone:
- Calm, curious, professional
- No hype, no promises
- Sounds like a human starting a conversation
- Focus on THEIR situation and challenges


What FermanIQ offers to their clients:
FermanIQ specializes in developing tailored AI solutions designed to meet the unique needs of each client's business.
Our custom build AI Systems are helping companies to unlock data driver insights, and help the companies in their decision making capabilities.
Our insights have shown that companies using AI have increased productivity, revenue and customer satisfaction level.


**Custom AI Systems**:
- Process documents and extract data
- Connect multiple tools/databases
- Build intelligent workflows
- System that makes onboarding new employees easier

**AI Chatbots**:
- Handle 60-70% of customer support queries automatically
- Answer employee questions (HR, policies, internal knowledge)
- Make phone calls and book appointments
- Answer questions about the company and its products/services


company_painpoints
Be ultra-specific. Format: **[What you observed] → [What it costs them]**

Example: "Their FAQ has 35 questions about pricing and setup. Their support team likely answers these 50+ times per week,
consuming 15-20 hours on repetitive questions that an AI chatbot could handle instantly."

### company_outcomes
Quantify the solution. Format: **[Specific result] + [Time saved] + [Business impact]**

Example: "AI chatbot handles 65% of routine queries automatically, saving 15 hours/week. Support team focuses on complex issues and upselling.
Clients get instant 24/7 answers instead of waiting for email responses."

### representative_results
Generate quantifiable results that similar companies have achieved. These should be DIFFERENT from company_outcomes.
Format: **[Percentage/Number] + [Metric] + [Timeframe/Context]**

IMPORTANT: Do NOT use dollar amounts ($1M, $500k, etc.). Use percentages, time savings, or qualitative improvements instead.

Examples:
- "30% reduction in logistics processing time through automated workflows"
- "15 hours/week saved in supply chain coordination tasks with AI agents"
- "20+ hours/month saved in benefits administration through automated reporting"
- "Improved visibility into operational costs and decision bottlenecks"
- "Significant reduction in manual analysis and decision-making time"
- "40% faster processing of routine administrative tasks"

These should be realistic, industry-specific results with concrete numbers, percentages, time savings, or qualitative improvements. NO dollar amounts.


CRITICAL: The "reasoning" field is REQUIRED and MUST be included in every output. It cannot be null, empty, or omitted.
The reasoning should explain why the company is or isn't suitable for FermanIQ's services.
Even if fit_for_outreach is false, you MUST still provide a reasoning explanation.

Use these as a guide to help you understand how FermanIQ can help the company.

Industry-Specific Logic Examples:
Manufacturing & Logistics:

Focus: Supply chain and safety.

How FermanIQ can help: "AI agents for maintenance scheduling," or "AI system that helps with Streamlining logistics paperwork."


Healthcare/Medical:

Focus: Compliance and patient flow.

How FermanIQ can help: "AI agents for patient care," "Reducing clinician burnout with AI scribes,"
"Automated appointment follow-ups." "AI system that helps with Streamlining healthcare paperwork."


Real Estate:

Focus: Lead conversion and speed.

How FermanIQ can help: "AI agents for lead qualification," "Automated property analysis,"
"Streamlining property management paperwork." "AI system that helps with Streamlining real estate paperwork."


Email Example:
Gold-standard outreach email (REFERENCE ONLY):
Email Subject: {{company_name}} x AI?
Email Body (NOTE: Use \n\n between paragraphs, \n between "Best regards," and "FermanIQ Team"):
Hi {{company_name}} Team,\n\nWe help HR outsourcing organizations streamline operations using custom AI agents.\n\nFor teams like yours, this typically means automating payroll, benefits administration, and compliance management tasks.\n\nI've attached a short PDF with 3 concrete AI use cases we're deploying in HR teams today.\n\nWorth a quick look?\n\nBest regards,\nFermanIQ Team

CRITICAL FORMATTING RULES:
- Use exactly \n\n (two newlines) between each paragraph/sentence in your output
- This creates one blank line between paragraphs (the correct format)
- EXCEPTION: Use only \n (one newline) between "Best regards," and "FermanIQ Team" (no blank line)
- Strip whitespace from company_name and industry variables before using them
- Do NOT use 3+ newlines - only \n\n between paragraphs, and \n between "Best regards," and "FermanIQ Team"


Visual Email Format Example (shows spacing - use \n\n between paragraphs, \n between "Best regards," and "FermanIQ Team"):
Hi ADP Team,

We help HR outsourcing organizations streamline operations using custom AI agents.

For teams like yours, this typically means automating payroll, benefits administration, and compliance management tasks.

I've attached a short PDF with 3 concrete AI use cases we're deploying in HR teams today.

Worth a quick look?

Best regards,
FermanIQ Team

IMPORTANT: In your JSON output, use \n\n (two newlines) between paragraphs to create one blank line. Use \n (one newline) between "Best regards," and "FermanIQ Team" (no blank line between them).

Rules:
- This example is for tone, brevity, structure, and PDF focus ONLY
- Notice it ALWAYS starts with "Hi [Company Name] Team,"
- Notice it's very short (under 60 words) - let the PDF do the explaining
- Notice it mentions the PDF attachment in paragraph 3 - this is important
- Notice it uses industry-specific language ("HR outsourcing organizations", "HR teams")
- Notice it focuses on what FermanIQ does and what it means for them, then directs them to the PDF
- Do NOT reuse wording
- Do NOT copy sentence structure verbatim
- Keep it brief - the PDF contains all the details and use cases




{format_instructions}
""",
)


def research_company(
    company_url: str,
    few_shot_examples: str = "",
    bad_examples: str = "",
    html: str = None,
):
    if html is None:
        html = fetch_html_with_selenium(company_url)

    visible_text = extract_visible_text(html)
    visible_text = truncate_text(visible_text)


    linkedin_profiles = extract_linkedin_profiles(html, company_url)


    linkedin_section = ""
    if linkedin_profiles:
        linkedin_section = f"""
LinkedIn Profiles Found:
------------------------
{chr(10).join(f"- {profile}" for profile in linkedin_profiles)}
"""
    else:
        linkedin_section = """
LinkedIn Profiles Found:
------------------------
No LinkedIn profiles found on the website.
"""

    user_input = f"""
Company website: {company_url}

Website content:
----------------
{visible_text}
{linkedin_section}
"""


    chain_llm = prompt | llm
    ai_message = chain_llm.invoke(
        {
            "user_input": user_input,
            "few_shot_examples": few_shot_examples,
            "bad_examples": bad_examples,
            "format_instructions": output_parser.get_format_instructions(),
        }
    )


    token_usage = {}

    metadata = getattr(ai_message, "response_metadata", {}) or {}
    if isinstance(metadata, dict):
        token_usage = metadata.get("token_usage", {}) or {}


    try:
        result = output_parser.invoke(ai_message.content)
    except Exception as e:
       
        print(f"\n=== DEBUG: LLM Raw Output ===")
        print(ai_message.content)
        print(f"\n=== DEBUG: Parsing Error ===")
        print(str(e))


        try:
            parsed_json = extract_json_from_content(ai_message.content)
            if "reasoning" not in parsed_json:
                print(f"\n=== DEBUG: Missing 'reasoning' field ===")
                print(f"Available fields: {list(parsed_json.keys())}")

                parsed_json["reasoning"] = "Analysis completed but reasoning field was not generated by the model."
                result = output_parser.invoke(json.dumps(parsed_json))
                print("=== Using fallback reasoning ===")
            else:

                raise
        except (json.JSONDecodeError, ValueError) as json_error:
            print(f"\n=== DEBUG: Could not extract JSON from content ===")
            print(f"JSON Error: {json_error}")
            
            raise e

    return result, token_usage