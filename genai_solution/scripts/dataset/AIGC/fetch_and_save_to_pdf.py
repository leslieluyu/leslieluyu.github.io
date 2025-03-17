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

def read_markdown_file(markdown_file_path, output_file):
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Convert markdown content to HTML
        html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
        
        # Save the HTML content to PDF
        save_to_pdf(html_content, output_file)
        print(f"PDF saved as {output_file}")
    except Exception as e:
        print(f"Error reading markdown file {markdown_file_path}: {e}")


def save_to_pdf(content, output_file):
    try:
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [('Accept-Encoding', 'gzip')],
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Add syntax highlighting CSS for code blocks
        css = """
        <style>
            .highlight pre { background-color: #f6f8fa; padding: 16px; border-radius: 6px; }
            code { font-family: monospace; }
        </style>
        """
        html_content = css + content
        
        pdfkit.from_string(html_content, output_file, options=options)
    except Exception as e:
        print(f"Error saving PDF: {e}")
        raise

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


def extract_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # List to store links in order of appearance
    links_list = []
    # Set to track seen URLs to avoid duplicates
    seen_urls = set()
    
    # Multiple patterns to match different link formats
    patterns = [
        # Match bullet points (• or o) with description and URL
        r'[•o]\s*([^:\n]*?)(?:：|\:)\s*(https?://[^\s\)]+)',
        # Match bullet points with direct URL
        r'[•o]\s+(https?://[^\s\)]+)',
        # Match description with URL
        r'(?:^|\n)([^:\n]+?)(?:：|\:)\s*(https?://[^\s\)]+)',
        # Match plain URLs
        r'(?:^|\n|\s)(https?://[^\s\)]+)'
    ]
    
    # Find all matches in the content
    all_matches = []
    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        all_matches.extend((match.start(), match, pattern) for match in matches)
    
    # Sort matches by their position in the file
    all_matches.sort(key=lambda x: x[0])
    
    # Process matches in order
    for _, match, pattern in all_matches:
        groups = match.groups()
        url = None
        name = None
        
        # Extract URL and name based on pattern match
        if len(groups) == 2:
            # Pattern with both name and URL
            name, url = groups
        elif len(groups) == 1:
            # Pattern with URL only
            url = groups[0]
        
        if url:
            # Clean up the URL
            url = url.rstrip('.,;')
            
            # Skip if we've seen this URL before
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Generate name if not provided or clean up existing name
            if not name or name.strip() == '':
                # Try to create a meaningful name from the URL
                path_parts = url.split('/')
                if 'github.com' in url:
                    # For GitHub URLs, use the last meaningful part
                    relevant_parts = [part for part in path_parts[5:] if part and part not in ['blob', 'tree', 'main', 'latest']]
                    if relevant_parts:
                        name = relevant_parts[-1].replace('.md', '').replace('.ipynb', '')
                else:
                    name = path_parts[-1].split('.')[0]
            else:
                # Clean up the provided name
                name = name.strip()
                # Remove bullet points and other unwanted characters from start
                name = re.sub(r'^[•o\s]+', '', name)
            
            # Make the name filename-friendly
            safe_name = re.sub(r'\W+', '_', name)
            safe_name = re.sub(r'_+', '_', safe_name)  # Replace multiple underscores with single
            safe_name = safe_name.strip('_')  # Remove leading/trailing underscores
            
            # Ensure unique name
            base_name = safe_name
            counter = 1
            final_name = base_name
            while any(item['name'] == final_name for item in links_list):
                final_name = f"{base_name}_{counter}"
                counter += 1
            
            # Add to list in order of appearance
            links_list.append({'name': final_name, 'url': url})
    
    # Convert to final format while preserving order
    links_dict = {item['name']: item['url'] for item in links_list}
    return links_dict


def extract_from_html_old(url):
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


def extract_from_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main content of the page
        main_content = soup.find('main')  # Assuming the main content is within a <main> tag
        if not main_content:
            main_content = soup.find('article')  # Fallback to <article> if <main> is not found
        if not main_content:
            main_content = soup.find('body')  # Fallback to <body> if <article> is not found
        
        # Extract text from the main content
        text = main_content.get_text(separator='\n', strip=True)
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
        
        raw_content = response.text
        
        # Handle different file types
        if path.endswith('.ipynb'):
            # Parse Jupyter notebook content
            import json
            notebook = json.loads(raw_content)
            
            # Extract markdown and code cells
            content = []
            for cell in notebook['cells']:
                if cell['cell_type'] == 'markdown':
                    content.extend(cell['source'])
                    content.append('\n\n')
                elif cell['cell_type'] == 'code':
                    content.append('```python\n')
                    content.extend(cell['source'])
                    content.append('\n```\n\n')
            
            # Join all content and convert to HTML
            markdown_content = ''.join(content)
            html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
            
        else:
            # Regular markdown files
            html_content = markdown.markdown(raw_content, extensions=['fenced_code', 'tables'])
        
        return html_content
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing notebook {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
        return None

def check_webpage_type(url):
    try:
        # First check if it's a GitHub URL
        if 'github.com' in url:
            # Check different GitHub URL patterns
            if url.endswith('.ipynb'):
                return 'github_markdown'  # We'll handle notebooks as markdown
            elif any(pattern in url for pattern in ['/blob/', '/tree/']):
                return 'github_markdown'
            elif url.endswith('.md'):
                return 'github_markdown'
            elif '/raw/' in url:
                return 'github_markdown'
        
        # For non-GitHub URLs, check content type
        response = requests.head(url)
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'text/html' in content_type:
            return 'html'
        elif any(md_type in content_type for md_type in ['text/markdown', 'text/x-markdown']):
            return 'github_markdown'
        else:
            return 'other'
    
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return None

def save_links_to_file(links_dict, output_dir):
    output_file = os.path.join(output_dir, 'links_output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        # Use items() to maintain the original order
        for index, (name, url) in enumerate(links_dict.items(), 1):
            indexed_name = f"{index}_{name}"
            f.write(f"{indexed_name}\t{url}\n")
    return output_file

def read_links_from_file(links_file):
    links_dict = {}
    with open(links_file, 'r', encoding='utf-8') as f:
        for line in f:
            print(line)
            name, url = line.strip().split('\t')
            # Remove the index from the name if it exists
            # if '_' in name:
            #     try:
            #         index, actual_name = name.split('_', 1)
            #         if index.isdigit():
            #             name = actual_name                       
            #     except ValueError:
            #         pass  # Keep original name if splitting fails
            links_dict[name] = url
    return links_dict

def main(file_path, output_dir, test_extract=False, save_by_links=False):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if save_by_links:
        # Directly read from existing links file and process
        if not os.path.exists(file_path):
            print(f"Error: Links file {file_path} does not exist!")
            return
        print(f"\nReading links from: {file_path}")
        links = read_links_from_file(file_path)
    else:
        # Extract links and save to file
        links = extract_links(file_path)
        print("Extracted links:")
        for name, url in links.items():
            print(f"{name}: {url}")
        
        # Save links to file
        links_file = save_links_to_file(links, output_dir)
        print(f"\nLinks saved to: {links_file}")
        
        if test_extract:
            return

    # Process links and save PDFs
    print("\nProcessing links and saving PDFs:")
    for name, url in links.items():
        print(f"\nFetching content from: {name}: {url}")
        try:
            content = crawl_webpage(url)
            if content:
                output_file = os.path.join(output_dir, f"{name}.pdf")
                save_to_pdf(content, output_file)
                print(f"PDF saved as {output_file}")
            else:
                print(f"Failed to fetch content from {url}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch content from links in a text file and save each to a separate PDF file.")
    parser.add_argument('file_path', type=str, help="Path to the input text file or links file when using --save_by_links.")
    parser.add_argument('output_dir', type=str, help="Path to the output directory.")
    parser.add_argument('--test_extract', action='store_true', help="Only test the extraction of links from the given file.")
    parser.add_argument('--save_by_links', action='store_true', help="Read links directly from a links file and save PDFs without extracting links from text.")
    parser.add_argument('--markdown_file', type=str, help="Path to a markdown file to convert to PDF.")
    args = parser.parse_args()

    if args.markdown_file:
        output_file = os.path.join(args.output_dir, 'output.pdf')
        read_markdown_file(args.markdown_file, output_file)
    else:
        main(args.file_path, args.output_dir, args.test_extract, args.save_by_links)