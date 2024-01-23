import pickle
import streamlit as st
import networkx as nx
import spacy

st.title("Agronomy Annotator")


@st.cache_resource
def load_matcher():
    with open("matcher.pkl", "rb") as file:
        matcher = pickle.load(file)
    return matcher


@st.cache_resource
def load_nlp_model():
    nlp = spacy.load("en_core_web_trf", disable=["ner"])
    return nlp


matcher = load_matcher()
nlp = load_nlp_model()

txt = st.text_area(label="text", label_visibility="collapsed")
analyze = st.button(label="Analyze")

if analyze:
    doc = nlp(txt)

    for sent in doc.sents:
        matches = matcher(sent)

        if matches:
            G = nx.Graph()
            G.add_nodes_from({w for t in matches for w in t[1]})
            G.add_edges_from([t[1] for t in matches if len(t[1]) == 2])
            for t in matches:
                if len(t[1]) > 2:
                    nx.add_path(G, t[1])

            st.markdown("---")
            st.markdown(sent.text)
            st.markdown(
                "**Entities**: *"
                + "*, *".join(
                    [
                        " ".join([sent[i].text for i in sorted(list(ent))])
                        for ent in sorted(
                            [list(cc) for cc in nx.connected_components(G)]
                        )
                    ]
                )
                + "*"
            )
