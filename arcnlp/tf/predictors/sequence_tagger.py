# -*- coding: utf-8 -*-

from typing import Dict, List, Callable

from tensorflow.keras.models import Model
import numpy as np

from .predictor import Predictor
from ..data import DataHandler


class SequenceTaggerPredictor(Predictor):

    def __init__(self, model: Model, data_handler: DataHandler,
                 featurizers: Dict[str, Callable[[str], List[str]]]):
        super(SequenceTaggerPredictor, self).__init__(model, data_handler)
        self.featurizers = featurizers

    def _json_to_example(self, json_dict):
        tokens = list(json_dict['text'])
        features = {}
        for k, v in self.featurizers.items():
            fea = v(json_dict['text'])
            assert len(tokens) == len(fea), \
                "featurizer %s, len(tokens) %d != len(fea) %d" \
                % (len(tokens), len(fea))
            features[k] = fea
        return self.data_handler.build_example(tokens, features)

    def decode(self, preds: np.array) -> Dict[str, np.ndarray]:
        tags = [[self.targets['tags'].vocab.itos[idx + 2] for idx in tag_idx]
                for tag_idx in np.argmax(preds, axis=-1)]
        return {'tags': tags}
