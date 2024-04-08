import conllu
import argparse
import random
import math

# pud = 'sv_pud-ud'
# lines = 'sv_lines-ud'
talbanken = 'sv_talbanken-ud'

# add the name for our conll files
# swell = ''

# forbidden = ['sv-ud-train-4214']

random.seed(42)

def read_conllu(filename):
    with open(filename) as f:
        treebank = f.read()
    return conllu.parse(treebank)

def trim_treebank(treebank, trim):
    random.shuffle(treebank)
    if trim < len(treebank):
        return treebank[:trim]
    else:
        return treebank

def shuffle_and_recombine(treebank_list, trim):
    # output = trim_treebank(read_conllu(treebank_list[0]), trim)
    # if len(treebank_list) > 1:
    #     for i in range(1, len(treebank_list)):
    #         output += trim_treebank(read_conllu(treebank_list[i]), trim)
    # random.shuffle(output)
    uncorrupted = read_conllu(treebank_list[0])
    corrupted = read_conllu(treebank_list[1])
    
    assert len(uncorrupted) == len(corrupted)

    corrupted = filter_forbidden([corrupted, uncorrupted])
    
    random.shuffle(uncorrupted)
    random.shuffle(corrupted)
    
    cutoff = math.floor(trim*len(uncorrupted))
    if cutoff < len(corrupted):
        output = corrupted[:cutoff] + uncorrupted[cutoff:]
    else:
        output = corrupted
    random.shuffle(output)
    return output

def save_treebank(treebank, file):
    with open(file, 'w') as f:
        for sent in treebank:
            f.write(sent.serialize())
            
def filter_forbidden(treebanks):
    corrupted = []
    for i, sent in enumerate(treebanks[0]):  # corrupted
        if len(sent) == len(treebanks[1][i]):
            corrupted.append(sent)
    return corrupted


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("tsv", help="Path to the input TSV file")
    # parser.add_argument("org_conllu", help="Path to the CoNNL-U file for original sentences") 
    # parser.add_argument("trg_conllu", help="Path to the CoNNL-U file for target hypotheses") 
    
    # parser.add_argument('--pud', required=False, action='store_true', help='Whether or not to use the PUD treebank (only test set).')  # we are always using this one
    # parser.add_argument('--talbanken', required=False, action='store_true', help='Whether or not to use the Talbanken treebank.')  # we are not using those
    # parser.add_argument('--lines', required=False, action='store_true', help='Whether or not to use the Lines treebank.')
    parser.add_argument('--treebank_path', required=False, default='./data/', help='Path to the folder with all the treebanks.')
    # parser.add_argument('--train_trim', required=False, default=1000, help='The maximum number of sentences to take from a treebank in the train set.')
    # parser.add_argument('--test_dev_trim', required=False, default=100, help='The maximum number of sentences to take from a treebank in the test and dev sets.')
    parser.add_argument('--trim', required=False, default=0.15, help='The % of corrupted sentences.')
    parser.add_argument('--output_name', required=False, default='talbanken/sv-talbanken-ud-mix15', help='The core of the name for the output files.')
       
    
    args = parser.parse_args()
    
    # if not args.lines and not args.talbanken:
    #     print('You must choose at least one treebank with more than just a test set!')
    #     exit()
    
    # add our conll files
    # treebank_train_list = ['./data/WO/train_org.conllu']
    # treebank_dev_list = ['./data/WO/dev_org.conllu']
    # treebank_test_list = ['./data/WO/test_org.conllu']
    treebank_train_list = []
    treebank_dev_list = []
    treebank_test_list = []
    
    
    # if args.pud:
    #     treebank_test_list.append(args.treebank_path + pud + '-test.conllu')
    # if args.talbanken:
    #     treebank_train_list.append(args.treebank_path + talbanken + '-train.conllu')
    #     treebank_dev_list.append(args.treebank_path + talbanken + '-dev.conllu')
    #     treebank_test_list.append(args.treebank_path + talbanken + '-test.conllu')
    # if args.lines:
    #     treebank_train_list.append(args.treebank_path + lines + '-train.conllu')
    #     treebank_dev_list.append(args.treebank_path + lines + '-dev.conllu')
    #     treebank_test_list.append(args.treebank_path + lines + '-test.conllu')
    
    treebank_train_list.append(args.treebank_path + 'talbanken/' + talbanken + '-train.conllu')
    treebank_dev_list.append(args.treebank_path + 'talbanken/' + talbanken + '-dev.conllu')
    treebank_test_list.append(args.treebank_path + 'talbanken/' + talbanken + '-test.conllu')
    
    treebank_train_list.append(args.treebank_path + 'talbanken/' + talbanken + '-train-corrupted.conllu')
    treebank_dev_list.append(args.treebank_path + 'talbanken/' + talbanken + '-dev-corrupted.conllu')
    treebank_test_list.append(args.treebank_path + 'talbanken/' + talbanken + '-test-corrupted.conllu')
        
    # print(treebank_train_list, treebank_test_list, treebank_dev_list)
    
    test_treebank = shuffle_and_recombine(treebank_test_list, float(args.trim))
    dev_treebank = shuffle_and_recombine(treebank_dev_list, float(args.trim))
    train_treebank = shuffle_and_recombine(treebank_train_list, float(args.trim))
    
    save_treebank(test_treebank, args.treebank_path + args.output_name + '-test.conllu')
    save_treebank(dev_treebank, args.treebank_path + args.output_name + '-dev.conllu')
    save_treebank(train_treebank, args.treebank_path + args.output_name + '-train.conllu')
