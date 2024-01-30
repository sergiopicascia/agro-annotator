import json
import random
import os
import rispy
import streamlit as st
import streamlit_antd_components as sac

st.set_page_config(page_title="Article Explorer", page_icon="🔎")

st.markdown("# Article Explorer")

if "seed" not in st.session_state.keys():
    st.session_state["seed"] = ""

if "mode" not in st.session_state.keys():
    st.session_state["mode"] = "init"


def search_with_box():
    if st.session_state.selected_ent:
        st.session_state["mode"] = "search"
        st.session_state["seed"] = st.session_state.selected_ent
    else:
        st.session_state["mode"] = "init"


def re_search(i):
    st.session_state["seed"] = st.session_state[f"filter-{i}"]
    st.session_state.selected_ent = st.session_state["seed"]


@st.cache_data
def load_entities():
    with open("./data/ent2art.json", "r") as file:
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


@st.cache_data
def load_abstracts():
    abstracts = []
    for file in sorted(os.listdir("./data/papers/")):
        f = os.path.join("./data/papers/", file)
        with open(f, "r") as bib:
            entries = rispy.load(bib)
            for e in entries:
                if "abstract" in e:
                    abstracts.append((e["title"], e["abstract"]))
    return abstracts


@st.cache_data
def load_articles():
    with open("./data/art2ent.json", "r") as file:
        articles = json.load(file)
    return articles


entities, entities_names = load_entities()
abstracts = load_abstracts()
articles = load_articles()

if st.session_state["mode"] == "init" or st.session_state["mode"] == "search":
    ent = st.selectbox(
        label="entities_selection",
        key="selected_ent",
        options=entities_names,
        index=None,
        label_visibility="collapsed",
        placeholder="Select an entity...",
        on_change=search_with_box,
    )

if st.session_state["mode"] == "search":
    for i in random.sample(
        entities[st.session_state["seed"]],
        min([20, len(entities[st.session_state["seed"]])]),
    ):
        st.markdown("---")
        st.markdown(f"### {abstracts[i][0]}")
        st.markdown(abstracts[i][1])

        with st.expander("**Entities**"):
            sac.buttons(
                [
                    sac.ButtonsItem(label=f"{e}", color="#262730")
                    for e in set(articles[str(i)])
                ],
                key=f"filter-{i}",
                index=None,
                variant="dashed",
                on_change=re_search,
                args=[i],
            )
