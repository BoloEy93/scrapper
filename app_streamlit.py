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
        search_results_ol = soup.select_one('ol.search-results.node-results')
        results_data = []

        if search_results_ol:
            list_items = search_results_ol.find_all('li')
            for item in list_items:
                title_element = item.select_one('h3.title a')
                snippet_element = item.select_one('div.search-snippet-info p.search-snippet')
                info_element = item.select_one('div.search-snippet-info p.search-info')

                title = title_element.text.strip() if title_element else None
                link = "https://minsante.cm" + title_element['href'] if title_element and 'href' in title_element.attrs else None
                snippet = snippet_element.text.strip() if snippet_element else None
                info = info_element.text.strip() if info_element else None

                result_item = {
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "info": info
                }
                results_data.append(result_item)
        else:
            return {"error": "Impossible de trouver la liste des résultats de recherche sur la page."}

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
        st.code(json.dumps(search_results, indent=4, ensure_ascii=False), language="json")
        if not isinstance(search_results, dict) or "error" not in search_results:
            st.download_button(
                label="Télécharger les données JSON",
                data=json.dumps(search_results, indent=4, ensure_ascii=False),
                file_name="minsante_ambulance_search_results.json",
                mime="application/json",
            )
        else:
            st.error(search_results["error"])
