# A simple Python implementation of Viterbi Algorithm
------------------------------------------------------

In this, I have tried to implement the ```Viterbi Algorithm``` for **POS Tagging**.
Viterbi Algo is based on the concept of **HMM**; in this case tags forming the hidden layer.

The program available in this repo won't run because it requires the following files:
* ```train``` This is a labeled data set used to calculate the *transition* and *emission* probabilities
* ```test_full_unlabeled``` This is the dataset on which we make our tag predictions
* ```test_public_labeled``` This is subset of the above file, labeled, used to measure accuracy of the program

Out of these three files, I have provided only the first file due to uncertainity of data distributin rights.
However, the training dataset should give you an idea how to construct the dataset.
