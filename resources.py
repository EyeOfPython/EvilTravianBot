
class Resources(tuple):

    def __add__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] + other[i] for i in range(len(self)))
        else:
            raise NotImplemented("for " + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] - other[i] for i in range(len(self)))
        else:
            raise NotImplemented("for " + str(type(other)))

    def __mul__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] * other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v * other for v in self)
        else:
            raise NotImplemented("for " + str(type(other)))

    def __truediv__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] / other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v / other for v in self)
        else:
            raise NotImplemented("for " + str(type(other)))

    def __floordiv__(self, other):
        if isinstance(other, (list, tuple)):
            return Resources(self[i] // other[i] for i in range(len(self)))
        elif isinstance(other, (int, float)):
            return Resources(v // other for v in self)
        else:
            raise NotImplemented("for " + str(type(other)))
    
    def __pos__(self):
        return Resources(max(v, 0) for v in self)

    def __neg__(self):
        return Resources(-v for v in self)
