"""=================== General symmetry groups =====================
 Add a symmetry group (frieze, planar or spherical) to an object, as a
 more general mirror / repeat modifier. Orbifold notation is used, as
 in Conway, Burgiel and Goodman-Strauss's book *The symmetries of
 things*.

"""
from math import pi ,inf, cos, acos, sin
from string import digits

from .utils import (
    get_spherical_group,
    ImmutableList,
    ImmutableModifyError,
    Quaternion, Vector,
)


class BadSymGrpError(ValueError):
    """For symmetry groups that have impossible signatures or that do
    not make planar / spherical patterns

    """
    pass


class SymGrp():
    """Immutable symmetry group from orbifold signature.

    Each character of a well-formed signature lies in
    '0123456789*xo()'.  0 is interpreted as inf. Parens must surround
    numbers >= 10. Points are not supported. Dihedrical / Cyclic
    gruops can be obtained as spherical groups (*NN or NN,
    respectively).  Ones '1' in the signature are ignored.  Option
    'calculate_axes' can be turned off for debugging purposes.

    EXAMPLE:
    > G = SymGrp("*432")      # Symmetry group of a cube
    > G.n_symmetries
    48
    > len(G.axes)
    24

    """
    def __init__(self, signature, *, calculate_axes = True):
        self._parse(signature)
        self._axes = self._tile = self._inverse_axes = self._all_axes = None
        if calculate_axes:
            self._calculate_axes()
            assert(len(self) == self.n_symmetries)

    def _calculate_axes(self):
        self._axes, self._inverse_axes, *self._tile = self._get_axes()
        self._all_axes = (*((ax, Vector((1,1,1))) for ax in self.axes),
                          *((ax, Vector((1,-1,1))) for ax in self.inverse_axes))
            
    @property
    def stars(self):
        """Number of stars '*', which means non-congruent
        kaleidoscopes (series of mirrors that meet cyclically).

        """
        return self._stars
    
    @property
    def xs(self):
        """Number of 'x', which correspond to miracles (inverse
        symmetries that are not due to mirrors).

        """
        return self._xs
    
    @property
    def os(self):
        """Number of 'o' (wonders), corresponding to pairs of
        translations not explained by gyrations / mirrors.

        """
        return self._os
    
    @property
    def kaleidoscopes(self):
        """Period of each kaleidoscopic point (a point at which
        mirrors touch).  Represented by a (red) number after a
        star. Each period is considered to be part of the same
        kaleidoscope, which is not a problem for the groups considered
        here, since the only planar / spherical group with two
        kaleidoscopes is '**', which has no kaleidoscopic points.

        """
        return self._kaleidoscopes
    
    @property
    def gyrations(self):
        """Period of the gyrations, which are points with a rotational
        symmetry that are not kaleidoscopic.

        """
        return self._gyrations

    def _parse(self, signature):
        """Obtain the centers and stuff from the signature"""
        kaleidoscopes = []
        gyrations = []
        self._stars = 0                   # Kaleidoscopic points
        self._xs = 0                      # Miracles
        self._os = 0                      # Wanderings
        
        centers = gyrations
        parens = None
        try:
            for char in signature:
                match char:
                    case ")" if parens is not None:
                        N = int("".join(parens))
                        N = inf if N == 0 else N
                        centers.append(N)
                        parens = None
                    case _ if parens is not None and char in digits:
                        parens.append(char)
                    case _ if parens is not None:
                        raise ValueError("Non-digit in parens")
                    case "0" | "∞":
                        centers.append(inf)
                    case _ if char in digits:
                        centers.append(int(char))
                    case "*" | "★":
                        centers = kaleidoscopes
                        self._stars += 1
                    case "x" | "❌" | "✕":
                        self._xs += 1
                        centers = ImmutableList(
                            err = "Miracle (x) with centers is impossible"
                        )
                    case "o" if centers is gyrations:
                        self._os += 1
                    case "o":
                        raise ValueError(
                            "Wandering (o) after inverse symmetry is impossible"
                        )
                    case "(":
                        parens = []
                    case _:
                        raise ValueError(f"Unwanted '{char}'")
            if parens is not None:
                raise ValueError("Unclosed '('")
        except (ValueError, ImmutableModifyError) as e:
            new_e = BadSymGrpError() 
            new_e.args = ("Incorrect orbifold signature", *e.args)
            raise new_e from None
        self._gyrations = tuple(n for n in gyrations if n != 1)
        self._kaleidoscopes = tuple(n for n in kaleidoscopes if n != 1) 
        
    @property
    def cost(self):
        """The cost of the orbifold signature"""
        return (sum(1 - 1/n for n in self.gyrations)
                + sum(1/2 - 1/(2*n) for n in self.kaleidoscopes)
                + self.stars + self.xs + 2*self.os)
    
    @property
    def has_inverse_symmetry(self):
        """Whether there is an inverse symmetry (kaleidoscope or miracle)"""
        return bool(self.stars or self.xs)

    @property
    def gyrational(self):
        """The opposite of self.has_inverse_symmetry (all direct
        symmetries)"""
        return not self.has_inverse_symmetry
    
    @property
    def n_symmetries(self):
        """Number of symmetries in the spherical case.  Does not work
        in the hyperbolic case.

        """
        try:
            value = round(2/(2 - self.cost))
        except ZeroDivisionError:
            value = inf
        return value
    
    @property
    def type(self):
        """One of 'SPHERICAL', 'PLANAR', 'FRIEZE', 'HYPERBOLIC'"""
        if self.cost > 2:
            return 'HYPERBOLIC'
        if self.cost < 2:
            return 'SPHERICAL'
        if inf in (*self.gyrations, *self.kaleidoscopes):
            return 'FRIEZE'
        return 'PLANAR'
    
    def _get_axes(self):
        """Calculates the axis and fundamental tile"""
        # Default for when there are no symmetries
        axes = (Quaternion(),)
        inverse_axes = ()
        verts = (Vector((0,0,1)), Vector((0,0,-1)),
                 Vector((1,0,0)), Vector((-1,0,0)),
                 Vector((0,1,0)), Vector((0,-1,0)),
                 )
        faces = ((0,2,4), (0,5,2), (0,4,3), (0,3,5),
                 (1,4,2), (1,2,5), (1,3,4), (1,5,3),
                 )

        match self.type, self:
            case 'HYPERBOLIC', _:
                raise BadSymGrpError(
                    f"Hyperbolic groups not supported (cost {self.cost} > 2)"
                )

            case ('FRIEZE' | 'PLANAR'), _:
                raise NotImplementedError("Non-spherical symmetry group")

            case 'SPHERICAL', _ if inf in [*self.gyrations,
                                           *self.kaleidoscopes]:
                raise BadSymGrpError(
                    "Spherical groups cannot have infinites (0)"
                )

            # Gyrational spherical groups
            case 'SPHERICAL', SymGrp(gyrational = True, gyrations = []):
                pass                                 # * Group C_1 (unit)

            case 'SPHERICAL', SymGrp(gyrational = True, gyrations = [M, N]):
                if M != N:                           # * Group C_N (cyclyc)
                    raise BadSymGrpError("Spherical group MN must have M = N")
                axes = tuple(Quaternion((0, 0, 1), i*2*pi/N) for i in range(N))
                verts = (Vector((0, 0, 1)),
                         Vector((0, 0, -1)),
                         Vector((1, 0, 0)),
                         Quaternion((0,0,1), pi/N) @ Vector((1, 0, 0)),
                         Quaternion((0,0,1), 2*pi/N) @ Vector((1, 0, 0)))
                faces = (0,2,3), (0,3,4), (1,3,2), (1,4,3)

            case 'SPHERICAL', SymGrp(gyrational = True, gyrations = [M, N, P]):
                A, B, C = pi/M, pi/N, pi/P           # * Other

                # Side lengths
                c = acos((cos(C) + cos(A)*cos(B))/(sin(A)*sin(B)))
                b = acos((cos(B) + cos(C)*cos(A))/(sin(C)*sin(A)))
                
                # Vertices and faces
                pa = Vector((0, 0, 1))
                pb = Quaternion((0, 1, 0), c) @ pa
                v = Vector((0,1,0))
                v.rotate(Quaternion((0,0,1), A))
                pc = pa.copy()
                pc.rotate(Quaternion(v, b))
                
                verts = (pa, pb, pc, pc * Vector((1,-1,1)))
                faces = (0,1,2), (0,3,1)

                # Rotation axes
                axes = get_spherical_group(
                    [Quaternion(pa, 2*A),
                     Quaternion(pb, 2*B),
                     Quaternion(pc, 2*C)], 
                    self.n_symmetries)

            case 'SPHERICAL', SymGrp(gyrational = True):
                raise BadSymGrpError(
                    "Gyrational spherical groups must be MN or MNP"
                )

            # Mixed spherical groups
            case 'SPHERICAL', SymGrp(gyrations = [2], kaleidoscopes = [N]):
                # Vertices and faces
                pa = Vector((1,0,0))
                pb = Vector((0,0,1))
                pc = Quaternion((1,0,0),   pi/(2*N)) @ Vector((0,0,1))
                pd = Quaternion((1,0,0), 2*pi/(2*N)) @ Vector((0,0,1))
                verts = (pa, pb, pc, pd)
                faces = (0,1,2), (0,2,3)

                # Rotation axes
                axes = get_spherical_group(
                    (Quaternion((1,0,0), 2*pi/N), Quaternion(pc, pi)),
                    self.n_symmetries // 2)

            case 'SPHERICAL', SymGrp(gyrations = [3], kaleidoscopes = [2]):
                A, B, C = pi/4, pi/2, pi/3           # * Group 3*2

                # Side lengths
                b = acos((cos(B) + cos(C)*cos(A))/(sin(C)*sin(A)))

                # Vertices and faces
                v = Quaternion((0,0,1), A) @ Vector((0,1,0))
                pa = Vector((0,0,1))
                pb = Quaternion((0,1,0), pi/4) @ pa
                pc = Vector((1,0,0))
                pd = Quaternion(v, b) @ pa

                verts = pa, pb, pc, pd
                faces = (0,1,3), (1,2,3)

                # Rotation axes
                axes = get_spherical_group(
                    (Quaternion(pd, 2*pi/3),
                     Quaternion((0,0,1), pi)),
                    self.n_symmetries // 2)

            case 'SPHERICAL', SymGrp(gyrations = [N], stars = 1,
                                     kaleidoscopes = []):
                # Vertices and faces                 # * Group N*
                pa = Vector((0,1,0))
                pb = Vector((0,0,1))
                pc =  Quaternion((0,1,0), pi/N) @ pb
                pd =  Quaternion((0,1,0), 2*pi/N) @ pb
                verts = pa, pb, pc, pd
                faces = (0,1,2), (0,2,3)

                # Rotation axes
                axes = tuple(Quaternion((0,1,0), n*2*pi/N)
                             for n in range(N))

            case 'SPHERICAL', SymGrp(gyrations = [N], xs = 1,
                                     kaleidoscopes = []):
                # Vertices and faces                 # * Group Nx
                pa = Vector((0,1,0))
                pb = Vector((0,0,1))
                pc =  Quaternion((0,1,0), pi/N) @ pb
                pd =  Quaternion((0,1,0), 2*pi/N) @ pb
                verts = pa, pb, pc, pd
                faces = (0,1,2), (0,2,3)

                # Rotation axes
                axes = tuple(Quaternion((0,1,0), n*2*pi/N)
                             for n in range(N))
                inverse_axes = tuple(Quaternion((0,1,0), n*2*pi/N + pi/N)
                                     for n in range(N))

            case 'SPHERICAL', SymGrp(gyrational = False, gyrations = [_,*_]):
                raise BadSymGrpError(
                    "Mixed spherical groups must be 2*N, 3*2, N* or Nx"
                )

            # Groups with no gyrations or miracles
            case 'SPHERICAL', SymGrp(gyrations = [], xs = 1):
                # Vertices and faces                 # * Single miracle
                verts = verts[:-1]  
                faces = (0,2,4), (0,4,3), (1,4,2), (1,3,4)

                # Rotation axes
                inverse_axes = (Quaternion((0,1,0), pi),)

            case 'SPHERICAL', SymGrp(gyrations = [], kaleidoscopes = []):
                verts = verts[:-1]                   # * Group D_1 single mirror
                faces = (0,2,4), (0,4,3), (1,4,2), (1,3,4)

            case 'SPHERICAL', SymGrp(gyrations = [],
                                     kaleidoscopes = [M, N]):
                if M != N:                           # * Group D_N (dyhedric)
                    raise BadSymGrpError("Spherical group *MN must have M = N")
                verts = (Vector((0, 0, 1)),
                         Vector((0, 0, -1)),
                         Vector((1, 0, 0)),
                         Quaternion((0,0,1), pi/N) @ Vector((1, 0, 0)),)
                faces = (0,2,3), (1,3,2)
                axes = tuple(Quaternion((0, 0, 1), i*2*pi/N) for i in range(N))

            case 'SPHERICAL', SymGrp(gyrations = [],
                                     kaleidoscopes = [M, N, P]):
                A, B, C = pi/M, pi/N, pi/P           # * Other

                # Side lengths
                c = acos((cos(C) + cos(A)*cos(B))/(sin(A)*sin(B)))
                b = acos((cos(B) + cos(C)*cos(A))/(sin(C)*sin(A)))
                
                # Vertices and faces
                pa = Vector((0, 0, 1))
                pb = Quaternion((0, 1, 0), c) @ pa
                v = Vector((0,1,0))
                v.rotate(Quaternion((0,0,1), A))
                pc = pa.copy()
                pc.rotate(Quaternion(v, b))
                
                verts = pa, pb, pc
                faces = ((0,1,2),)

                # Rotation axes
                axes = get_spherical_group(
                    [Quaternion(pa, 2*A),
                     Quaternion(pb, 2*B),
                     Quaternion(pc, 2*C)], 
                    self.n_symmetries // 2)

            case 'SPHERICAL', SymGrp(gyrational = False):
                raise BadSymGrpError(
                    "Kaleidoscopic spherical groups must be *MN or *MNP"
                )

            case _:
                raise BadSymGrpError("Bug: non-existing group found")

        if self.has_inverse_symmetry and not self.xs:
            inverse_axes = axes
        return axes, inverse_axes, verts, faces
    
    @property
    def axes(self):
        """Tuple containing the direct symmetries represented via
        quaternions"""
        if self._axes is None:
            self._calculate_axes()
        return self._axes

    @property
    def inverse_axes(self):
        """Tuple containing the inverse symmetries represented via
        quaternions.

        After rotating according to each quaternion, it is necessary
        to scale by -1 on the Y axis to get the right symmetry.

        """
        if self._inverse_axes is None:
            self._calculate_axes()
        return self._inverse_axes

    @property
    def all_axes(self):
        """Sequence of two-element tuples, where the first element is
        a quaternion, indicating rotation, and the second one is a
        scaling vector to apply after the rotation.

        """
        if self._all_axes is None:
            self._calculate_axes()
        return self._all_axes
    
    @property
    def tile(self):
        """Returns vertices and faces that make up the fundamental
        tile.

        The fundamental tile represents a maximal region that doesn't
        overlap itself when the group acts on it. Its shape is
        uniquely determined only for kaleidoscopic groups.

        In this implementation, the tile is made up of one or more
        triangles making a closed solid. All of the vertices are at
        distance 1 from the origin. One of the triangles starts from
        the North pole (0,0,1) and goes on the X directions. The XZ
        plane is a mirror whenever there are any mirrors. Different
        dispositions occur according to the order of the centers in
        the orbifold signature.

        """  
        if self._tile is None:
            self.calculate_axes()
        return self._tile

    @property
    def signature(self):
        """Orbifold signature"""
        sig = []
        for centers, name in ((self._gyrations, "gyrations"),
                              (self._kaleidoscopes, "kaleidoscopes")):
            for N in centers:
                if N == inf:
                    sig.append("0")
                elif N < 10:
                    sig.append(str(N))
                else:
                    sig.append(f"({N!r})")
            if name == "gyrations":
                sig.append("o" * self._os  +  "*" * self._stars)
            else:
                sig.append("x" * self._xs)
        return "".join(sig)

    def __repr__(self):
        return f"SymGrp('{self.signature}')"

    def __getitem__(self, position):
        return self.all_axes[position]

    def __len__(self):
        return len(self.all_axes)
