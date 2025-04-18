import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(
    page_title="Actualités Santé -OMS Cameroun",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.afro.who.int/',
        'Report a bug': None,
        'About': "Cette application Streamlit récupère les actualités du Cameroun depuis le site de l'OMS Afrique et les affiche au format JSON."
    }
)

st.title("Actualités OMS Cameroun")
st.markdown("Récupération des dernières actualités du Cameroun depuis [https://www.afro.who.int/countries/cameroon/news](https://www.afro.who.int/countries/cameroon/news)")

NEWS_URL = "https://www.afro.who.int/countries/cameroon/news"

# Add a User-Agent header to mimic a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_news(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        news_container = soup.find('div', class_='view-content')
        news_data = []

        if news_container:
            news_items = news_container.find_all('div', class_='views-row')
            for item in news_items:
                title_element = item.find('h3', class_='news-title')
                title = title_element.a.text.strip() if title_element and title_element.a else None
                link = "https://www.afro.who.int" + title_element.a['href'] if title_element and title_element.a and 'href' in title_element.a.attrs else None
                date_element = item.find('div', class_='news-created')
                date = date_element.text.strip() if date_element else None
                image_container = item.find('div', class_='field--name-field-image')
                image_url = "https://www.afro.who.int" + image_container.img['src'] if image_container and image_container.img and 'src' in image_container.img.attrs else None
                image_alt = image_container.img.get('alt') if image_container and image_container.img else None
                summary_element = item.find('div', class_='field--name-field-preamble')
                summary = summary_element.text.strip() if summary_element else None

                news_item = {
                    "title": title,
                    "link": link,
                    "date": date,
                    "image_url": image_url,
                    "image_alt": image_alt,
                    "summary": summary
                }
                news_data.append(news_item)
        return news_data
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de connexion au site de l'OMS: {e}"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Erreur HTTP lors de la récupération de la page: {e}"}
    except Exception as e:
        return {"error": f"Une erreur inattendue s'est produite: {e}"}

if st.button("Récupérer les actualités au format JSON"):
    with st.spinner(f"Récupération des actualités depuis {NEWS_URL}..."):
        news_data = scrape_news(NEWS_URL, headers)
        st.subheader("Données JSON:")
        st.code(json.dumps(news_data, indent=4), language="json")
        st.download_button(
            label="Télécharger les données JSON",
            data=json.dumps(news_data, indent=4),
            file_name="oms_cameroun_actualites.json",
            mime="application/json",
        )
