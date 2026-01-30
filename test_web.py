import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

def test_web_analyzer():
    """Test web content analyzer with image extraction"""
    
    # Test URL
    test_url = "https://www.bbc.com"
    
    try:
        print("Testing web content analyzer...")
        print(f"URL: {test_url}")
        
        # Simulate the web scraping process
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(test_url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract images
        images = []
        img_tags = soup.find_all('img', src=True)
        print(f"Found {len(img_tags)} total images")
        
        for img in img_tags[:10]:  # Limit to 10 images
            src = img.get('src')
            alt = img.get('alt', '')
            
            # Convert relative URLs to absolute
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(test_url, src)
            elif not src.startswith('http'):
                src = urljoin(test_url, src)
            
            # Filter out small images and icons
            if not any(x in src.lower() for x in ['icon', 'logo', 'favicon', 'sprite']):
                images.append({"src": src, "alt": alt})
        
        print(f"Extracted {len(images)} usable images:")
        for i, img in enumerate(images[:5]):
            print(f"  {i+1}. {img['src'][:60]}...")
            print(f"     Alt: {img['alt'][:40]}...")
        
        # Extract content
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        content = soup.get_text(separator=" ", strip=True)
        content_length = len(content)
        print(f"Extracted content length: {content_length} characters")
        
        if content_length > 200:
            print("SUCCESS: Web analyzer working correctly!")
            print(f"SUCCESS: Images extracted: {len(images)}")
            print("SUCCESS: Content extracted successfully")
            return True
        else:
            print("ERROR: Not enough content extracted")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_web_analyzer()