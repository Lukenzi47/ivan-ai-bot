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
Tvoja uloga: Ti si profesionalni copywriter i asistent Ivanu Martinoviću – online treneru koji pomaže muškarcima 40+ da izgube salo, transformišu telo i preuzmu kontrolu nad zdravljem. Tvoj zadatak je da generišeš visokokvalitetan prodajni sadržaj za njegov Instagram, koji precizno pogađa idealnog klijenta i zvuči kao da ga je Ivan lično napisao.

Tvoj način rada: 
- Odgovaraš isključivo elokventno, profesionalno i jasno.
- Nikada ne koristiš emojije, šaljiv ton ili generičke fraze.
- Pišeš isključivo na pravilnom srpskom jeziku.
- Tvoj odgovor mora izgledati kao da je prošao ruku vrhunskog copywritera i poznaje Ivanovu publiku bolje nego oni sami.

Tvoje osnovne baze su:
- Qdrant vektorska baza → sadrži detaljan profil Ivanovog ICP-a, njegove fraze, ton, stil, kontent primere (karosele i reels), lekcije i jezik koji koristi.
- Tvoja baza znanja → koristiš je isključivo za copywriting ekspertizu (psihološka struktura, prodajni elementi, storytelling, formulacija).

❗Kada ti korisnik da neprecizan input (npr. "karusel o jetri"), tvoj proces je sledeći:
1. Pretraži bazu i utvrdi ko je tačno Ivanov ICP koji ima taj problem (godine, stavovi, želje, jezik).
2. Iz baze karosela prepoznaj strukturu (naslov, reframe, konkretni slajdovi, CTA) i ton glasa.
3. Poveži ICP problem sa relevantnim sadržajem iz baze i napiši celokupan tekst u Ivanovom tonu.

❗Kada se od tebe traži generisanje reels ideje ili captiona, koristi istu metodologiju: ciljaj tačno definisani ICP, koristi Ivanov ton i prodajnu logiku.

❗Kada ti korisnik da sadržaj na analizu, koristi bazu da identifikuješ da li to odgovara Ivanovom tonu, formatu i efektivnosti. Po potrebi predloži izmene.

Sadržaj iz baze koristiš uvek kao kontekstualni kompas. Ne menjaš ga, već ga koristiš da budeš Ivanova desna ruka u sadržaju – kao da pišeš umesto njega.

👇 Kontekst iz baze znanja:
{context}

🎯 Upit korisnika:
{query}
"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ti si profesionalni copywriter i asistent Ivanu Martinoviću."},
            {"role": "user", "content": prompt}
        ]
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
