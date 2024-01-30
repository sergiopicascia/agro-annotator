import os
from collections import defaultdict, Counter
import json
import pickle
import rispy
import spacy
import networkx as nx
from tqdm import tqdm

PATH = "../data/papers/"

papers = []
for file in sorted(os.listdir(PATH)):
    f = os.path.join(PATH, file)
    with open(f, "r") as bib:
        entries = rispy.load(bib)
        for e in entries:
            if "abstract" in e:
                papers.append(e["abstract"])

print(len(papers))

with open("../data/matcher.pkl", "rb") as file:
    matcher = pickle.load(file)

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_trf", disable=["ner"])

entities = defaultdict(Counter)

ent2art = defaultdict(list)
art2ent = defaultdict(list)

for idx, doc in enumerate(tqdm(nlp.pipe(papers, batch_size=128))):
    matches = matcher(doc)

    G = nx.Graph()
    G.add_nodes_from({w for t in matches for w in t[1]})
    G.add_edges_from([t[1] for t in matches if len(t[1]) == 2])
    for t in matches:
        if len(t[1]) > 2:
            nx.add_path(G, t[1])

    for ids in list(nx.connected_components(G)):
        ent = " ".join([doc[i].lemma_ for i in sorted(list(ids))]).lower()
        for i in ids:
            entities[doc[i].lemma_.lower()][ent] += 1
        ent2art[ent].append(idx)
        art2ent[idx].append(ent)

with open("../data/vocabulary.json", "w") as file:
    json.dump(entities, file, indent=4)

with open("../data/ent2art.json", "w") as file:
    json.dump(ent2art, file, indent=4)

with open("../data/art2ent.json", "w") as file:
    json.dump(art2ent, file, indent=4)
