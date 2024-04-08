import argparse
import conllu
import os.path
import random
import itertools

ADV_RELS = ["advmod", "advcl"]
SUBJ_RELS = ["nsubj", "csubj"]
SWELL_LABELS = ["S-Adv", "S-FinV", "S-WO"]

# return deprel without subtypes, e.g. nsubj:pass -> nsubj
def base_deprel(deprel):
    return deprel.split(":")[0]

# return True if the given token is a finite verb, False otherwise. Works for
# both VERB and AUX tokens
def is_finv(tok):
    return tok["feats"] and "VerbForm" in tok["feats"] and tok["feats"]["VerbForm"] == "Fin"

# return True if the given token is an imperative, False otherwise. Works for
# both VERB and AUX tokens
def is_imp(tok):
    return tok["feats"] and "Mood" in tok["feats"] and tok["feats"]["Mood"] == "Imp"

# return True if the given token is a syntactic subject, False otherwise
def is_subj(tok):
    return base_deprel(tok["deprel"]) in SUBJ_RELS

# give a token and the sentence it belongs to as a TokenList, return the 
# token's syntactic head
def dephead(token, sent):
    return sent[token["head"] - 1]

# return a list of all subtrees of a given TokenTree
def all_subtrees(tree):
    return [tree] + list(itertools.chain.from_iterable([all_subtrees(child) for child in tree.children]))

# given a token and the tree for the sentence it belongs to, return the 
# subtree rooted in the token
def find_subtree(head, tree):
    return [subtree for subtree in all_subtrees(tree) if subtree.token["id"] == head["id"]][0]

# given a sentence (as TokenList) and a (finite verb) token, recursively
# find the subject (if the token does not directly have a subject dependent, 
# e.g. because it is a conj or aux, go up to its parent and look for a subj
# again)
def find_subj(sent, finv):
    subjs = [tok for tok in sent if tok["head"] == finv["id"] and is_subj(tok)]
    if subjs: # base case 1: found a subj
        return (subjs[0], finv) # there should always only be one subj
    if finv["deprel"] in ["root", "_"]: # base case 2: root
        return None
    # recursive case
    return find_subj(sent, dephead(finv, sent))

# given a token and the sentence it belongs to, return the TokenList
# (segment) corresponding to the phrase/subtree rooted in the token
def phrase(token, sent):
    tree = sent.to_tree()
    return conllu.parse(find_subtree(token, tree).serialize())[0] 

def adjust_indices(sent):
    # map old IDs to new, sequential ones
    old_new = {}
    new_sent = sent.copy()
    for i in range(len(new_sent)): 
        old_new[new_sent[i]["id"]] = i + 1
    for i in range(len(new_sent)):
        if not new_sent[i]["head"] == 0:  
            new_sent[i]["head"] = old_new[new_sent[i]["head"]]
        new_sent[i]["id"] = old_new[new_sent[i]["id"]]
    
    return new_sent
        
# move a phrase of a given sentence with respect to a pivot token.
# Returns a new TokenList (does not adjust the indices just yet)
def move_phrase(sent, phrase, pivot):
    indices = [token["id"] for token in phrase]
    # phrase range
    start,end = min(indices),max(indices)
    prefix = [token for token in sent if token["id"] < start and token["id"] != pivot["id"]]
    postfix = [token for token in sent if token["id"] > end and token["id"] != pivot["id"]]
    if end < pivot["id"]: # mv phrase to the right of the head
        scrambled = prefix + [pivot] + phrase + postfix
    else: # mv phrase to the left of the head 
        scrambled = prefix + phrase + [pivot] + postfix

    return scrambled

def corrupt(sent):
    # try corrupt sentence with S-Adv
    try:
        advs = [tok for tok in sent if base_deprel(tok["deprel"]) in ADV_RELS]
        adv = random.choice(advs)
        adv_phrase = phrase(adv, sent)
        sadv_sent = move_phrase(sent,adv_phrase,dephead(adv,sent))
    except:
        sadv_sent = None
    
    # try corrupt sentence with S-FinV
    try:
        # select viable finite verbs (excludes imperatives bc they don't have
        # an explicit subject)
        finvs = [tok for tok in sent if is_finv(tok) and not is_imp(tok)]
        finv = random.choice(finvs)
        (subj, finv) = find_subj(sent, finv)
        subj_phrase = phrase(subj, sent)
        sfinv_sent = move_phrase(sent, subj_phrase, finv)
    except:
        sfinv_sent = None
        
    # simplistic strategy: just swap two adjacent tokens. This is far from 
    # ideal and might result in errors that are quite unlikely, but it should
    # never fail unless the sentence has length 1, in which case we have to
    # leave it as it is
    if len(sent) > 1:
        i = random.randint(0,len(sent) - 2) # -2 cause randint is crazy
        j = i + 1
        swo_sent = sent.copy()
        swo_sent[i] = sent[j]
        swo_sent[j] = sent[i]
    else:
        swo_sent = sent

    # select what label & sentence to use/keep, kinda based on SweLL freqs
    if sadv_sent and sfinv_sent:
        [label] = random.choices(SWELL_LABELS, [0.5, 0.4, 0.1])
    elif sadv_sent and (not sfinv_sent):
        label = "S-Adv"
    elif (not sadv_sent) and sfinv_sent:
        label = "S-FinV"
    else:
        label = "S-WO"
    if label == "S-Adv":
        scrambled_sent = sadv_sent
    elif label == "S-FinV":
        scrambled_sent = sfinv_sent
    else:
        scrambled_sent = swo_sent
    adjusted_sent = adjust_indices(scrambled_sent)

    # simplistically adjust case
    for i in range(len(adjusted_sent)):
        adjusted_sent[i]["form"] = adjusted_sent[i]["form"].lower() if adjusted_sent[i]["upos"] != "PROPN" else adjusted_sent[i]["form"]
    adjusted_sent[0]["form"] = adjusted_sent[0]["form"].title()
    
    # generate metadata
    scrambled_str = " ".join([token["form"] for token in adjusted_sent])
    meta = sent.metadata
    scrambled_meta = meta.copy()
    scrambled_meta["uncorrupted_text"] = meta["text"]
    scrambled_meta["text"] = scrambled_str
    scrambled_meta["error_label"] = label 

    return conllu.TokenList(adjusted_sent, metadata=scrambled_meta)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("treebank", help=".conllu treebank to be corrupted")
    args = parser.parse_args()

    inpath = args.treebank
    # the output treebank is created in the same folder as the original one,
    # same name with added -corrupted
    (name,ext) = os.path.splitext(inpath) 
    outpath = "{}-corrupted{}".format(name,ext)

    with open(inpath) as infile, open(outpath, "w") as outfile:
        intext = infile.read()
    
        insents = conllu.parse(intext)
    
        for insent in insents:
            outsent = corrupt(insent)
            outfile.write(outsent.serialize())

