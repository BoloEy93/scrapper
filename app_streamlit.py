import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(
    page_title="Page d'informations sur les ambulances (Ministère Santé Cameroun)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://minsante.cm/',
        'Report a bug': None,
        'About': "Cette application Streamlit récupère les résultats de recherche pour 'ambulance' sur le site du Ministère de la Santé du Cameroun et les affiche au format JSON."
    }
)

st.title("Page d'information sur les ambulances (Ministère Santé Cameroun)")
st.markdown("Récupération des résultats de recherche pour 'ambulance' depuis [https://minsante.cm/site/?q=fr/search/node/ambulance](https://minsante.cm/site/?q=fr/search/node/ambulance) et affichage au format JSON.")

SEARCH_URL = "https://minsante.cm/site/?q=fr/search/node/ambulance"

def scrape_search_results(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        results_container = soup.find('div', class_='content')
        results_data = []

        if results_container:
            result_items = results_container.find_all('div', class_='views-row')
            for item in result_items:
                title_element = item.find('h3', class_='title')
                title = title_element.a.text.strip() if title_element and title_element.a else None
                link = "https://minsante.cm" + title_element.a['href'] if title_element and title_element.a and 'href' in title_element.a.attrs else None
                date_element = item.find('span', class_='date')
                date = date_element.text.strip() if date_element else None
                body_element = item.find('div', class_='search-snippet-info')
                body = body_element.text.strip() if body_element else None

                result_item = {
                    "title": title,
                    "link": link,
                    "date": date,
                    "body": body
                }
                results_data.append(result_item)
        return results_data
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de connexion au site du Ministère de la Santé: {e}"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Erreur HTTP lors de la récupération de la page: {e}"}
    except Exception as e:
        return {"error": f"Une erreur inattendue s'est produite: {e}"}

if st.button("Récupérer les résultats de recherche (Ambulance) au format JSON"):
    with st.spinner(f"Récupération des résultats depuis {SEARCH_URL}..."):
        search_results = scrape_search_results(SEARCH_URL)
        st.subheader("Données JSON:")
        st.code(json.dumps(search_results, indent=4), language="json")
        st.download_button(
            label="Télécharger les données JSON",
            data=json.dumps(search_results, indent=4),
            file_name="minsante_ambulance_search_results.json",
            mime="application/json",
        )
