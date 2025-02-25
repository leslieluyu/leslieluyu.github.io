import os
import re
import requests
from fpdf import FPDF
from bs4 import BeautifulSoup
import pdfkit
import markdown

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font("Arial", style="", fname="/usr/share/fonts/truetype/msttcorefonts/arial.ttf", uni=True)
        self.set_font("Arial", style="", size=12)
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'AIGC Contest Quick Start Guide', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def fetch_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    else:
        return "Failed to retrieve content."

def save_to_pdf(content, title, output_file):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title(title)
    pdf.chapter_body(content)
    pdf.output(output_file)

def crawl_webpage(url):
    # response = requests.get(url)
    # return response.text
    webpage_type = check_webpage_type(url)
    
    if webpage_type == 'html':
        content = extract_from_html(url)
        print(f"")
    elif webpage_type == 'github_markdown':
        content = extract_from_github_markdown(url)
    else:
        print(f"Unsupported webpage type: {webpage_type}")
    print(f"webpage_type: {webpage_type}")
    return content


def save_to_pdf(html_content, output_file):
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    pdfkit.from_string(html_content, output_file, options=options)



def extract_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Dictionary to store all links with their names/descriptions
    links_dict = {}
    
    # Multiple patterns to match different link formats
    patterns = [
        # Match bullet points with • and o
        r'[•o]\s*(.*?)\s*:\s*(https?://[^\s]+)',
        # Match direct URLs with descriptions
        r'(?:^|\n)([^:\n]+)：\s*(https?://[^\s]+)',
        # Match plain URLs in text (with optional description before)
        r'(?:^|\n)?(?:([^:\n]+):\s*)?(https?://[^\s]+)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            if len(match.groups()) >= 2:
                name, url = match.groups()
                if name and url:
                    # Clean up the name and use it as key
                    name = name.strip()
                    # Remove any unwanted characters and make it filename-friendly
                    safe_name = re.sub(r'\W+', '_', name)
                    # Remove any trailing punctuation from URL
                    url = url.rstrip('.,;')
                    links_dict[safe_name] = url
            elif len(match.groups()) == 1:
                # Handle cases where we only found a URL
                url = match.group(0).strip()
                if url.startswith('http'):
                    # Use part of the URL as the name if no description
                    name = url.split('/')[-1].split('.')[0]
                    safe_name = re.sub(r'\W+', '_', name)
                    links_dict[safe_name] = url

    return links_dict


def extract_from_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example: Extract all text from the page
        text = soup.get_text()
        return text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_from_github_markdown(url):
    try:
        # Extract the owner, repo, and path from the URL
        parts = url.split('/')
        owner = parts[3]
        repo = parts[4]
        path = '/'.join(parts[7:])  # Path to the file in the repo
        
        # Construct the GitHub API URL for the raw content
        api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
        
        # Make the API request
        response = requests.get(api_url, headers={'Accept': 'application/vnd.github.v3.raw'})
        response.raise_for_status()  # Raise an exception for bad status codes
        
        raw_markdown = response.text
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(raw_markdown)
        
        return html_content
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
def check_webpage_type(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('Content-Type')
        
        if 'text/html' in content_type:
            if 'github.com' in url and 'blob' in url:
                return 'github_markdown'
            else:
                return 'html'
        else:
            return 'other'
    
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return None
def main(file_path, output_dir, test_extract=False):
    links = extract_links(file_path)
    print("Extracted links:")
    for name, url in links.items():
        print(f"{name}: {url}")
    
    if test_extract:
        return

    for name, url in links.items():
        print(f"Fetching content from: {name:},{url}")
        # content = fetch_content(url)
        content = crawl_webpage(url)
        # print(f"Content fetched: {content}")
        output_file = os.path.join(output_dir, f"{name}.pdf")
        # save_to_pdf(content, name, output_file)
        save_to_pdf(content, output_file)
        print(f"PDF saved as {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch content from links in a text file and save each to a separate PDF file.")
    parser.add_argument('file_path', type=str, help="Path to the input text file.")
    parser.add_argument('output_dir', type=str, help="Path to the output directory.")
    parser.add_argument('--test_extract', action='store_true', help="Only test the extraction of links from the given file.")
    args = parser.parse_args()

    main(args.file_path, args.output_dir, args.test_extract)