from sklearn.model_selection import train_test_split
import csv  

ALIGNED_SENTS = "data/aligned_sentences.tsv"

if __name__ == "__main__":
    with open(ALIGNED_SENTS) as infile:
        # ignore column names
        full = list(csv.reader(infile, delimiter="\t"))[1:]
    filtered = []
    for [src,trg,essay_id,lables_str] in full:
        labels = lables_str.split(",")
        if labels and all([label in ["S-Adv", "S-FinV", "S-WO", "O-Cap"] and labels != ["O-Cap"] for label in labels]):
            filtered.append([src,trg,essay_id,lables_str])
    [train, test_dev] = train_test_split(filtered, test_size=0.2, random_state=4)
    [test, dev] = train_test_split(test_dev, test_size=0.5, random_state=4)
    with open("data/test.tsv", "w") as test_file:
        writer = csv.writer(test_file, delimiter="\t")
        writer.writerows(test)
    with open("data/dev.tsv", "w") as dev_file:
        writer = csv.writer(dev_file, delimiter="\t")
        writer.writerows(dev)
    with open("data/train.tsv", "w") as train_file:
        writer = csv.writer(train_file, delimiter="\t")
        writer.writerows(train)