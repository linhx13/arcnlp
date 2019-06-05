# -*- coding: utf-8 -*-


class Batch(object):
    """Defines a batch of examples along with its Fields.

    Attributes:
        batch_size: Number of examples in the batch.
        dataset: A reference to the dataset object the examples come from
            (which itself contains the dataset's Field objects).
        fields: The name of fields in the dataset.
        input_fields: The names of the fields that are used as input for model
        target_fields: The names of the fields that are used as targets during
            model training.

    Also store the tensor for each column in the batch as an attribute.
    """

    def __init__(self, data=None, dataset=None):
        """Create a Batch from a list of examples."""
        if data is not None:
            self.batch_size = len(data)
            self.dataset = dataset
            self.fields = list(dataset.fields.keys())  # copy field names
            self.input_fields = [k for k, v in dataset.fields.items()
                                 if v is not None and not v.is_target]
            self.target_fields = [k for k, v in dataset.fields.items()
                                  if v is not None and v.is_target]
            for (name, field) in dataset.fields.items():
                if field is not None:
                    batch = [getattr(x, name) for x in data]
                    setattr(self, name, field.process(batch))

    @classmethod
    def from_vars(cls, dataset, batch_size, train=None, **kwargs):
        """Create a Batch directly from a number of Variables."""
        batch = cls()
        batch.batch_size = batch_size
        batch.dataset = dataset
        batch.fields = list(dataset.fields.keys())
        for k, v in kwargs.items():
            setattr(batch, k, v)
        return batch

    def __len__(self):
        return self.batch_size

    def _get_field_values(self, fields):
        if len(fields) == 0:
            return None
        elif len(fields) == 1:
            return getattr(self, fields[0])
        else:
            return list(getattr(self, f) for f in fields)

    def __iter__(self):
        yield self._get_field_values(self.input_fields)
        yield self._get_field_values(self.target_fields)

    def as_tensors(self):
        return self._get_field_values(self.input_fields), \
            self._get_field_values(self.target_fields)

