from scrape import fetch_html_with_selenium, extract_linkedin_profiles
from prompt import research_company
from pdf_converter import generate_ai_opportunity_pdf
from token_usage import TokenUsage, time_call
from mongodb_storage import save_analysis
from send_email import send_email_to_boss
import re


def clean_email_spacing(email_content: str) -> str:
    """
    Normalize email spacing to consistent format.
    - Strips leading/trailing whitespace from each line
    - Ensures exactly \n\n (two newlines = one blank line) between all paragraphs
    - Ensures \n (one newline) between "Best regards," and "FermanIQ Team"
    - Removes leading/trailing empty lines
    - Collapses 3+ consecutive newlines into exactly 2
    """
    if not email_content:
        return email_content

   
    cleaned = re.sub(r'\n{2,}', '\n\n', email_content)

   
    lines = [line.rstrip() for line in cleaned.split('\n')]

  
    while lines and not lines[0]:
        lines.pop(0)
    
    while lines and not lines[-1]:
        lines.pop()

 
    non_empty_lines = [line for line in lines if line.strip()]

    result = []
    for i, line in enumerate(non_empty_lines):
      
        if i > 0 and 'FermanIQ' in line and 'Best regards' in non_empty_lines[i-1]:
            result.append(line)
        else:
           
            if result:
                result.append('')
            result.append(line)

   
    output = '\n'.join(result)

   
    output = re.sub(r'(Best regards,)\s*\n\s*\n\s*(FermanIQ Team)', r'\1\n\2', output)

   
    output = re.sub(r'\n{3,}', '\n\n', output)

    return output.strip()


if __name__ == "__main__":
    print("=== AI Outreach Research Agent ===")
    user_input_url = input("Enter the company website URL (e.g., https://example.com): ").strip()

    
    company_url = user_input_url
    if not company_url.startswith("http"):
        company_url = "https://" + company_url

    print("Running research...")
    html = fetch_html_with_selenium(company_url)
    linkedin_profiles = extract_linkedin_profiles(html, company_url)

    (output, token_usage_raw), elapsed_seconds = time_call(
        research_company, company_url, html=html
    )

    print("\n=== Output ===")
    print(output.model_dump_json(indent=2))

    TokenUsage(
        model_name="gpt-4o-mini",
        input_tokens=token_usage_raw.get("prompt_tokens") or token_usage_raw.get("input_tokens") or 0,
        output_tokens=token_usage_raw.get("completion_tokens") or token_usage_raw.get("output_tokens") or 0,
        elapsed_seconds=elapsed_seconds,
    ).pretty_print()

    pdf_path = generate_ai_opportunity_pdf(output)
    if pdf_path:
        print(f"\n PDF generated: {pdf_path}")

    try:
        doc_id = save_analysis(
            company_url=company_url,
            user_input=user_input_url,
            html=html,
            output=output,
            token_usage=token_usage_raw,
            elapsed_seconds=elapsed_seconds,
            linkedin_profiles=linkedin_profiles,
            pdf_path=pdf_path
        )
        print(f"Analysis saved to MongoDB (ID: {doc_id})")
    except Exception as e:
        print(f"Warning: Failed to save to MongoDB: {e}")

 
    if output.email_subject and output.email_content:
        if pdf_path:
            print("\n:e-mail: Sending email to boss...")
            
            cleaned_email_content = clean_email_spacing(output.email_content)
            success = send_email_to_boss(
                email_subject=output.email_subject,
                email_content=cleaned_email_content,
                pdf_path=pdf_path
            )
            if success:
                print("Email sent successfully!")
            else:
                print("Failed to send email. Check error messages above.")
        else:
            print("\n Warning: No PDF generated. Skipping email send.")
    else:
        print("\n Warning: No email subject or content generated. Skipping email send.")