from abc import abstractmethod, ABC

from pysad.transform.ensemble.base_ensembler import BaseScoreEnsembler
from pyod.models.combination import average, maximization, median, moa, aom


class PYODScoreEnsembler(BaseScoreEnsembler, metaclass=ABC):
    """Abstract base class for the scoring ensembling methods for the scoring based ensemblers of the `PyOD <https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.combination>`_.
    """

    @abstractmethod
    def _combine(self, scores):
        """Abstract method that directly uses  of our framework to be filled.

        Args:
            scores: Numpy array of type np.float and shape (1, num_scores)
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
            Resulting anomaly score.
        """
        pass

    def transform_partial(self, scores):
        """Combines anomaly scores from multiple anomaly detectors for a particular timestep.

        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        scores = scores.reshape(1, -1)

        return self._combine(scores)


class AverageScoreEnsembler(PYODScoreEnsembler):
    """An wrapper class that results in the weighted average of the anomaly scores from multiple anomaly detectors. For more details, see `PyOD documentation <https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.combination>`_.

        Args:
            estimator_weights: np array of shape (1, num_anomaly_detectors), if None, assigns uniform weights.

    """

    def __init__(self, estimator_weights=None):
        super().__init__()
        self.estimator_weights = estimator_weights

    def _combine(self, scores):
        """
        Wrapping for PyOD the ensembler.
        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        return average(scores, estimator_weights=self.estimator_weights)


class MaxScoreEnsembler(PYODScoreEnsembler):
    """An ensembler that results the maximum of the previous scores.
    """

    def _combine(self, scores):
        """
        Wrapping for PyOD the ensembler.
        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        return maximization(scores)


class MedianScoreEnsembler(PYODScoreEnsembler):
    """An ensembler that results the median of the previous scores.
    """

    def _combine(self, scores):
        """
        Helper method to wrap the PyOD ensembler.
        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        return median(scores)


class AverageOfMaximumEnsembler(PYODScoreEnsembler):
    """Maximum of average scores ensembler that outputs the maximum of average. For more details, see :cite:`aggarwal2015theoretical` and `PyOD documentation <https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.combination>`_. The ensembler firt divides the scores into buckets and takes the maximum for each bucket. Then, the ensembler outputs the average of all these maximum scores of buckets.

    Args:
        scores : numpy array of shape (n_samples, n_estimators)
            The score matrix outputted from various estimators

        n_buckets : int, optional (default=5)
            The number of subgroups to build

        method : str, optional (default='static')
            {'static', 'dynamic'}, if 'dynamic', build subgroups
            randomly with dynamic bucket size.

        bootstrap_estimators : bool, optional (default=False)
            Whether estimators are drawn with replacement.
    """

    def __init__(self, n_buckets=5, method='static', bootstrap_estimators=False):
        self.method = method
        self.n_buckets = n_buckets
        self.bootstrap_estimators = bootstrap_estimators

    def _combine(self, scores):
        """Wrapping for PyOD the ensembler.

        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        return aom(scores, n_buckets=self.n_buckets, method=self.method, bootstrap_estimators=self.bootstrap_estimators)


class MaximumOfAverageEnsembler(PYODScoreEnsembler):
    """Maximum of average scores ensembler that outputs the maximum of average. For more details, see :cite:`aggarwal2015theoretical` and `PyOD documentation <https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.combination>`_. The ensembler firt divides the scores into buckets and takes the average for each bucket. Then, the ensembler outputs the maximum of all these average scores of buckets.

    Args:
        scores : numpy array of shape (n_samples, n_estimators)
            The score matrix outputted from various estimators

        n_buckets : int, optional (default=5)
            The number of subgroups to build

        method : str, optional (default='static')
            {'static', 'dynamic'}, if 'dynamic', build subgroups
            randomly with dynamic bucket size.

        bootstrap_estimators : bool, optional (default=False)
            Whether estimators are drawn with replacement.
    """

    def __init__(self, n_buckets=5, method='static', bootstrap_estimators=False):
        self.method = method
        self.n_buckets = n_buckets
        self.bootstrap_estimators = bootstrap_estimators

    def _combine(self, scores):
        """
        Wrapping for PyOD the ensembler.
        Args:
            scores: np.float array of shape (num_anomaly_detectors, )
                List of scores from multiple anomaly detectors.

        Returns:
            score: float
                Resulting anomaly score.
        """
        return moa(scores, n_buckets=self.n_buckets, method=self.method, bootstrap_estimators=self.bootstrap_estimators)
