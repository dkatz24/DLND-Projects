import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_model, best_score = None, float('inf')

        # Iterate through range of possible states
        for n in range(self.min_n_components, self.max_n_components + 1):
            try:
                # Create model with each possible number of states
                model = self.base_model(n)
                # Method from GaussianHMM class of hmmlearn - computes log probability
                # under model given features, seq. length of states
                log_L = model.score(self.X, self.lengths)
                # Number of parameters (p)
                p = n ** 2 + 2 * n * model.n_features - 1
                # Log of number of data points (N)
                log_N = np.log(self.X.shape[0])

                bic = -2.0 * log_L + p * log_N

                # LOWER scores indicate better models
                if bic < best_score:
                    best_score = bic
                    best_model = model
            except:
                #print('Exception encountered when calculating BIC for model of ' + self.this_word
                #      + ' with ' + str(n) + ' states.')
                pass

        if not best_model:
            best_model = self.base_model(self.n_constant)
            #print("BIC Selection failed for " + self.this_word + "; default # states (" +
            #      str(self.n_constant) + ") used to create base model.")

        return best_model

class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_model, best_score = None, float('-inf')

        # Iterate through range of possible states
        for n in range(self.min_n_components, self.max_n_components + 1):
            try:
                # Create model with each possible number of states
                model = self.base_model(n)
                # Initialize array to track log(L) for other words in dict
                other_word_scores = []
                # Iterate through words in dict
                for word, (X, lengths) in self.hwords.items():
                    if word != self.this_word:
                        other_word_scores.append(model.score(X, lengths))
                # Calculate DIC score by subtracting mean log(L) of all other words in dict
                # from log(L) of given word
                dic = model.score(self.X, self.lengths) - np.mean(other_word_scores)

                # HIGHER scores indicate better models
                if dic > best_score:
                    best_score = dic
                    best_model = model

            except:
                #print('Exception encountered when calculating DIC for model of ' + self.this_word
                #     + ' with ' + str(n) + ' states.')
                pass

        if not best_model:
            best_model = self.base_model(self.n_constant)
            #print("DIC Selection failed for " + self.this_word + "; default # states (" +
            #      str(self.n_constant) + ") used to create base model.")

        return best_model

class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_model, best_score = None, float('-inf')

        # Define method for determining split indicies
        split_method = KFold()

        # Iterate through range of possible states
        for n in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = self.base_model(n)
                # Initialize array to track scores for different splits
                kfold_scores = []
                # Iterate through potential train, test indices that separate the frames
                for train_idx, test_idx in split_method.split(self.sequences):
                    # Create test sets using a given set test indices
                    test_x, test_l = combine_sequences(test_idx, self.sequences)
                    # Append model score on test sets
                    kfold_scores.append(model.score(test_x, test_l))

                # Average all KFold scores for a single state
                kfold_mean = np.mean(kfold_scores)

                # HIGHER scores indicate better models
                if kfold_mean > best_score:
                    best_score = kfold_mean
                    best_model = model

            except:
                #print('Exception encountered when calculating KFold score for model of ' + self.this_word
                #      + ' with ' + str(n) + ' states.')
                pass

        if not best_model:
            best_model = self.base_model(self.n_constant)
            #print("CV Selection failed for " + self.this_word + "; default # states (" +
            #      str(self.n_constant) + ") used to create base model.")

        return best_model