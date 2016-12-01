import numpy as np
from scipy.linalg import cholesky, solve


class GPRegressor:
	def __init__(self, covfunc, sigma = 0):
		self.covfunc = covfunc
		self.sigma = sigma
	def fit(self, X, y):
		self.X = X
		self.y = y
		self.nsamples = self.X.shape[0]
		self.K = self.covfunc.K(self.X, self.X)
		self.L = cholesky(self.K + self.sigma * np.eye(self.nsamples)).T
		self.alpha = solve(self.L.T, solve(self.L, y))
		self.logp = -.5 * np.dot(self.y, self.alpha) - np.sum(np.log(np.diag(self.L))) - self.nsamples/2 * np.log(2 * np.pi)

	def param_grad(self, X, y, k_param):
		k_param_key = list(k_param.keys())
		covfunc = self.covfunc.__class__(**k_param)
		n = X.shape[0]
		K = covfunc.K(X, X)
		L = cholesky(K + self.sigma * np.eye(n)).T
		alpha = solve(L.T, solve(L, y))
		# Compute gradient matrix for each parameter
		grads = []
		for param in k_param_key:
			gradK = covfunc.gradK(X, X, param = param)
			inner = np.dot(np.atleast_2d(alpha).T, np.atleast_2d(alpha)) - np.linalg.inv(K)
			gradK = .5 * np.trace(np.dot(inner, gradK))
			grads.append(gradK)
		return np.array(grads)
			
	def predict(self, Xstar, return_std = False):
		Xstar = np.atleast_2d(Xstar)
		kstar = self.covfunc.K(self.X, Xstar).T
		fmean = np.dot(kstar, self.alpha)
		v = solve(self.L, kstar.T)
		fcov = self.covfunc.K(Xstar, Xstar) - np.dot(v.T, v)
		if return_std:
			fcov = np.diag(fcov)
		return fmean, fcov

	def update(self, xnew, ynew):
		y = np.concatenate((self.y, ynew), axis = 0)
		X = np.concatenate((self.X, xnew), axis = 0)
		self.fit(X, y)

