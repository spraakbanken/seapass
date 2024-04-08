import argparse
import conllu
import pandas as pd
from sentence_eval import scorer

parser = argparse.ArgumentParser()
parser.add_argument('test_path')
parser.add_argument('pred_path')
parser.add_argument('--outfile', default='out')
args = parser.parse_args()
    
with open(args.test_path, 'r', encoding='utf-8') as t, open(args.pred_path, 'r', encoding='utf-8') as p:
    tst, prd = t.read(), p.read()
    test_sents, pred_sents = conllu.parse(tst), conllu.parse(prd)
        
scores = scorer(pred_sents,test_sents)
results = pd.DataFrame(scores)
results.columns =['UAS', 'LAS']
file = f'evaluations/{args.outfile}.csv'
results.to_csv(file)