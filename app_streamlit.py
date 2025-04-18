import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

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

# Initialize session state for scraped data
if "scraped_ambulance_data" not in st.session_state:
    st.session_state.scraped_ambulance_data = []

def fetch_and_store_data():
    data = scrape_search_results(SEARCH_URL)
    st.session_state.scraped_ambulance_data = data

if not st.session_state.scraped_ambulance_data:
    with st.spinner("Récupération initiale des données..."):
        fetch_and_store_data()

# Extract the full URL path
query_params = st.experimental_get_query_params()

# Check if the user is accessing the 'ambulance_data' path
if "ambulance_data" in st.experimental_get_query_params():
    # Serve JSON data directly
    st.json(st.session_state.scraped_ambulance_data)
else:
    # Default Streamlit app view
    st.title("Page d'information sur les ambulances (Ministère Santé Cameroun)")
    st.markdown("Récupération des résultats de recherche pour 'ambulance' depuis [https://minsante.cm](https://minsante.cm).")

    if st.button("Mettre à jour les données"):
        with st.spinner("Mise à jour des données..."):
            fetch_and_store_data()

    st.subheader("Données JSON:")
    st.code(json.dumps(st.session_state.scraped_ambulance_data, indent=4, ensure_ascii=False), language="json")
