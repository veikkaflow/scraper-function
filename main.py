from firebase_functions import https_fn
from firebase_admin import initialize_app
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import logging
import json

# Initialize Firebase Admin only if not already initialized
try:
    initialize_app()
except ValueError:
    # App already initialized, that's OK
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website_data(url):
    """
    Scrape website using requests + BeautifulSoup
    Returns same format as Scrapy version: {title, text, logos, colors}
    """
    try:
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SiteScraper/1.0; +https://gen-lang-client-0746010330.firebaseapp.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Fetch the page
        logger.info(f'Fetching URL: {url}')
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        
        # Extract text content from body
        text_parts = []
        
        # Get text from main content areas (in priority order)
        for selector in ['main', 'article', '.content', '#content']:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if text.strip():
                    text_parts.append(text)
                    break  # Use first match
        
        # If no main content found, get all body text
        if not text_parts:
            body = soup.find('body')
            if body:
                text_parts = [body.get_text(separator=' ', strip=True)]
        
        # Clean and combine text
        full_text = ' '.join(text_parts)
        full_text = ' '.join(full_text.split())  # Remove extra whitespace
        full_text = full_text[:5000]  # Limit to 5000 characters
        
        # Extract logos
        logos = set()
        base_url = response.url
        
        # Find logo images
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            class_attr = ' '.join(img.get('class', [])).lower()
            
            if src and ('logo' in src.lower() or 'logo' in alt or 'logo' in class_attr):
                try:
                    absolute_url = urljoin(base_url, src)
                    logos.add(absolute_url)
                except:
                    pass
        
        # Find favicons
        link_elements = soup.find_all('link')
        for link in link_elements:
            rel = link.get('rel', [])
            if isinstance(rel, list):
                rel = ' '.join(rel).lower()
            else:
                rel = str(rel).lower()
            href = link.get('href', '')
            
            if href and 'icon' in rel:
                try:
                    absolute_url = urljoin(base_url, href)
                    logos.add(absolute_url)
                except:
                    pass
        
        # Try common logo paths
        parsed_url = urlparse(base_url)
        base_path = f"{parsed_url.scheme}://{parsed_url.netloc}"
        common_logo_paths = [
            '/logo.png', '/logo.svg', '/logo.jpg',
            '/images/logo.png', '/images/logo.svg',
            '/assets/logo.png', '/assets/logo.svg',
            '/static/logo.png', '/static/logo.svg'
        ]
        for path in common_logo_paths:
            try:
                absolute_url = urljoin(base_path, path)
                logos.add(absolute_url)
            except:
                pass
        
        # Extract colors from CSS
        colors = set()
        
        # Extract from style attributes
        style_elements = soup.find_all(attrs={'style': True})
        for elem in style_elements:
            style = elem.get('style', '')
            hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', style, re.IGNORECASE)
            for color in hex_colors:
                if len(color) == 3:
                    color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
                colors.add(f'#{color}')
        
        # Extract from style tags
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_content = style_tag.string or ''
            hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', style_content, re.IGNORECASE)
            for color in hex_colors:
                if len(color) == 3:
                    color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
                colors.add(f'#{color}')
        
        # Convert to lists and limit
        logos_list = list(logos)[:10]
        colors_list = list(colors)[:5]
        
        # Default colors if none found
        if not colors_list:
            colors_list = ['#4f46e5', '#1f2937', '#3b82f6', '#10b981', '#f59e0b']
        
        return {
            'title': title or 'Untitled',
            'text': full_text,
            'logos': logos_list,
            'colors': colors_list
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f'Request error: {str(e)}')
        raise Exception(f'Failed to fetch website: {str(e)}')
    except Exception as e:
        logger.error(f'Scraping error: {str(e)}', exc_info=True)
        raise


@https_fn.on_request()
def scrape_website(req: https_fn.Request) -> https_fn.Response:
    """HTTP Cloud Function that scrapes website using requests + BeautifulSoup"""
    # CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=204, headers=cors_headers)
    
    # Only allow POST
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({'error': 'Method not allowed'}),
            status=405,
            headers={**cors_headers, 'Content-Type': 'application/json'}
        )
    
    try:
        data = req.get_json(silent=True)
        if not data:
            return https_fn.Response(
                json.dumps({'error': 'Invalid JSON'}),
                status=400,
                headers={**cors_headers, 'Content-Type': 'application/json'}
            )
        
        # Handle both direct calls and Firebase SDK calls (which wrap data in 'data' field)
        if 'data' in data and isinstance(data['data'], dict):
            url = data['data'].get('url')
        else:
            url = data.get('url')

        if not url or not isinstance(url, str):
            return https_fn.Response(
                json.dumps({'error': 'URL is required'}),
                status=400,
                headers={**cors_headers, 'Content-Type': 'application/json'}
            )
        
        if not url.startswith(('http://', 'https://')):
            return https_fn.Response(
                json.dumps({'error': 'URL must start with http:// or https://'}),
                status=400,
                headers={**cors_headers, 'Content-Type': 'application/json'}
            )
        
        logger.info(f'Scraping URL: {url}')
        
        # Scrape website
        result = scrape_website_data(url)
        
        logger.info(f'Successfully scraped: {url}')
        return https_fn.Response(
            json.dumps(result),
            status=200,
            headers={**cors_headers, 'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logger.error(f'Request error: {str(e)}', exc_info=True)
        return https_fn.Response(
            json.dumps({'error': str(e)}),
            status=500,
            headers={**cors_headers, 'Content-Type': 'application/json'}
        )

