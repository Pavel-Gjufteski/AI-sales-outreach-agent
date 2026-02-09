from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER
import os
from prompt import AgentOutput


def extract_solution_theme(output: AgentOutput) -> str:
    """
    Extract a solution theme from painpoints/outcomes for the PDF title.
    Returns a default if nothing specific can be extracted.
    """

    text_to_analyze = ""
    if output.company_painpoints:
        text_to_analyze += output.company_painpoints.lower()
    if output.company_outcomes:
        text_to_analyze += " " + output.company_outcomes.lower()

  
    if any(word in text_to_analyze for word in ["healthcare", "health", "medical", "benefits"]):
        return "Optimizing Healthcare Costs"
    elif any(word in text_to_analyze for word in ["cost", "saving", "expense", "spend"]):
        return "Reducing Operational Costs"
    elif any(word in text_to_analyze for word in ["manual", "repetitive", "automate", "workflow"]):
        return "Automating Manual Workflows"
    elif any(word in text_to_analyze for word in ["data", "report", "analysis", "analytics"]):
        return "Streamlining Data Analysis"
    elif any(word in text_to_analyze for word in ["customer", "support", "service", "chatbot"]):
        return "Enhancing Customer Support"
    else:
        return "Streamlining Business Operations"


def generate_ai_opportunity_pdf(output: AgentOutput) -> str:
    """
    Generate a branded PDF document from AgentOutput data.
    Follows the new template structure.

    Returns None if company_painpoints is missing (no value proposition to discuss).
    """

    if not output.company_painpoints or not output.company_painpoints.strip():
        print("Skipping PDF generation: No company painpoints identified.")
        return None

    try:
    
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

     
        company_name_safe = (
            output.company_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
            .replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_")
            .replace("<", "_").replace(">", "_").replace("|", "_")[:50]
            if output.company_name
            else "company"
        )
        filename = f"FermanIQ_Analysis_{company_name_safe}.pdf"
        pdf_path = os.path.join(output_dir, filename)

      
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=36,
        )

    
        story = []

      
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor="darkblue",
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor="darkblue",
            spaceAfter=10,
            spaceBefore=16,
        )
        normal_style = styles["Normal"]
        normal_style.fontSize = 11
        normal_style.leading = 14

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=normal_style,
            leftIndent=14,
            bulletIndent=4,
            spaceBefore=4,
            spaceAfter=4,
        )

    
        logo_path = r"C:\Users\Lenovo\Downloads\FermanIQ logo LinkedIn Banner.png"
        if os.path.exists(logo_path):
            img_reader = ImageReader(logo_path)
            orig_width, orig_height = img_reader.getSize()
            target_width = 1.8 * inch
            scale = target_width / float(orig_width)
            target_height = orig_height * scale
            logo = Image(logo_path, width=target_width, height=target_height)
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 0.3 * inch))

     
        solution_theme = extract_solution_theme(output)
        title_text = f"AI Systems for {solution_theme}"
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 0.3 * inch))

    
        story.append(Paragraph("Who We Are", heading_style))
        story.append(
            Paragraph(
                "FermanIQ specializes in developing tailored AI solutions designed to meet the unique needs of each client's business. Our custom build AI Systems are helping companies to unlock data driver insights, and help the companies in their decision making capabilities. Our insights have shown that companies using AI have increased productivity, revenue and customer satisfaction level.",
                normal_style,
            )
        )
        story.append(Spacer(1, 0.2 * inch))

      
        company_name = output.company_name or "your company"
        story.append(Paragraph(f"Challenges Organizations Like {company_name} Faces", heading_style))

       
        for line in output.company_painpoints.split("\n"):
            line = line.strip()
            if not line:
                continue
            story.append(Paragraph(f"• {line}", bullet_style))

        story.append(Spacer(1, 0.2 * inch))

   
        story.append(Paragraph("How FermanIQ Helps", heading_style))

    
        if output.company_outcomes and output.company_outcomes.strip():
            for line in output.company_outcomes.split("\n"):
                line = line.strip()
                if not line:
                    continue
                story.append(Paragraph(f"• {line}", bullet_style))
        else:
            story.append(
                Paragraph(
                    "• AI agents that automate repetitive, data-heavy processes",
                    bullet_style,
                )
            )

        story.append(Spacer(1, 0.2 * inch))

   
        story.append(Paragraph("Results / Outcomes (Representative)", heading_style))

     
        if output.representative_results and output.representative_results.strip():
            for line in output.representative_results.split("\n"):
                line = line.strip()
                if not line:
                    continue
                story.append(Paragraph(f"• {line}", bullet_style))
        else:
           
            story.append(
                Paragraph(
                    "• Significant time savings through automated workflows",
                    bullet_style,
                )
            )
            story.append(
                Paragraph(
                    "• Improved efficiency and decision-making capabilities",
                    bullet_style,
                )
            )
            story.append(
                Paragraph(
                    "• Enhanced productivity and reduced manual work",
                    bullet_style,
                )
            )

        story.append(Spacer(1, 0.2 * inch))

       
        story.append(Paragraph("Next Steps", heading_style))
        story.append(
            Paragraph(
                f"For a brief discussion on how FermanIQ could help {company_name} achieve similar results, schedule a meeting here:",
                normal_style,
            )
        )
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Paragraph(
                '<u>https://calendly.com/kasper-fermaniq</u>',
                normal_style,
            )
        )

      
        doc.build(story)
        return pdf_path

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None