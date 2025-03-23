"""Utility functions that do not depend on bpy, but might depend on
mathutils. Also re-exports mathutils' Quaternion and Vector."""
from itertools import product

from mathutils import Quaternion, Vector


class ImmutableModifyError(Exception):
    pass


class ImmutableList(list):
    """A hack for adding a custom error to a list if it is modified"""
    def __init__(self, *args, err="Immutable list cannot be modified"):
        self.err = err
        super().__init__(*args)

    def _raise_error(self, *args, **kwargs):
        raise ImmutableModifyError(self.err)

_mutating_methods = {
    "append", "extend", "clear", "insert", "pop",
    "remove", "sort", "reverse", "__setitem__", "__delitem__",
    "__iadd__", "__imul__"
}
for method in _mutating_methods:
   setattr(ImmutableList, method, ImmutableList._raise_error)


def approximate_in(q, ps, epsilon = 1e-2):
    """Whether quaternion q or its opposite is in qs, with a tolerance
    of epsilon.

    """
    for p in ps:
        if (p-q).magnitude < epsilon or (p+q).magnitude < epsilon:
            return True
    return False


def get_spherical_group(gens, size):
    """Returns a tuple of all the elements in a spherical group
    (modulo a reflection, if necessary) from the generator quaternions
    and the size.

    The gens must be an iterable of quaternions, and size must be a
    positive integer.

    The algorithm is the obvious one, so the time could blow up for
    large groups, which should be rare in practice.

    More refined algorithms would use abstract presentations (e.g.,
    Todd-Coxeter). Possible group elements would form a countable, and
    thus hashable, set, reducing the amount of loops.

    """
    group = [Quaternion()]
    new_els = [Quaternion()] 
    while True:
        last_els, new_els = new_els, []
        for gen, g in product(gens, last_els):
            if not approximate_in(h := g @ gen, group):
                new_els.append(h)
                group.append(h)
                if len(group) >= size:
                    return tuple(group)
        if not new_els:
            raise ValueError("get_spherical_group: 'size' larger than actual")
