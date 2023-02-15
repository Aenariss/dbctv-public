# testing/entities.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

import sqlalchemy as sa
from .. import exc as sa_exc
from ..util import compat

_repr_stack = set()


class BasicEntity(object):
    def __init__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

    def __repr__(self):
        if id(self) in _repr_stack:
            return object.__repr__(self)
        _repr_stack.add(id(self))
        try:
            return "%s(%s)" % (
                (self.__class__.__name__),
                ", ".join(
                    [
                        "%s=%r" % (key, getattr(self, key))
                        for key in sorted(self.__dict__.keys())
                        if not key.startswith("_")
                    ]
                ),
            )
        finally:
            _repr_stack.remove(id(self))


_recursion_stack = set()


class ComparableMixin(object):
    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """'Deep, sparse compare.

        Deeply compare two entities, following the non-None attributes of the
        non-persisted object, if possible.

        """
        if other is self:
            return True
        elif not self.__class__ == other.__class__:
            return False

        if id(self) in _recursion_stack:
            return True
        _recursion_stack.add(id(self))

        try:
            # pick the entity that's not SA persisted as the source
            try:
                self_key = sa.orm.attributes.instance_state(self).key
            except sa.orm.exc.NO_STATE:
                self_key = None

            if other is None:
                a = self
                b = other
            elif self_key is not None:
                a = other
                b = self
            else:
                a = self
                b = other

            for attr in list(a.__dict__):
                if attr.startswith("_"):
                    continue
                value = getattr(a, attr)

                try:
                    # handle lazy loader errors
                    battr = getattr(b, attr)
                except (AttributeError, sa_exc.UnboundExecutionError):
                    return False

                if hasattr(value, "__iter__") and not isinstance(
                    value, compat.string_types
                ):
                    if hasattr(value, "__getitem__") and not hasattr(
                        value, "keys"
                    ):
                        if list(value) != list(battr):
                            return False
                    else:
                        if set(value) != set(battr):
                            return False
                else:
                    if value is not None and value != battr:
                        return False
            return True
        finally:
            _recursion_stack.remove(id(self))


class ComparableEntity(ComparableMixin, BasicEntity):
    def __hash__(self):
        return hash(self.__class__)
