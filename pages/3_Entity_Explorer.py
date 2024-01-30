import json
import streamlit as st

st.set_page_config(page_title="Entity Explorer", page_icon="🔎")

st.markdown("# Entity Explorer")


@st.cache_data
def load_entities():
    with open("./data/vocabulary.json", "r") as file:
        ents = json.load(file)

    e_alpha = []
    e_num = []
    e_sym = []
    for e in sorted(ents.keys()):
        if e[0].isalpha():
            e_alpha.append(e)
        elif e[0].isdigit():
            e_num.append(e)
        else:
            e_sym.append(e)
    entities_names = e_alpha + e_num + e_sym

    return ents, entities_names


entities, entities_names = load_entities()

ent = st.selectbox(
    label="entities_selection",
    options=entities_names,
    index=None,
    label_visibility="collapsed",
    placeholder="Select an entity...",
)

if ent:
    st.dataframe(
        dict(sorted(entities[ent].items(), key=lambda x: -x[1])),
        width=1200,
        height=500,
        column_config={
            "": "Entity",
            "value": st.column_config.NumberColumn("Count"),
        },
    )
