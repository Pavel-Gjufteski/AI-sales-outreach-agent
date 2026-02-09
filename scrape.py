import time
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def fetch_html_with_selenium(url: str, wait_seconds: int = 5) -> str:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    driver = webdriver.Chrome(options=options)

    try:
        print(f"Fetching {url} with Selenium...")
        driver.get(url)
        time.sleep(wait_seconds)
        html = driver.page_source
        return html
    finally:
        driver.quit()


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "footer", "header", "nav"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def truncate_text(text: str, max_chars: int = 6000) -> str:
    return text[:max_chars]


def extract_linkedin_profiles(html: str, base_url: str) -> list[str]:
    """
    Extract all LinkedIn profile URLs from the HTML.
    Returns a list of unique LinkedIn URLs found on the page.
    """
    soup = BeautifulSoup(html, "html.parser")
    linkedin_urls = set()


    for link in soup.find_all("a", href=True):
        href = link.get("href", "").strip()

        if not href:
            continue


        if href.startswith("/"):
            href = urljoin(base_url, href)
        elif not href.startswith("http"):
            continue


        parsed = urlparse(href)
        if "linkedin.com" in parsed.netloc.lower():

            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            linkedin_urls.add(normalized)


    return sorted(list(linkedin_urls))