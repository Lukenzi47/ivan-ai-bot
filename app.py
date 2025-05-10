import streamlit as st
import os
import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
#test
# KONFIGURACIJA
import streamlit as st
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

qdrant = QdrantClient(
    url="https://7fb35336-432e-4293-acd4-adf59c466d9d.eu-west-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.5WRidA4U5GxkC2UQzYlx_rCOir7_RUhrkxB-uf0UVSI"
)

COLLECTION_NAME = "ivanbase"

def search_qdrant(query_text):
    embedding = openai.embeddings.create(
        input=query_text,
        model="text-embedding-3-small"
    ).data[0].embedding

    collection_names = [
    "ivan_alfa_protokol",
    "ivan_biografija",
    "ivan_carousels",
    "ivan_faq_baza",
    "ivan_icp_goals",
    "ivan_idealni_klijent",
    "ivan_lekcije_za_klijente",
    "ivan_moja_prica",
    "ivan_reelsovi"
]
    all_hits = []

    for name in collection_names:
        try:
            hits = qdrant.search(
                collection_name=name,
                query_vector=embedding,
                limit=3
            )
            all_hits.extend(hits)
        except Exception as e:
            print(f"Greška u kolekciji {name}: {e}")

    # Sortiramo po skoriranju (relevantnosti)
    all_hits = sorted(all_hits, key=lambda x: x.score, reverse=True)[:5]
    return [
    hit.payload.get('content') or next(iter(hit.payload.values()), "")
    for hit in all_hits
    if hit.payload
]


def generate_response(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"""
Ti si profesionalni copywriter i asistent Ivanu Martinoviću — treneru koji pomaže muškarcima 40+ da izgube salo, transformišu telo i uspostave kontrolu kroz svoj online program.

Tvoj zadatak je da napišeš predlog za Instagram objavu (karusel, reels tekst, caption) koji:

- pogađa probleme i uverenja muškaraca 40+ koji prate Ivana
- ne koristi generičke fraze, likove ili izmišljene scenarije
- ne pokušava da bude duhovit ili šokantan
- koristi realan, suptilan, autentičan ton
- je napisan kao predlog za Ivana — može ga iskoristiti direktno ili doraditi

📌 Koristi kontekst iz baze da razumeš:
- Ivanov kontent stil
- njegovog idealnog klijenta
- primere sadržaja koji je dobro prošao

📌 Ne pišeš kao Ivan. Pišeš kao njegov copywriting asistent.

📌 Ne izmišljaš karaktere, anegdote ili klišee.

📌 Napiši elokventan, pametno sročen predlog objave koji koristi strukturu (uvod, poenta, reframe, završnica), ali zvuči kao da dolazi od čoveka koji razume svog čitaoca.

📌 Pitanje koje ti Ivan postavlja:

{query}

📌 Koristan kontekst iz baze:

{context}

Na osnovu toga, napiši predlog pisanog sadržaja — kao da ga Ivan čita prvi put i odmah vidi da je vredan objave.
"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# STREAMLIT UI
st.title("Ivan AI Bot")
user_query = st.text_input("Postavi pitanje:")

if user_query:
    with st.spinner("Razmišljam..."):
        context = search_qdrant(user_query)
        answer = generate_response(user_query, context)
        st.markdown("**Ivan:**")
        st.write(answer)
