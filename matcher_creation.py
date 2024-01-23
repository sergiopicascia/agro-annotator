import json
import pickle
import spacy
from spacy.matcher import DependencyMatcher
import periodictable

# load vocabulary of patterns
with open("./data/patterns.json", "r") as file:
    patterns = json.load(file)

# load model
nlp = spacy.load("en_core_web_trf", disable=["ner"])

# allowed part of speech
pos = ["NOUN", "PROPN", "VERB", "NUM", "SCONJ", "ADV", "INTJ", "ADJ", "X"]

# allowed dependencies
deps = ["amod", "compound", "nmod", "advmod", "npadvmod", "acl"]

# extracting keywords
expressions = [e for exps in patterns.values() for e in exps]
high_level_patterns = [
    (t.lemma_, t.pos_) for doc in nlp.pipe(expressions) for t in doc if t.pos_ in pos
]

# chemical elements
high_level_patterns.extend(
    [(element.name, "NOUN") for element in list(periodictable.elements)[1:]]
)
high_level_patterns.extend(
    [(element.symbol, "NOUN") for element in list(periodictable.elements)[1:]]
)

high_level_patterns = set(high_level_patterns)

# configuring matcher
matcher = DependencyMatcher(nlp.vocab, validate=True)

for kw, pos in high_level_patterns:
    matcher.add(
        kw.upper() + "_" + pos.upper(),
        [
            # kw only
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {
                        "LEMMA": kw,
                        "POS": {"IN": ["NOUN", "PROPN", "VERB"]},
                    },
                },
            ],
            # kw with mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {"LEMMA": kw, "POS": pos},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
            ],
            # kw only with mod with mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {"LEMMA": kw, "POS": pos},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_MOD",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
            ],
        ],
    )

    matcher.add(
        kw.upper() + "_" + pos.upper() + "_MOD",
        [
            # kw as mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {
                        "LEMMA": kw,
                        "POS": pos,
                        "DEP": {"IN": deps},
                    },
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": "<++",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {},
                },
            ],
        ],
    )

    matcher.add(
        kw.upper() + "_NOT_" + pos.upper(),
        [
            # kw in other pos with mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {"LEMMA": kw, "POS": {"NOT_IN": [pos]}},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
            ],
            # kw in other pos with mod with mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {"LEMMA": kw, "POS": {"NOT_IN": [pos]}},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
                {
                    "LEFT_ID": f"{kw.upper()}_MOD",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_MOD_MOD",
                    "RIGHT_ATTRS": {"DEP": {"IN": deps}},
                },
            ],
        ],
    )

    matcher.add(
        kw.upper() + "_NOT_" + pos.upper() + "_MOD",
        [
            # kw in other pos as mod
            [
                {
                    "RIGHT_ID": f"{kw.upper()}_ANCHOR",
                    "RIGHT_ATTRS": {
                        "LEMMA": kw,
                        "POS": {"NOT_IN": [pos]},
                        "DEP": {"IN": deps},
                    },
                },
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": "<++",
                    "RIGHT_ID": f"{kw.upper()}_MOD",
                    "RIGHT_ATTRS": {},
                },
            ],
        ],
    )

    matcher.add(
        kw.upper() + "_" + pos.upper() + "_NEG",
        [
            # kw negated
            [
                {"RIGHT_ID": f"{kw.upper()}_ANCHOR", "RIGHT_ATTRS": {"LEMMA": kw}},
                {
                    "LEFT_ID": f"{kw.upper()}_ANCHOR",
                    "REL_OP": ">--",
                    "RIGHT_ID": f"{kw.upper()}_NEG",
                    "RIGHT_ATTRS": {"LEMMA": {"IN": ["no", "not"]}},
                },
            ]
        ],
    )

with open("./data/matcher.pkl", "wb") as file:
    pickle.dump(matcher, file)
