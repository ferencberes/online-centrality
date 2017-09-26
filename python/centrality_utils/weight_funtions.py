import math

### Weight function objects ###

class ConstantWeighter:
	def __init__(self, c=1):
		self.c = c

	def weight(self, x):
		return self.c

	def __repr__(self):
		return 'Const(%.2f)' % self.c


class PowerWeighter:
	def __init__(self, norm=1.0, exponent=-1.0):
		"""Set negative value for exponent!"""
		self.exponent, self.norm = exponent, norm

	def weight(self, x):
		return math.pow(1 + float(x)/self.norm, self.exponent)

	def __repr__(self):
		return 'Pow(e:%.3f,n:%.3f)' % (self.exponent, self.norm)


class ExponentialWeighter:
	def __init__(self, norm=1.0, base=0.5):
		"""Set value smaller than 1 for base!"""
		self.base, self.norm = base, norm

	def weight(self, x):
		return math.pow(self.base, float(x)/self.norm)

	def __repr__(self):
		return 'Exp(b:%.3f,n:%.3f)' % (self.base, self.norm)


class RayleighWeighter:
	def __init__(self, norm=1.0, sigma=1.0):
		self.sigma, self.norm = sigma, norm
		self.var = self.sigma**2

	def weight(self, x):
		val = float(x) / self.norm
		return (1.0/self.var) * val * math.exp(-1.0 * val**2 / (2*self.var))

	def __repr__(self):
		return 'Ray(s%.3f,n:%.3f)' % (self.sigma, self.norm)
