import numpy as np
import unittest

from chainer import testing
from chainer.dataset import TabularDataset

from .test_tabular_dataset import DummyDataset


@testing.parameterize(*testing.product_dict(
    testing.product({
        'mode_a': [tuple, dict],
        'mode_b': [tuple, dict],
    }),
    [
        {'indices': None,
         'expected_indices_a': slice(0, 10, 1),
         'expected_indices_b': slice(0, 5, 1)},
        # {'indices': [3, 1, 4, 12, 14, 13, 7, 5],
        #  'expected_indices_a': [3, 1, 4, 7, 5],
        #  'expected_indices_b': [2, 4, 3]},
        {'indices': slice(13, 6, -2),
         'expected_indices_a': slice(9, 6, -2),
         'expected_indices_b': slice(3, None, -2)},
        {'indices': slice(9, None, -2),
         'expected_indices_a': slice(9, None, -2)}
        # {'indices': [3, 1], 'expected_len': 2, 'expected_indices': [3, 1]},
        # {'indices': [11, 1], 'exception': IndexError},
        # {'indices': [i in {1, 3} for i in range(10)],
        #  'expected_len': 2, 'expected_indices': [1, 3]},
        # {'indices': [True] * 11, 'exception': ValueError},
        # {'indices': slice(3, None, -2), 'expected_len': 2,
        #  'expected_indices': slice(3, -1, -2)},
    ],
))
class TestConcat(unittest.TestCase):

    def test_concat(self):
        def callback_a(indices, key_indices):
            self.assertEqual(indices, self.expected_indices_a)
            self.assertIsNone(key_indices)

        dataset_a = DummyDataset(mode=self.mode_a, callback=callback_a)

        def callback_b(indices, key_indices):
            self.assertEqual(indices, self.expected_indices_b)
            self.assertIsNone(key_indices)

        dataset_b = DummyDataset(len_=5, mode=self.mode_b, callback=callback_b)

        view = dataset_a.concat(dataset_b)
        self.assertIsInstance(view, TabularDataset)
        self.assertEqual(len(view), len(dataset_a) + len(dataset_b))
        self.assertEqual(view.keys, dataset_a.keys)
        self.assertEqual(view.mode, dataset_a.mode)

        data = np.hstack((dataset_a.data, dataset_b.data))
        if self.indices is not None:
            data = data[:, self.indices]
        self.assertEqual(
            view.get_examples(self.indices, None),
            tuple(list(d) for d in data))


testing.run_module(__name__, __file__)
