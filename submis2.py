from __future__ import division
from collections import Counter
# from operator import itemgetter
#  this functionality is NOT needed. It may help slightly, but you can definitely ignore it completely.

#DO NOT CHANGE!
def read_train_file():
    '''
    HELPER function: reads the training files containing the words and corresponding tags.
    Output: A tuple containing 'words' and 'tags'
    'words': This is a nested list - a list of list of words. See it as a list of sentences, with each sentence itself being a list of its words.
    For example - [['A','boy','is','running'],['Pick','the','red','cube'],['One','ring','to','rule','them','all']]
    'tags': A nested list similar to above, just the corresponding tags instead of words.
    '''
    f = open('train','r')
    words = []
    tags = []
    lw = []
    lt = []
    for line in f:
        s = line.rstrip('\n')
        w,t= s.split('/')[0],s.split('/')[1]
        if w=='###':
            words.append(lw)
            tags.append(lt)
            lw=[]
            lt=[]
        else:
            lw.append(w)
            lt.append(t)
    words = words[1:]
    tags = tags[1:]
    assert len(words) == len(tags)
    f.close()
    return (words,tags)


#NEEDS TO BE FILLED!
def train_func(train_list_words, train_list_tags):

    '''
    This creates dictionaries storing the transition and emission probabilities - required for running Viterbi.
    INPUT: The nested list of words and corresponding nested list of tags from the TRAINING set. This passing of correct lists and calling the function
    has been done for you. You only need to write the code for filling in the below dictionaries. (created with bigram-HMM in mind)
    OUTPUT: The two dictionaries

    HINT: Keep in mind the boundary case of the starting POS tag. You may have to choose (and stick with) some starting POS tag to compute bigram probabilities
    for the first actual POS tag.
    '''

    dict2_tag_follow_tag= {}
    """Nested dictionary to store the transition probabilities
    each tag X is a key of the outer dictionary with an inner dictionary as the corresponding value
    The inner dictionary's key is the tag Y following X
    and the corresponding value is the number of times Y follows X - convert this count to probabilities finally before returning
    for example - { X: {Y:0.33, Z:0.25}, A: {B:0.443, W:0.5, E:0.01}} (and so on) where X,Y,Z,A,B,W,E are all POS tags
    so the first key-dictionary pair can be interpreted as "there is a probability of 0.33 that tag Y follows tag X, and 0.25 probability that Z follows X"
    """
    dict2_word_tag = {}
    """Nested dictionary to store the emission probabilities.
    Each word W is a key of the outer dictionary with an inner dictionary as the corresponding value
    The inner dictionary's key is the tag X of the word W
    and the corresponding value is the number of times X is a tag of W - convert this count to probabilities finally before returning
    for example - { He: {A:0.33, N:0.15}, worked: {B:0.225, A:0.5}, hard: {A:0.1333, W:0.345, E:0.25}} (and so on) where A,N,B,W,E are all POS tags
    so the first key-dictionary pair can be interpreted as "there is a probability of 0.33 that A is the POS tag for He, and 0.15 probability that N is the POS tag for He"
    """

    #      *** WRITE YOUR CODE HERE ***

    # Counting occurrences of each tag
    STRT_TAG = "<S>"

    def flatten(seq, container=None):
        if container is None:
            container = []
        for s in seq:
            if hasattr(s, '__iter__'):
                flatten(s, container)
            else:
                container.append(s)
        return container
    c = flatten(train_list_tags)
    count_tags = Counter(c)
    # print count_tags

    # Populating start of sentence tag probabilities
    strt_probab = {}
    tempStartTgList = [tagSent[0] for tagSent in train_list_tags]
    for tgSent in train_list_tags:
        strt_probab[tgSent[0]] = tempStartTgList.count(tgSent[0]) / count_tags[tgSent[0]]
    # print strt_probab

    # Populating the tag follow tag dictionary and the word given tag dictionary
    assert len(train_list_words) == len(train_list_tags)
    train_lst_tag_flat = flatten(train_list_tags)
    train_lst_wrd_flat = flatten(train_list_words)
    for indx, (tg, wrd) in enumerate(zip(train_lst_tag_flat, train_lst_wrd_flat)):
        wrd = wrd.lower()
        if tg not in dict2_tag_follow_tag:      # initializing the tag follow tag dictionary
            dict2_tag_follow_tag[tg] = {}
        if wrd not in dict2_word_tag:           # initializing the word for a tag dictionary
            dict2_word_tag[wrd] = {}
        if indx < len(train_lst_tag_flat) - 2 and indx < len(train_lst_wrd_flat) - 2:
            # below we count the tag after current tag
            nxtTg = train_lst_tag_flat[indx + 1]
            if nxtTg in dict2_tag_follow_tag[tg]:
                dict2_tag_follow_tag[tg][nxtTg] += 1
            else:
                dict2_tag_follow_tag[tg][nxtTg] = 1
            # below we count the emitter tag for current word
            if tg in dict2_word_tag[wrd]:
                dict2_word_tag[wrd][tg] += 1
            else:
                dict2_word_tag[wrd][tg] = 1

    # now generating probabilities from counts
    for tg in dict2_tag_follow_tag:
        for followTag in dict2_tag_follow_tag[tg]:
            dict2_tag_follow_tag[tg][followTag] /= count_tags[tg]        # this will give the probabilities
    for wrd in dict2_word_tag:
        for emitTag in dict2_word_tag[wrd]:
            dict2_word_tag[wrd][emitTag] /= count_tags[emitTag]
    # appending the starting probabilities
    dict2_tag_follow_tag[STRT_TAG] = strt_probab

    # END OF YOUR CODE

    return (dict2_tag_follow_tag, dict2_word_tag)


#NEEDS TO BE FILLED!
def assign_POS_tags(test_words, dict2_tag_follow_tag, dict2_word_tag):

    '''
    This is where you write the actual code for Viterbi algorithm.
    INPUT: test_words - this is a nested list of words for the TEST set
           dict2_tag_follow_tag - the transition probabilities (bigram), filled in by YOUR code in the train_func
           dict2_word_tag - the emission probabilities (bigram), filled in by YOUR code in the train_func
    OUTPUT: a nested list of predicted tags corresponding to the input list test_words. This is the 'output_test_tags' list created below, and returned after your code
    ends.

    HINT: Keep in mind the boundary case of the starting POS tag. You will have to use the tag you created in the previous function here, to get the
    transition probabilities for the first tag of sentence...
    HINT: You need not apply sophisticated smoothing techniques for this particular assignment.
    If you cannot find a word in the test set with probabilities in the training set, simply tag it as 'N'.
    So if you are unable to generate a tag for some word due to unavailability of probabilities from the training set,
    just predict 'N' for that word.

    '''

    output_test_tags = []   # list of list of predicted tags, corresponding to the list of list of words in Test set (test_words input to this function)


    #      *** WRITE YOUR CODE HERE ***

    STRT_TAG = "<S>"
    states = ["C", "D", "E", "F", "I", "J", "L", "M", "N", "P", "R", "S", "T", "U", "V", "W", "###", ",", ".", ":", "-", "'", "$"]
    ZERO = 0
    BASIC = 0.0000001e-15     # this number is random, need to get the least common probability from training dataset

    for wrdLst in test_words:
        output_list = []
        # now implement for each list
        V = [{}]        # list of dictionaries
        for st in states:

            strt_prob = dict2_tag_follow_tag[STRT_TAG][st] if st in dict2_tag_follow_tag[STRT_TAG] else ZERO
            emit_prob = dict2_word_tag[wrdLst[0].lower()][st] if wrdLst[0].lower() in dict2_word_tag and st in dict2_word_tag[wrdLst[0].lower()] else BASIC

            V[0][st] = {"prob": strt_prob * emit_prob, "prev": None}
        # forward probability calculations
        for t in range(1, len(wrdLst)):
            V.append({})
            for st in states:
                probab_prod = []
                for prev_st in states:
                    trans_prob = dict2_tag_follow_tag[prev_st][st] if prev_st in dict2_tag_follow_tag and st in dict2_tag_follow_tag[prev_st] else ZERO
                    probab_prod.append(V[t-1][prev_st]["prob"] * trans_prob)
                max_tr_prob = max(probab_prod)

                for prev_st in states:
                    trans_prob = dict2_tag_follow_tag[prev_st][st] if prev_st in dict2_tag_follow_tag and st in dict2_tag_follow_tag[prev_st] else ZERO
                    if V[t-1][prev_st]["prob"] * trans_prob == max_tr_prob:
                        emit_prob = dict2_word_tag[wrdLst[t].lower()][st] if wrdLst[t].lower() in dict2_word_tag and st in dict2_word_tag[wrdLst[t].lower()] else BASIC
                        max_prob = max_tr_prob * emit_prob
                        V[t][st] = {"prob": max_prob, "prev": prev_st}
                        break

        # The highest probability
        max_prob = max(value["prob"] for value in V[-1].values())
        previous = None
        # Get most probable state and its backtrack
        for st, data in V[-1].items():
            if data["prob"] == max_prob:
                output_list.append(st)
                previous = st
                break
        # Follow the backtrack till the first observation
        for t in range(len(V) - 2, -1, -1):
            output_list.insert(0, V[t + 1][previous]["prev"])
            previous = V[t + 1][previous]["prev"]

        output_test_tags.append(output_list)

    # END OF YOUR CODE

    return output_test_tags


# DO NOT CHANGE!
def public_test(predicted_tags):
    '''
    HELPER function: Takes in the nested list of predicted tags on test set (prodcuced by the assign_POS_tags function above)
    and computes accuracy on the public test set. Note that this accuracy is just for you to gauge the correctness of your code.
    Actual performance will be judged on the full test set by the TAs, using the output file generated when your code runs successfully.
    '''

    f = open('test_public_labeled','r')
    words = []
    tags = []
    lw = []
    lt = []
    for line in f:
        s = line.rstrip('\n')
        w,t= s.split('/')[0],s.split('/')[1]
        if w=='###':
            words.append(lw)
            tags.append(lt)
            lw=[]
            lt=[]
        else:
            lw.append(w)
            lt.append(t)
    words = words[1:]
    tags = tags[1:]
    assert len(words) == len(tags)
    f.close()
    public_predictions = predicted_tags[:len(tags)]
    assert len(public_predictions)==len(tags)

    correct = 0
    total = 0
    flattened_actual_tags = []
    flattened_pred_tags = []
    for i in range(len(tags)):
        x = tags[i]
        y = public_predictions[i]
        if len(x)!=len(y):
            print(i)
            print(x)
            print(y)
            break
        flattened_actual_tags+=x
        flattened_pred_tags+=y
    assert len(flattened_actual_tags)==len(flattened_pred_tags)
    correct = 0.0
    for i in range(len(flattened_pred_tags)):
        if flattened_pred_tags[i]==flattened_actual_tags[i]:
            correct+=1.0
    print('Accuracy on the Public set = '+str(correct/len(flattened_pred_tags)))


# DO NOT CHANGE!
if __name__ == "__main__":
    words_list_train = read_train_file()[0]
    tags_list_train = read_train_file()[1]

    dict2_tag_tag = train_func(words_list_train,tags_list_train)[0]
    dict2_word_tag = train_func(words_list_train,tags_list_train)[1]

    f = open('test_full_unlabeled','r')  # open('test_unlabeled_small', 'r')

    words = []
    l=[]
    for line in f:
        w = line.rstrip('\n')
        if w=='###':
            words.append(l)
            l=[]
        else:
            l.append(w)
    f.close()
    words = words[1:]
    test_tags = assign_POS_tags(words, dict2_tag_tag, dict2_word_tag)
    assert len(words)==len(test_tags)

    public_test(test_tags)

    # create output file with all tag predictions on the full test set

    f = open('output','w')
    f.write('###/###\n')
    for i in range(len(words)):
        sent = words[i]
        pred_tags = test_tags[i]
        for j in range(len(sent)):
            word = sent[j]
            pred_tag = pred_tags[j]
            f.write(word+'/'+pred_tag)
            f.write('\n')
        f.write('###/###\n')
    f.close()

    print('OUTPUT file has been created')

