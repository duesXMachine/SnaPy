# Class for generating a similarity model from Minhash signature matrices using LSH.
# Author: Justin Boylan-Toomey

from collections import defaultdict
import numpy as np
from copy import copy


class LSH:
    def __init__(self, minhash=None, labels=None, no_of_bands=None):
        """ Initialize the LSH object.

        Args:
            minhash (np.array): Object returned by MinHash class.
            labels (list, np.array, pandas series): Iterable containing labels.
            no_of_bands (int): Number of bands to break minhash signature into.
        """
        # Create default variables
        self.signatures = None
        self.no_of_bands = no_of_bands
        self._buckets = defaultdict(list)
        self._i_bucket = defaultdict(list)
        # Run methods if minhash and labels provided
        if minhash and labels:
            self.permutations = minhash.permutations
            self._lsh(minhash.signatures, labels)
        elif minhash:
            raise ValueError(
                'labels cannot be None if LSH initialised with minhash object.'
            )
        elif labels:
            raise ValueError(
                'minhash object cannot be None if LSH initialised with labels.'
            )

    def _lsh(self, signatures, labels):
        """ Break signatures into bands and hash components to buckets.

        Args:
            signatures (np.array): MinHash signature Matrix.
            labels (list): List of labels for MinHash signatures.
        """
        if not self.no_of_bands:
            self.no_of_bands = self.permutations // 2
        for label, signature in zip(labels, signatures):
            bands = np.hsplit(
                np.array(signature), self.no_of_bands
            )
            for band in bands:
                bucket_id = hash(tuple(band))
                self._buckets[bucket_id].append(label)
                self._i_bucket[label].append(bucket_id)

    def _candidate_duplicates(self, bucket_ids, label, sensitivity, jaccard):
        """ Identify candidate duplicates and check Jaccard Similarity.

        Args:
            bucket_ids (list): List of bucket ids.
            label (str, int, float): Text label.
            sensitivity (int): Number of identical buckets two ids must occur
                in to be considered a near duplicate pair.
            jaccard (float): Minimum Jaccard Similarity for documents to be
                counted as near duplicates.

        Returns:
            List: Near duplicate document ids.
        """
        candidates = defaultdict(int)
        # Retrieve candidate duplicate pairs from model.
        for bucket_id in bucket_ids:
            matches = copy(self._buckets.get(bucket_id))
            matches.remove(label)
            for match in matches:
                candidates[match] += 1
        # Apply sensitivity threshold.
        if sensitivity > 1:
            for key in list(candidates):
                if candidates[key] < sensitivity:
                    del candidates[key]
        # Apply Jaccard threshold and unzip pairs.
        if jaccard:
            for key in list(candidates):
                if (
                    candidates[key] / self.no_of_bands
                ) < jaccard:
                    del candidates[key]
        candidates = candidates.keys()
        return candidates

    def update(self, minhash, new_labels):
        """ Update model with new MinHash matrix and labels.

        Args:
            minhash (minhash): MinHash object containing new minhash signatures.
            new_labels (list): List of new labels for update texts.
        """
        if self._i_bucket:
            # Check parameters if model already exists.
            if set(
                    self._i_bucket.keys()
            ).intersection(set(new_labels)) != set():
                raise ValueError(
                    'At least one provided label already exists in model.'
                )
            if self.permutations != minhash.permutations:
                raise ValueError(
                    'Number of permutations must be {} to match LSH model.'.format(self.permutations)
                )
        else:
            # Create parameters for new model.
            self.permutations = minhash.permutations
        # Update model.
        self._lsh(minhash.signatures, new_labels)

    def query(self, label, sensitivity=1, min_jaccard=None):
        """ Take unique identifier and return near duplicates from model.

        Args:
            label (str, int, float): Label of document for which to return
            near duplicates.
            sensitivity (int): Number of identical buckets two ids must occur
                in to be considered a near duplicate pair.
            min_jaccard (float): Minimum Jaccard Similarity for documents to be
                counted as near duplicates.

        Returns:
            List: Candidate duplicates for provided text label.
        """
        if sensitivity > self.no_of_bands:
            raise ValueError(
                'Sensitivity must be <= no of bands.'
            )
        buckets = self._i_bucket.get(label)
        if not buckets:
            raise KeyError(
                'Label {} does not exist in model'.format(label)
            )
        return self._candidate_duplicates(
            buckets, label, sensitivity, min_jaccard
        )

    def remove(self, label):
        """ Remove file label and minhash from model.

        Args:
            label (str, int, float): Label for text to be removed from model.
        """
        buckets = self._i_bucket.get(label)
        if not buckets:
            raise ValueError(
                'Label {} does not exist in model'.format(label)
            )
        for bucket in buckets:
            self._buckets[bucket].remove(label)
            if not self._buckets[bucket]:
                del self._buckets[bucket]
        del self._i_bucket[label]

    def contains(self):
        """ Returns list of ids contained in the model.

        Returns:
             List: Text ids in model.
        """
        return self._i_bucket.keys()


"""
    def adjacency_list(
            self,
            sensitivity=1,
            jaccard=None,
            keep_weighting=False
    ):
        "#"" Returns adjacency list.

        Args:
            sensitivity (int): Number of identical buckets two ids must occur
                in to be considered a near duplicate pair.
            jaccard (float): Minimum Jaccard Similarity for documents to be
                counted as near duplicates.
            keep_weighting (bool): If True return near duplicate tuple as Jaccard score,
                near duplicate tuple.

        Returns:
            List: adjacency list.
        "#""
        adjacency_list = {}
        for label in self._i_bucket:
            check_buckets = self._i_bucket[label]
            candidates = []
            for bucket in check_buckets:
                candidates += copy(self._buckets[bucket])
                candidates.remove(label)
            if sensitivity > 1:
                candidates = [
                    value
                    for value, count in Counter(candidates).items()
                    if count >= sensitivity
                ]
            else:
                candidates = list(set(candidates))
            if jaccard:
                duplicates = []
                for candidate in candidates:
                    score = self._jaccard_similarity(label, candidate)
                    if score >= jaccard:
                        result = candidate
                        if keep_weighting:
                            result = (score, candidate)
                        duplicates.append(result)

                adjacency_list[label] = duplicates
            else:
                adjacency_list[label] = candidates
        return adjacency_list
"""
