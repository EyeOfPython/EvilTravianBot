
class Resources(tuple):
    
    def __new__(cls, d=None):
        if d is not None:
            d = list(d)
            assert len(d) == 4, 'Four values have to be present, but %s are.' % (d,)
            return super().__new__(cls, d)
        
        return super().__new__(cls, (0,0,0,0))

    def __add__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] + other[i] for i in range(len(self)))
        else:
            raise NotImplementedError("for " + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] - other[i] for i in range(len(self)))
        else:
            raise NotImplementedError("for %s(%s)" %(type(other), other) )

    def __mul__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] * other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v * other for v in self)
        else:
            raise NotImplementedError("for %s(%s)" %(type(other), other) )

    def __truediv__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] / other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v / other for v in self)
        else:
            raise NotImplementedError("for %s(%s)" %(type(other), other) )

    def __floordiv__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] // other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v // other for v in self)
        else:
            raise NotImplementedError("for %s(%s)" %(type(other), other) )
    
    def __pos__(self):
        return Resources(max(v, 0) for v in self)

    def __neg__(self):
        return Resources(-v for v in self)
