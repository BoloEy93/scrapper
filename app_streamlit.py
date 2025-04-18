import requests
from bs4 import BeautifulSoup
import json

def scrape_minsante_ambulance_news(url):
    """
    Scrapes the titles and links of ambulance-related news from the provided
    Minsanté search results page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        search_results = soup.select('ol.search-results.node-results > li')
        ambulance_news = []
        for item in search_results:
            title_element = item.select_one('h3.title a')
            snippet_element = item.select_one('div.search-snippet-info p.search-snippet')
            info_element = item.select_one('div.search-snippet-info p.search-info')

            if title_element:
                title = title_element.text.strip()
                link = "https://minsante.cm" + title_element['href']
                snippet = snippet_element.text.strip() if snippet_element else None
                info = info_element.text.strip() if info_element else None
                ambulance_news.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'info': info
                })
        return ambulance_news
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

if __name__ == "__main__":
    search_url = "https://minsante.cm/site/?q=fr/search/node/ambulance"
    ambulance_data = scrape_minsante_ambulance_news(search_url)

    if ambulance_data:
        print(json.dumps(ambulance_data, indent=4, ensure_ascii=False))

        # You can save this to a JSON file
        with open('minsante_ambulance_news.json', 'w', encoding='utf-8') as f:
            json.dump(ambulance_data, f, indent=4, ensure_ascii=False)
        print("\nData saved to minsante_ambulance_news.json")
    else:
        print("No ambulance news found on the page.")
