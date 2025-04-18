import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Actualités OMS Cameroun",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.afro.who.int/',
        'Report a bug': None,
        'About': "Cette application Streamlit récupère et affiche les actualités du Cameroun depuis le site de l'OMS Afrique."
    }
)

st.title("Actualités OMS Cameroun")
st.markdown("Récupération des dernières actualités du Cameroun depuis [https://www.afro.who.int/countries/cameroon/news](https://www.afro.who.int/countries/cameroon/news)")

NEWS_URL = "https://www.afro.who.int/countries/cameroon/news"

with st.spinner(f"Récupération des actualités depuis {NEWS_URL}..."):
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver la section contenant les actualités
        news_container = soup.find('div', class_='view-content')

        if news_container:
            news_items = news_container.find_all('div', class_='views-row')

            if news_items:
                for item in news_items:
                    # Extraire le titre
                    title_element = item.find('h3', class_='news-title')
                    title = title_element.a.text.strip() if title_element and title_element.a else "Titre non trouvé"
                    link = "https://www.afro.who.int" + title_element.a['href'] if title_element and title_element.a and 'href' in title_element.a.attrs else "#"

                    st.subheader(f"[{title}]({link})")

                    # Extraire la date
                    date_element = item.find('div', class_='news-created')
                    date = date_element.text.strip() if date_element else "Date non trouvée"
                    st.markdown(f"**Date:** {date}")

                    # Extraire l'image (si présente)
                    image_container = item.find('div', class_='field--name-field-image')
                    if image_container and image_container.img and 'src' in image_container.img.attrs:
                        image_url = "https://www.afro.who.int" + image_container.img['src']
                        alt_text = image_container.img.get('alt', 'Image associée')
                        st.image(image_url, caption=alt_text, use_column_width=True)

                    # Extraire le résumé/extrait
                    summary_element = item.find('div', class_='field--name-field-preamble')
                    summary = summary_element.text.strip() if summary_element else "Résumé non trouvé"
                    st.markdown(summary)
                    st.markdown("---")

            else:
                st.info("Aucune actualité trouvée sur cette page.")
        else:
            st.warning("La section des actualités n'a pas pu être trouvée sur la page.")

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion au site de l'OMS: {e}")
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur HTTP lors de la récupération de la page: {e}")
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite: {e}")