# SnaPy
[![Build Status](https://travis-ci.com/justinnbt/SnaPy.svg?branch=master)](https://travis-ci.com/justinnbt/SnaPy)
[![PyPI version](https://badge.fury.io/py/snapy.svg)](https://badge.fury.io/py/snapy)
[![Downloads](https://pepy.tech/badge/snapy)](https://pepy.tech/project/snapy)
[![Python Version](https://img.shields.io/badge/python-3.6%20+-blue.svg)](https://pypi.org/project/snapy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
<br>
Python library for detecting near duplicate texts in a corpus at scale using Locality Sensitive Hashing.<br>
As described in Mining Massive Datasets http://infolab.stanford.edu/~ullman/mmds/ch3.pdf.

## Installation
Install SnaPy using: `pip install snapy`<br>
Install mmh3 library needed for Minhash using: `pip install mmh3`

## Quickstart Example
``` python
from snapy import MinHash, LSH

content = [
    'Jupiter is primarily composed of hydrogen with a quarter of its mass '
    'being helium',
    'Jupiter moving out of the inner Solar System would have allowed the '
    'formation of inner planets.',
    'A helium atom has about four times as much mass as a hydrogen atom, so '
    'the composition changes when described as the proportion of mass '
    'contributed by different atoms.',
    'Jupiter is primarily composed of hydrogen and a quarter of its mass '
    'being helium',
    'A helium atom has about four times as much mass as a hydrogen atom and '
    'the composition changes when described as a proportion of mass '
    'contributed by different atoms.',
    'Theoretical models indicate that if Jupiter had much more mass than it '
    'does at present, it would shrink.',
    'This process causes Jupiter to shrink by about 2 cm each year.',
    'Jupiter is mostly composed of hydrogen with a quarter of its mass '
    'being helium',
    'The Great Red Spot is large enough to accommodate Earth within its '
    'boundaries.'
]

labels = [1, 2, 3, 4, 5, 6, 7, 8, 9]
seed = 3


# Create MinHash object.
minhash = MinHash(content, n_gram=9, permutations=100, hash_bits=64, seed=3)


# Create LSH model.
lsh = LSH(minhash, labels, no_of_bands=50)


# Query to find near duplicates for text 1.
print(lsh.query(1, min_jaccard=0.5))
>>> [8, 4]


# Generate minhash signature and add new texts to LSH model.
new_text = [
    'Jupiter is primarily composed of hydrogen with a quarter of its mass being 
    'helium',
    'Jupiter moving out of the inner Solar System would have allowed the '
    'formation of inner planets.',
]

new_labels = ['doc1', 'doc2']

new_minhash = MinHash(new_text, n_gram=9, permutations=100, hash_bits=64, seed=3)

lsh.update(new_minhash, new_labels)


# Check contents of documents.
print(lsh.contains())
>>> [1, 2, 3, 4, 5, 6, 7, 8, 9, 'doc1', 'doc2']


# Remove text and label from model.
lsh.remove(5)
print(lsh.contains())
>>> [1, 2, 3, 4, 6, 7, 8, 9, 'doc1', 'doc2']


# Return adjacency list for all similar texts.
adjacency_list = lsh.adjacency_list(min_jaccard=0.55)
print(adjacency_list)
>>> {
        1: ['doc1', 4],
        2: ['doc2'], 
        3: [], 
        4: [1, 'doc1'], 
        6: [], 
        7: [], 
        8: [], 
        9: [], 
        'doc1': [1, 4], 
        'doc2': [2]
    }


# Returns edge list for use creating a weighted graph.
edge_list = lsh.edge_list(min_jaccard=0.5, jaccard_weighted=True)
print(edge_list)
>>> [
        ('doc2', 2, 1.0), 
        ('doc1', 1, 1.0), 
        ('doc1', 8, 0.5), 
        ('doc1', 4, 0.58), 
        (8, 1, 0.5), 
        (4, 1, 0.58)
    ]

```
## API Guide

### MinHash
Creates a MinHash object that contains matrix of Minhash Signatures for each text.

#### MinHash Parameters
```MinHash(text, n_gram=9, n_gram_type='char', permutations=100, hash_bits=64, seed=None)```<br><br>
<b>text: {list or ndarray}</b><br>
Iterable containing strings of text for each text in a corpus.<br><br>
<b>n_gram: int, optional, default: 9</b><br>
Size of each overlapping text shingle to break text into prior to hashing. Shingle size should be carefully selected dependant on average text length as too low a shingle size will yield false similarities, whereas too high a shingle size will fail to return similar documents.<br><br>
<b>n_gram_type: str, optional, default: 'char'</b><br>
Type of n gram to use for shingles, must be 'char' to split text into character shingles or 'term' to split text into overlapping sequences of words.<br><br>
<b>permutations: int, optional, default: 100</b><br>
Number of randomly sampled hash values to use for generating each texts minhash signature. Intuitively the larger the number of permutations, the more accurate the estimated Jaccard similarity between the texts but longer the algorithm will take to run.<br><br>
<b>hash_bits: int, optional, default: 64</b><br>
Hash value size to be used to generate minhash signatures from shingles, must be 32, 64 or 128 bit. Hash value size should be chosen based on text length and a trade off between performance and accuracy. Lower hash values risk false hash collisions leading to false similarities between documents for larger corpora of texts.<br><br>
<b>method: str, optional, default: 'multi_hash'</b><br>
Method for random sampling via hashing, must be 'multi_hash' or 'k_smallest_values'.<br>
If multi_hash selected texts are hashed once per permutation and the minimum hash value selected each time to construct a signature.<br>
If k_smallest_values selected each text is hashed once and k smallest values selected for k permutations. This method is much faster than multi_hash but far less stable.<br><br>
<b>seed: int, optional, default: None</b><br>
Seed from which to generate random hash function, necessary for reproducibility or to allow updating of the LSH model with new minhash values later.<br><br>

#### MinHash Properties
<b>n_gram: int</b><br>
```.n_gram```<br>
Returns size of each overlapping text shingle used to create minhash signatures.<br><br>
<b>n_gram_type: int</b><br>
```.n_gram_type```<br>
Returns type of n-gram used for text shingling.<br><br>
<b>permutations: int</b><br>
```.permutations```<br>
Returns number of permutations used to create signatures.<br><br>
<b>hash_bits: int</b><br>
```.hash_bits```<br>
Returns hash value size used to create signatures.<br><br>
<b>method: str</b><br>
```.method```<br>
Returns hashing method used in minhash function.<br><br>
<b>seed: int</b><br>
```.seed```<br>
Returns seed value used to generate random hashes in minhash function.<br><br>
<b>signatures: ndarray</b><br>
```.signatures```<br>
Returns matrix of text signatures generated by minhash function.<br>
n = text row, m = selected permutations.<br><br>

### LSH
Creates an LSH model of text similarity that can be used to return similar texts based on estimated Jaccard similarity.

#### LSH Parameters
```LSH(minhash=None, labels=None, no_of_bands=None)```<br><br>
<b>minhash, optional, default: None</b><br>
Minhash object containing minhash signatures returned by MinHash class.<br><br>
<b>labels: {list or ndarray}, optional, default: None</b><br>
List, array or Pandas series containing unique labels for each text in minhash object signature. This should be provided in the same order as texts passed to the MinHash class. Example labels include filepaths and database ids.<br><br>
<b>no_of_bands: int, optional, default: permutations // 2</b><br>
Number of bands to break minhash signature into before hashing into buckets. A smaller number of bands will result in a stricter algorithm, requiring larger possibly leading to false negatives missing some similar texts, whereas a higher number may lead to false similarities. <br><br>

#### LSH Methods
<b>update</b><br>
Updates model from a MinHash object containing signatures generated from new texts and their corresponding labels.<br>
```.update(minhash, new_labels)```<br>
<b>minhash:</b> MinHash object containing signatures of new texts, parameters must match any previous MinHash objects.<br>
<b>new_labels:</b> List, array or Pandas series containing text labels.<br><br>
<b>query</b><br>
Takes a label and returns the labels of any similar texts.<br>
```.query(label, min_jaccard=None, sensitivity=1)```<br>
<b>label:</b> Label of text to return list of similar texts for.<br>
<b>min_jaccard:</b> Jaccard similarity threshold texts have to exceed to be returned as similar.<br>
<b>sensitivity:</b> Number of buckets texts must share to be returned as similar.<br><br>
<b>remove</b><br>
Remove file label and minhash signature from model.<br>
```.remove(label)```<br>
<b>label:</b> Label of text to remove from LSH model.<br><br>
<b>contains</b><br>
Returns list of labels contained in the model.<br>
```.contains()```<br><br>
<b>adjacency_list</b><br>
Returns an adjacency list that can be used to create a text similarity graph.<br>
```.adjacency_list(min_jaccard=None, sensitivity=1)```<br>
<b>min_jaccard:</b> Jaccard similarity threshold texts have to exceed to be returned as similar.<br>
<b>sensitivity:</b> Number of buckets texts must share to be returned as similar.<br><br>
<b>edge_list</b><br>
Returns a list of edges as tuples of similar pairs, that can be used to create a text similarity graph.<br>
```.edge_list(min_jaccard=None, jaccard_weighted=False, sensitivity=1)```<br>
<b>min_jaccard:</b> Jaccard similarity threshold texts have to exceed to be returned as a pair of similar texts.<br>
<b>jaccard_weighted:</b> Return a list of edges as 3 tuples including text similarity pairs and estimated Jaccard similarity score.<br>
<b>sensitivity:</b> Number of buckets texts must share to be returned as similar.<br><br>

#### LSH Properties
<b>no_of_bands: int</b><br>
```.no_of_bands```<br>
Number of bands used in LSH model.<br><br>
<b>permutations: int</b><br>
```.permutations```<br>
Number of permutations used to create minhash signatures used in LSH model.<br><br>

## Contributing
Contributions are very welcome, message us or just submit a pull request!

## License
MIT License
