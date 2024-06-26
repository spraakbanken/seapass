# SEAPaSS 
Data and code for the paper [_Synthetic-Error Augmented Parsing of Swedish as a Second language_](https://aclanthology.org/2024.mwe-1.7/) by Arianna Masciolini, Emilie Marie Carreau Francis, Maria Irena Szawerna

## Data and preprocessing scripts
- [SweLL-derived evaluation set](data/swell/), obtained by:
  1. extracting sentence-correction pairs from the full [SweLL-gold corpus](https://spraakbanken.gu.se/resurser/swell-gold) with the [extract_sentence_pairs.py script](swell_scripts/extract_sentence_pairs.py)
  1. filtering out sentences that do not exclusively contain word order errors with the [filter.py](swell_scripts/filter.py)
  1. parsing the resulting corrected sentences with the `swedish-talbanken-ud-2.12-230717` UDPipe 2 model
  2. applying the [transfer_annotation.py script](swell_scripts/transfer_annotation.py) to transfer UD annotation from correction hypotheses to learner originals
- [corrupted version of the Talbanken Swedish treebank](data/corrupted_talbanken/), obtained by processing [UD_Swedish-Talbanken](https://github.com/UniversalDependencies/UD_Swedish-Talbanken) with the [corrupt.py script](preproc_scripts/corrupt.py)
- _we have also used the original version of [UD_Swedish-Talbanken](https://github.com/UniversalDependencies/UD_Swedish-Talbanken), which is not included in the repository_

- [mix_treebanks.py](mix_treebanks.py) combines and creates splits for normative and corrupted data in different configurations for the various parsing experiments

## Training and MaChAmp configurations
For training our models we have used the [MaChAmp toolkit](https://machamp-nlp.github.io/). The configurations for the training can be found in the [machamp_configs](machamp_configs/) folder. 

## Evaluation
- [swell_scripts/prune.py](swell_scripts/prune.py) is used to isolate ungrammatical segments for the targeted evaluation
- [eval_scripts/](eval_scripts/) contains two evaluation scripts:
  - [sentence_eval.py](eval_scripts/sentence_eval.py) calculates LAS and UAS scores
  - [sentence_scoring.py](eval_scripts/sentence_scoring.py) is used to run the scorer and present the result in a readable format

## License
This code is released under the [CRAPL academic-strength open source license](https://matt.might.net/articles/crapl/).
