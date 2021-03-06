# -*- coding: utf-8 -*-

import tensorflow as tf

from .token_embedder import TokenEmbedder


class TokenCharsEmbedder(TokenEmbedder):
    """A `TokenCharsEmbedder` takes a tensor of shape
    (batch_size, num_tokens, num_chars) as input, embeds the characters, runs
    a token-level encoder, and returns a tensor of shape
    (batch_size, num_tokens, encoding_dim). We also optionally apply dropout
    after the token-level encoder.
    """

    def __init__(self, embedding, encoder, dropout=0.0):
        """Create a TokenCharsEmbedder.

        Args:
            embedding: tf.keras.layers.Embedding
            encoder: seq2vec_encoder
            dropout: dropout rate
        """
        super(TokenCharsEmbedder, self).__init__()
        self.embedding = tf.keras.layers.TimeDistributed(embedding)
        self.encoder = encoder
        self.dropout = dropout

    def call(self, inputs):
        outputs = tf.keras.layers.TimeDistributed(self.embedding)(inputs)
        outputs = self.encoder(outputs)
        if self.dropout > 0:
            outputs = tf.keras.layers.Dropout(self.dropout)(outputs)
        return outputs
