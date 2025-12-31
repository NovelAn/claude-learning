#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Article Fetcher
Fetches articles from WeChat public accounts and saves them as JSON files.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import hashlib

class WeChatArticleFetcher:
    """Fetches and parses WeChat public account articles."""

    def __init__(self, output_dir="data/articles"):
        """Initialize the fetcher.

        Args:
            output_dir: Directory to save fetched articles
        """
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_article(self, url):
        """Fetch a single WeChat article.

        Args:
            url: WeChat article URL (mp.weixin.qq.com)

        Returns:
            dict: Article data with keys:
                - url: Original URL
                - title: Article title
                - content: Article content (HTML)
                - content_text: Plain text content
                - author: Author name
                - account_name: Public account name
                - publish_time: Publish timestamp
                - read_count: Read count (if available)
                - like_count: Like count (if available)
                - images: List of image URLs
                - fetched_at: Fetch timestamp
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article data
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'content_text': self._extract_text(soup),
                'author': self._extract_author(soup),
                'account_name': self._extract_account_name(soup),
                'publish_time': self._extract_publish_time(soup),
                'publish_time_str': self._extract_publish_time_str(soup),
                'read_count': self._extract_read_count(soup),
                'like_count': self._extract_like_count(soup),
                'images': self._extract_images(soup),
                'fetched_at': datetime.now().isoformat()
            }

            print(f"  [OK] Title: {article_data['title']}")
            print(f"  [OK] Author: {article_data['author']}")
            print(f"  [OK] Content length: {len(article_data['content_text'])} chars")

            return article_data

        except requests.RequestException as e:
            print(f"  [ERROR] Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"  [ERROR] Error parsing {url}: {e}")
            return None

    def _extract_title(self, soup):
        """Extract article title."""
        # Try multiple selectors for title
        selectors = [
            'meta[property="og:title"]',
            'h1.rich_media_title',
            '.rich_media_title',
            'h1'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        return "Untitled"

    def _extract_content(self, soup):
        """Extract article content (HTML)."""
        content_div = soup.select_one('.rich_media_content') or soup.select_one('#js_content')
        if content_div:
            return str(content_div)
        return ""

    def _extract_text(self, soup):
        """Extract article content as plain text."""
        content_div = soup.select_one('.rich_media_content') or soup.select_one('#js_content')
        if content_div:
            # Remove script and style elements
            for script in content_div(['script', 'style']):
                script.decompose()
            return content_div.get_text(separator='\n', strip=True)
        return ""

    def _extract_author(self, soup):
        """Extract author name."""
        selectors = [
            'meta[property="og:article:author"]',
            '.rich_media_meta_text'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        return "Unknown"

    def _extract_account_name(self, soup):
        """Extract public account name."""
        selector = 'meta[property="og:article:author"]'
        element = soup.select_one(selector)
        if element:
            return element.get('content', '').strip()

        # Fallback to profile link
        profile_link = soup.select_one('.rich_media_meta_link_text')
        if profile_link:
            return profile_link.get_text().strip()

        return "Unknown"

    def _extract_publish_time(self, soup):
        """Extract publish time as timestamp."""
        # Try script tag with publish time
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'createTime' in script.string:
                try:
                    import re
                    match = re.search(r'"createTime"\s*:\s*(\d+)', script.string)
                    if match:
                        return int(match.group(1))
                except:
                    pass

        # Fallback to meta tag
        selector = 'meta[property="article:published_time"]'
        element = soup.select_one(selector)
        if element:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(element.get('content', '').replace('Z', '+00:00'))
                return int(dt.timestamp())
            except:
                pass

        return None

    def _extract_publish_time_str(self, soup):
        """Extract publish time as readable string."""
        # Try to find in script
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'createTime' in script.string:
                try:
                    import re
                    match = re.search(r'"createTime"\s*:\s*(\d+)', script.string)
                    if match:
                        timestamp = int(match.group(1))
                        dt = datetime.fromtimestamp(timestamp)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

        return "Unknown"

    def _extract_read_count(self, soup):
        """Extract read count (if available)."""
        # Read counts are often loaded dynamically and not in HTML
        return None

    def _extract_like_count(self, soup):
        """Extract like count (if available)."""
        # Like counts are often loaded dynamically and not in HTML
        return None

    def _extract_images(self, soup):
        """Extract image URLs from article."""
        images = []
        content_div = soup.select_one('.rich_media_content') or soup.select_one('#js_content')
        if content_div:
            for img in content_div.find_all('img'):
                img_url = img.get('data-src') or img.get('src')
                if img_url:
                    images.append(img_url)
        return images

    def generate_article_id(self, url):
        """Generate unique ID for article."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()[:12]

    def save_article(self, article_data):
        """Save article data to JSON file.

        Args:
            article_data: Dictionary with article data

        Returns:
            str: Path to saved file
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate filename
        article_id = self.generate_article_id(article_data['url'])
        filename = f"article-{article_id}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

        print(f"  [OK] Saved to: {filepath}")
        return filepath

    def fetch_multiple(self, urls):
        """Fetch multiple articles.

        Args:
            urls: List of WeChat article URLs

        Returns:
            list: List of fetched article data
        """
        articles = []
        print(f"\nFetching {len(urls)} articles...\n")

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}]", end=" ")
            article = self.fetch_article(url.strip())
            if article:
                articles.append(article)
                self.save_article(article)
            print()

        return articles


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python fetch-articles.py <url1> <url2> ...")
        print("\nExample:")
        print("  python fetch-articles.py https://mp.weixin.qq.com/s/xxxxx")
        print("\nOr provide URLs via stdin:")
        print('  echo "url1\\nurl2" | python fetch-articles.py -')
        sys.exit(1)

    # Get URLs
    if sys.argv[1] == '-':
        # Read from stdin
        urls = [line.strip() for line in sys.stdin if line.strip()]
    else:
        # Get from command line
        urls = sys.argv[1:]

    # Validate URLs
    valid_urls = []
    for url in urls:
        if 'mp.weixin.qq.com' in url:
            valid_urls.append(url)
        else:
            print(f"Warning: Skipping invalid WeChat URL: {url}")

    if not valid_urls:
        print("Error: No valid WeChat article URLs provided.")
        sys.exit(1)

    # Fetch articles
    fetcher = WeChatArticleFetcher()
    articles = fetcher.fetch_multiple(valid_urls)

    # Summary
    print(f"\n{'='*60}")
    print(f"Fetch complete!")
    print(f"Successfully fetched: {len(articles)}/{len(valid_urls)} articles")
    print(f"Output directory: {fetcher.output_dir}")
    print(f"{'='*60}\n")

    # Save summary
    summary_file = os.path.join(fetcher.output_dir, 'fetch-summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'fetched_at': datetime.now().isoformat(),
            'total_urls': len(valid_urls),
            'successful': len(articles),
            'failed': len(valid_urls) - len(articles),
            'articles': [
                {
                    'id': fetcher.generate_article_id(a['url']),
                    'title': a['title'],
                    'url': a['url']
                }
                for a in articles
            ]
        }, f, ensure_ascii=False, indent=2)

    print(f"Summary saved to: {summary_file}")


if __name__ == '__main__':
    main()
