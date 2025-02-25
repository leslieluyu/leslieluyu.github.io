import os
import re
import requests
from fpdf import FPDF
from bs4 import BeautifulSoup

class PDF(FPDF):
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

def save_to_pdf(content_dict, output_file):
    pdf = PDF()
    pdf.add_page()
    for title, content in content_dict.items():
        pdf.chapter_title(title)
        pdf.chapter_body(content)
    pdf.output(output_file)

def extract_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    pattern = re.compile(r'•\s(.+?)\s*:\s*(https?://[^\s]+)')
    matches = pattern.findall(content)
    return {name: url for name, url in matches}

def main(file_path, output_file):
    links = extract_links(file_path)
    content_dict = {}
    for name, url in links.items():
        print(f"Fetching content from: {url}")
        content = fetch_content(url)
        content_dict[name] = content
    save_to_pdf(content_dict, output_file)
    print(f"PDF saved as {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch content from links in a text file and save to PDF.")
    parser.add_argument('file_path', type=str, help="Path to the input text file.")
    parser.add_argument('output_file', type=str, help="Path to the output PDF file.")
    args = parser.parse_args()

    main(args.file_path, args.output_file)