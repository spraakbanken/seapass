from argparse import ArgumentParser
import conllu
import os.path

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument(
        "trg_gold", 
        help="reference target hypothesis treebank")
    argparser.add_argument(
        "org_silver",
        help="automatically parsed learner sentences treebank to be evaluated"
    )
    args = argparser.parse_args()

    with open(args.trg_gold) as inf:
        trg_golds = conllu.parse(inf.read())
    with open(args.org_silver) as inf:
        org_silvers = conllu.parse(inf.read())
    
    pairs = zip(trg_golds,org_silvers)
    err_segs = []
    for (i, (trg_gold, org_silver)) in enumerate(pairs):
        # not supposed to happen but SweLL annoataion is not that perfect
        if not (len(trg_gold) == len(org_silver)):
            print(
                "skipping {} because org and trg are of different lengths"
                .format(" ".join([tok["form"] for tok in trg_gold]))
            )
            continue
        err_start = 0
        while trg_gold[err_start]["form"] == org_silver[err_start]["form"]:
            err_start += 1
        err_end = len(trg_gold) - 1
        while trg_gold[err_end]["form"] == org_silver[err_end]["form"]:
            err_end -= 1
        err_segs.append(
            (conllu.TokenList(trg_gold[err_start:err_end+1]), 
            conllu.TokenList(org_silver[err_start:err_end+1])))
    
    (trg_err_segs, org_err_segs) = zip(*err_segs)

    trg_err_str = "\n".join([seg.serialize() for seg in trg_err_segs])
    (trg_name,ext) = os.path.splitext(args.trg_gold)
    trg_outp = "{}-pruned{}".format(trg_name, ext)
    with open(trg_outp, "w") as outf:
        outf.write(trg_err_str)
        
    org_err_str = "\n".join([seg.serialize() for seg in org_err_segs])
    (org_name,ext) = os.path.splitext(args.org_silver)
    org_outp = "{}-pruned{}".format(org_name, ext)
    with open(org_outp, "w") as outf:
        outf.write(org_err_str)

            