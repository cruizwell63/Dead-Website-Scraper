import requests 
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import time


def scrape_from_wayback(url):
    api_url = f'http://web.archive.org/cdx/search/cdx?url={url}&collapse=digest&output=json'
    response = requests.get(api_url)
    return json.loads(response.text)

def extract_content(wayback_url):
    content = []

    print('Extracting content')
    for url in wayback_url:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            paragraphs = [p.text for p in soup.find_all('p')]
            headings = [h.text for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
            meta_data = {
                            (meta.get('name') or meta.get('property') or meta.get('http-equiv') or '').strip(): meta.get('content', '').strip()
                            for meta in soup.find_all('meta')
                            if meta.get('name') or meta.get('property') or meta.get('http-equiv')
                        }
            content.append({
                'url': url,
                'headings': headings,
                'paragraphs': paragraphs,
                'images': images,
                'meta_data': meta_data
            })
            
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')
    print('Content extracted')
    return content

def data_to_xml(data, filename):
    root = ET.Element('data')

    print('Creating XML file')
    for entry in data:
        entry_element = ET.SubElement(root, 'entry')

        url_element = ET.SubElement(entry_element, "url")
        url_element.text = entry['url']

        p_element = ET.SubElement(entry_element, "paragraphs")
        for paragraph in entry['paragraphs']:
            p = ET.SubElement(p_element, "paragraph")
            p.text = paragraph

        h_element = ET.SubElement(entry_element, "headings")
        for heading in entry['headings']:
            h = ET.SubElement(h_element, "heading")
            h.text = heading

        img_element = ET.SubElement(entry_element, "images")
        for image in entry['images']:
            img = ET.SubElement(img_element, "image")
            img.text = image

        meta_elem = ET.SubElement(entry_element, "meta_data")
        for key, value in entry['meta_data'].items():  
            if key:
                meta_tag = ET.SubElement(meta_elem, "meta", name=key)
                meta_tag.text = value

      
    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print('XML file created successfully')

if __name__ == "__main__":
    target_url = 'https://www.geeksugar.com'  # Replace with the target domain
    archived_data = scrape_from_wayback(target_url)

    
    url_list = []
    for entry in archived_data[1:6]:  # Limit to the first 5 entries
        timestamp = entry[1]
        original_url = entry[2]
        wayback_url = f'https://web.archive.org/web/{timestamp}/{original_url}'
        url_list.append(wayback_url)

    # Extract content from the archived pages
    scraped_content = extract_content(url_list)
    # Export the scraped content to XML
    data_to_xml(scraped_content, 'wayback_scrape.xml')

    print("Data scraped is exported to wayback_scrape.xml.")


