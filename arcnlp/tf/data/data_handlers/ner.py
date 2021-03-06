# -*- coding: utf-8 -*-

from typing import Dict

from jieba import posseg

from .sequence_tagging import SequenceTaggingDataHandler
from .. import Field


class NerDataHanlder(SequenceTaggingDataHandler):

    def __init__(self,
                 token_fields: Dict[str, Field],
                 use_seg_feature: bool = False,
                 **kwargs):
        self.use_seg_feature = use_seg_feature
        if self.use_seg_feature:
            columns = ['token', 'seg', 'tag']
            feature_columns = ['seg']
        else:
            columns = ['token', 'tag']
            feature_columns = None
        super(NerDataHanlder, self).__init__(
            token_fields=token_fields,
            columns=columns,
            token_column='token',
            tag_column='tag',
            feature_columns=feature_columns,
            **kwargs)

    def get_seg_seq(self, text):
        res = []
        for t in posseg.lcut(text):
            if len(t.word) == 1:
                res.append('S-%s' % t.flag)
            else:
                res.append('B-%s' % t.flag)
                for _ in range(1, len(t.word) - 1):
                    res.append('I-%s' % t.flag)
                res.append('E-%s' % t.flag)
        return res
