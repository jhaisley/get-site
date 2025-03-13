import argparse
from apify import Actor, Request
import asyncio
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse, unquote
import validators
from pathlib import Path
import sys
import os
from httpx import AsyncClient
from typing import Optional, Dict, Any, List


class AsyncWebCrawler:
    def __init__(self, base_url: str, max_depth: int = 1, quiet: bool = False):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.base_path = urlparse(base_url).path.rstrip('/')
        self.visited = set()
        self.content = []
        self.max_depth = max_depth
        self.quiet = quiet
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = True  # We'll handle images ourselves
        self.converter.body_width = 0

    def log(self, message: str) -> None:
        """Log a message if not in quiet mode"""
        if not self.quiet:
            print(message)

    def process_images(self, soup: BeautifulSoup, base_url: str) -> str:
        """Process images in HTML and return markdown image references with alt text and filenames"""
        markdown_images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                full_url = urljoin(base_url, src)
                alt_text = img.get('alt', '')
                filename = os.path.basename(unquote(urlparse(full_url).path))
                
                if alt_text:
                    markdown_images.append(f'![{alt_text} (File: {filename})]({full_url})')
                else:
                    markdown_images.append(f'![File: {filename}]({full_url})')
        
        return '\n'.join(markdown_images)

    def is_valid_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        # Check if it's a valid URL and on the same domain
        if not (validators.url(url) and parsed_url.netloc == self.domain):
            return False
            
        # Check if it's not a binary file
        if any(ext in url for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip']):
            return False
            
        # If base_path is specified (not empty or root /), ensure the URL is under that path
        if self.base_path:
            url_path = parsed_url.path.rstrip('/')
            if not url_path.startswith(self.base_path):
                return False
            
        return True

    async def crawl_page(self, client: AsyncClient, url: str, depth: int) -> None:
        if url in self.visited or not self.is_valid_url(url):
            return

        self.log(f"Crawling: {url} (depth={depth})")
        self.visited.add(url)

        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Convert page to markdown and store
            title = soup.title.string if soup.title else url
            
            # Process images first
            image_markdown = self.process_images(soup, url)
            
            # Convert rest of the content
            main_content = self.converter.handle(response.text)
            
            # Combine content with processed images
            full_content = main_content
            if image_markdown:
                full_content = f"{image_markdown}\n\n{main_content}"
            
            self.content.append({
                'url': url,
                'title': title,
                'content': full_content
            })

            if depth < self.max_depth:
                tasks = []
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        if self.is_valid_url(full_url) and full_url not in self.visited:
                            tasks.append(self.crawl_page(client, full_url, depth + 1))
                
                if tasks:
                    await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"Error crawling {url}: {e}")

    async def crawl(self) -> None:
        async with AsyncClient() as client:
            await self.crawl_page(client, self.base_url, 0)

    def save_markdown(self, output_file: Optional[Path] = None) -> str:
        """Save or return markdown content. If output_file is None, returns the content as a string."""
        content = []
        for page in self.content:
            content.extend([
                f"\n\n# {page['title']}",
                f"*URL: {page['url']}*\n",
                page['content'],
                '-' * 80
            ])
        
        markdown = '\n'.join(content)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
                
        return markdown


async def run_apify_actor() -> None:
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        start_url = actor_input.get('start_url', 'https://apify.com')
        max_depth = actor_input.get('max_depth', 1)
        quiet = actor_input.get('quiet', False)
        output_file = actor_input.get('output_file', 'output.md')

        # Create crawler instance
        crawler = AsyncWebCrawler(start_url, max_depth=max_depth, quiet=quiet)
        await crawler.crawl()

        # Save to output file and push to dataset
        markdown_content = crawler.save_markdown(Path(output_file))
        
        # Push single combined result to dataset
        await Actor.push_data({
            'url': start_url,
            'content': markdown_content,
            'output_file': output_file
        })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Crawl a website and convert it to markdown'
    )
    parser.add_argument(
        'url',
        nargs='?',
        help='URL to crawl. If not provided, runs in Apify actor mode'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path. If not provided, prints to terminal'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output except errors'
    )
    parser.add_argument(
        '-d', '--max-depth',
        type=int,
        default=1,
        help='Maximum crawl depth (default: 1)'
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    
    if args.url:
        # Running as standalone script
        if not validators.url(args.url):
            print("Error: Please provide a valid URL", file=sys.stderr)
            sys.exit(1)

        crawler = AsyncWebCrawler(args.url, max_depth=args.max_depth, quiet=args.quiet)
        await crawler.crawl()
        
        # Handle output
        output_path = args.output and Path(args.output)
        result = crawler.save_markdown(output_path)
        
        if not output_path:
            # Print to terminal if no output file specified
            print(result)
        elif not args.quiet:
            print(f"\nCrawling complete! Results saved to {output_path}")
    else:
        # Running as Apify actor
        await run_apify_actor()


if __name__ == "__main__":
    asyncio.run(main())