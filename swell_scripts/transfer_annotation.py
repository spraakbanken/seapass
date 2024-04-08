import conllu

# transfer annotation from an annotated target TokenList to an unannotated
# sentence in string form, assuming WORD ORDER ERRORS ONLY
def transfer_annotation(trg_tokens, org_sent, meta={}):
    org_forms = org_sent.split()
    org_tokens = []
    trg_tokens = trg_tokens.copy()
    for (i,word) in enumerate(org_forms):
        for (j,trg_token) in enumerate(trg_tokens):
            if trg_token["misc"] and "Transferred=True" in trg_token["misc"]: # already used
                continue
            # lowercase bc wrong order can affect capitalization
            if trg_token["form"].lower() == word.lower():
                # build org_token by modifying indices of trg_token
                org_token = trg_token.copy()
                org_token["id"] = i + 1
                try:
                    if trg_token["deprel"].lower() not in ["root", "_"]:
                        trg_dephead = trg_tokens[int(trg_token["head"]) - 1]
                        # there might be more than one when a token is repeated, so...
                        possible_depheads = [i for (i,org_form) in enumerate(org_forms) if org_form.lower() == trg_dephead["form"].lower()]
                        # ...get the closest one (heuristic!)
                        org_token["head"] = min(possible_depheads, key=lambda d: abs(i - d)) + 1
                    else:
                        org_token["head"] = 0
                except Exception as e:
                    print(e)
                    print("transfer_annotation failed for sentence {}.".format(trg_tokens.metadata["sent_id"]))
                    print("please check trg/uncorrupted file tokenization")

                org_tokens.append(org_token)
                trg_tokens[j]["misc"] = "Transferred=True"
                break
    return conllu.TokenList(org_tokens, metadata=meta)


if __name__ == "__main__":
    with open("data/swell/org.txt") as f:
        org = f.readlines()
    # trg_gold.conllu is the result of automatically parsing trg.txt with 
    # UDPipe 2 and manually fixing the errors 
    with open("data/swell/trg_gold.conllu") as f: 
        trg_conllu = f.read()
    trg = conllu.parse(trg_conllu)
    # org_silver.conllu will need some minor fixes, the CoNLL-U validator
    # helps finding most of the problems. This is due to the fact that we
    # deal with repeated tokens through a heuristic (cf. line 23) 
    with open ("data/swell/org_silver.conllu", "w") as f:
        for i in range(len(trg)):
            f.write(transfer_annotation(trg[i], org[i], meta=trg.metadata).serialize())
