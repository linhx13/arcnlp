# -*- coding: utf-8 -*-

from typing import Dict, Sequence, Iterable, List
import logging

import numpy as np

from .data_handler import DataHandler
from .. import Field, Example


logger = logging.getLogger(__name__)


class SequenceTaggingDataHandler(DataHandler):
    def __init__(self,
                 token_fields: Dict[str, Field],
                 columns: Sequence[str],
                 token_column: str = "tokens",
                 tag_column: str = "tags",
                 separator: str = None,
                 sparse_target: bool = True,
                 sort_feature: str = None) -> None:
        if not columns:
            raise ValueError("columns cannot be null")
        if 'tokens' not in columns:
            raise ValueError("Cannot find tokens in columns: %s" % (columns,))
        if token_column is None or token_column not in columns:
            raise ValueError("Unknown token column: %s" % token_column)
        if tag_column is None or tag_column not in columns:
            raise ValueError("Unknown tag column: %s" % tag_column)

        self.columns = list(columns)
        self.token_column = token_column
        self.tag_column = tag_column
        self.feature_columns = set(x for x in self.columns
                                   if x and x != self.token_column
                                   and x != self.tag_column)
        self.separator = separator
        self.sparse_target = sparse_target

        feature_fields = {'tokens': token_fields}
        for f in self.feature_columns:
            feature_fields[f] = Field(namespace=f)
        target_fields = {'tags': Field(
            postprocessing=self._tags_postprocessing, namespace="tags")}

        super(SequenceTaggingDataHandler, self).__init__(
            feature_fields, target_fields, sort_feature)

    def _read_from_path(self, path: str) -> Iterable[Example]:
        columns = []
        with open(path, encoding='utf-8', errors='ignore') as fin:
            for line in fin:
                line = line.strip('\r\n')
                if self._is_divider(line):
                    if columns:
                        assert len(self.columns) == len(columns)
                        data = {
                            k: v
                            for k, v in zip(self.columns, columns)
                            if k is not None
                        }
                        tokens = data['tokens']
                        features = {f: data[f] for f in self.feature_columns}
                        tags = data[self.tag_column]
                        yield self.make_example(tokens, features, tags)
                    columns = []
                else:
                    arr = line.rsplit(self.separator,
                                      maxsplit=len(self.columns) - 1)
                    if len(arr) != len(self.columns):
                        logger.warn("Error for line: %s" % line)
                        continue
                    for i, column in enumerate(arr):
                        if len(columns) < i + 1:
                            columns.append([])
                        columns[i].append(column)
            if columns:
                assert len(self.columns) == len(columns)
                data = {
                    k: v
                    for k, v in zip(self.columns, columns)
                    if k is not None
                }
                tokens = data['tokens']
                features = {f: data[f] for f in self.feature_columns}
                tags = data[self.tag_column]
                yield self.make_example(tokens, features, tags)

    def _is_divider(self, line: str) -> bool:
        return line.strip() == ''

    def _tags_postprocessing(self, batch, vocab):
        batch = np.maximum(0, np.array(batch) - 2)
        if self.sparse_target:
            return np.expand_dims(batch, -1)
        else:
            return np.eye(len(vocab) - 2, dtype=np.int32)[batch]

    def make_example(self, tokens: List[str],
                     features: Dict[str, List] = None,
                     tags: List[str] = None) -> Example:
        data = {}
        data['tokens'] = tokens
        if features:
            data.update(features)
        if tags is not None:
            data['tags'] = tags
        fields = dict((k, self.example_fields[k]) for k in data)
        return Example.fromdict(data, fields)