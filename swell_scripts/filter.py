from sklearn.model_selection import train_test_split
import csv  
import sys

# usage python filter.py PATH-TO-OUTPUT-OF-EXTRACT-SENTENCE-PAIRS.tsv
# the output is a file called filtered.tsv

if __name__ == "__main__":
    tsv = sys.argv[1]
    with open(tsv) as infile:
        # ignore column names
        full = list(csv.reader(infile, delimiter="\t"))[1:]
    filtered = []
    for [src,trg,essay_id,lables_str] in full:
        labels = lables_str.split(",")
        if labels and all([label in ["S-Adv", "S-FinV", "S-WO", "O-Cap"] and labels != ["O-Cap"] for label in labels]):
            filtered.append([src,trg,essay_id,lables_str])
    with open("data/filtered.tsv", "w") as out_file:
        writer = csv.writer(out_file, delimiter="\t")
        writer.writerows(filtered)