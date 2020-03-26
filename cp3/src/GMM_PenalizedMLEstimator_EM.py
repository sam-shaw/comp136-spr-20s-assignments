'''
Summary
=======
Defines a penalized ML estimator for Gaussian Mixture Models, using Expectation-Maximization.

Supports these API functions common to any sklearn-like GMM unsupervised learning model:

* fit

Resources
=========
See COMP 136 CP3 assignment on course website for the complete problem description and all math details
https://www.cs.tufts.edu/comp/136/2020s/cp3.html

Examples
========
>>> np.set_printoptions(suppress=False, precision=3, linewidth=80)
>>> D = 2

## Verify that variance penalty works as expected
# Empty components (with no assigned data) should have variance equal to the intended "mode" of the penalty
# We'll use a mode of 2.0 (so stddev = sqrt(2.0) = 1.414...)
>>> gmm_em = GMM_PenalizedMLEstimator_EM(K=3, D=2, seed=42, variance_penalty_mode=2.0)
>>> empty_ND = np.zeros((0,D))
>>> log_pi_K, mu_KD, stddev_KD = gmm_em.generate_initial_parameters(empty_ND)
>>> calc_negative_log_likelihood(empty_ND, log_pi_K, mu_KD, stddev_KD)
-0.0
>>> gmm_em.fit(empty_ND, verbose=False)
>>> gmm_em.stddev_KD
array([[1.414, 1.414],
       [1.414, 1.414],
       [1.414, 1.414]])

>>> N = 25
>>> prng = np.random.RandomState(8675309)
>>> x1_ND = 0.1 * prng.randn(N, D) + np.asarray([[0, 0]])
>>> x2_ND = 0.1 * prng.randn(N, D) + np.asarray([[-1, 0]])
>>> x3_ND = np.asarray([[0.2, 0.05]]) * prng.randn(N, D) + np.asarray([[0, +1]])
>>> x_ND = np.vstack([x1_ND, x2_ND, x3_ND])
>>> gmm_em = GMM_PenalizedMLEstimator_EM(K=3, D=2, seed=42, variance_penalty_mode=2.0)
>>> gmm_em.fit(x_ND, verbose=False)
>>> np.exp(gmm_em.log_pi_K)
array([0.333, 0.333, 0.333])
>>> gmm_em.mu_KD
array([[-1.008,  0.009],
       [-0.005,  1.005],
       [-0.007,  0.01 ]])
>>> gmm_em.stddev_KD
array([[0.098, 0.103],
       [0.24 , 0.042],
       [0.076, 0.091]])
'''

import numpy as np
from collections import defaultdict
import scipy.stats as stats
from scipy.special import logsumexp
import scipy.optimize
import time

from GMM_PenalizedMLEstimator_LBFGS import (
    GMM_PenalizedMLEstimator_LBFGS,
    calc_negative_log_likelihood)

class GMM_PenalizedMLEstimator_EM(GMM_PenalizedMLEstimator_LBFGS):
    """ Maximum Likelihood Estimator for Gaussian Mixture models, trained with EM.

    Attributes
    ----------
    K : int
        Number of components
    D : int
        Number of data dimensions
    seed : int
        Seed for random number generator used for initialization
    variance_penalty_mode : float
        Must be positive.
        Defines mode of penalty on variance.
        See calc_penalty_stddev module.
    variance_penalty_spread : float,
        Must be positive.
        Defines spread of penalty on variance.
        See calc_penalty_stddev module.
    max_iter : int
        Maximum allowed number of iterations for training algorithm
    ftol : float
        Threshold that determines if training algorithm has converged
        Same definition as `ftol` setting used by scipy.optimize.minimize

    Additional Attributes (after calling fit)
    -----------------------------------------
    log_pi_K : 1D array, shape (K,)
        GMM parameter: Log of mixture weights
        Must satisfy logsumexp(log_pi_K) == 0.0 (which means sum(exp(log_pi_K)) == 1.0)
    mu_KD : 2D array, shape (K, D)
        GMM parameter: Means of all components
        The k-th row is the mean vector for the k-th component
    stddev_KD : 2D array, shape (K, D)
        GMM parameter: Standard Deviations of all components
        The k-th row is the stddev vector for the k-th component
    history : dict of lists
        Access performance metrics computed throughout iterative training.
        history['iter'] contains integer iteration count at each checkpoint
        history['train_loss'] contains training loss value at each checkpoint
        history['valid_neg_log_lik_per_pixel'] contains validation score at each checkpoint
            Normalized "per pixel" means divided by total number of observed feature dimensions (pixels)
            So that values for different size datasets can be fairly compared.

    Inherits
    --------
    * Constructor __init__() from GMM_PenalizedMLEstimator_LBFGS parent class
    * Initialization method generate_initial_parameters() from parent as well
    """

    
    def calc_EM_loss(self, r_NK, x_ND):
        ''' Compute the overall loss function minimized by the EM algorithm

        Includes three additive terms:
        * Negative of the expected complete likelihoods E_q[ log p(x,z)]
        * Negative of the entropy of the assignment distribution q(z|r)
        * Penalty on the standard deviation parameters

        Args
        ----
        r_NK : 2D array, shape (N, K)
            Parameters that define the approximate assignment distribution q(z)
            The n-th row r_NK[n] defines the K-length vector r_n that is non-negative & sums to one.
            Can interpret r_NK[n,k] as the probability of assigning cluster k to n-th example
            Formally, the n-th example's assignment distribution is given by:
                q(z_n | r_n) = CategoricalPMF(z_n | r_n[0], r_n[1], ... r_n[K-1])
        x_ND : 2D array, shape (N, D)
            Dataset of observed feature vectors
            The n-th row x_ND[n] defines a length-D feature vector

        Returns
        -------
        loss_em : float
            scalar value of the loss of provided x and r arrays
            Uses this object's internal GMM params (self.log_pi_K, self.mu_KD, self.stddev_KD)
        '''
        ## TODO compute the loss for EM (see 3 additive terms described above)
        ## For hints, see the objective defined in day 16 lecture notes
        return 0.0

    def estep__calc_r_NK(self, x_ND):
        ''' Perform E-step to update assignment variables r controling q(z | r)

        Returned value will optimize the EM loss function for r given fixed current GMM parameters

        Args
        ----
        x_ND : 2D array, shape (N, D)
            Dataset of observed feature vectors
            The n-th row x_ND[n] defines a length-D feature vector

        Returns
        -------
        r_NK : 2D array, shape (N, K)
            The n-th row r_NK[n] defines the K-length vector r_n that is non-negative & sums to one.
            Can interpret r_NK[n,k] as the probability of assigning cluster k to n-th example
            Formally, the n-th example's assignment distribution is given by:
                q(z_n | r_n) = CategoricalPMF(z_n | r_n[0], r_n[1], ... r_n[K-1])
        '''
        N = x_ND.shape[0]
        r_NK = np.zeros((N, self.K))
        r_NK[:,0] = 1.0
        ## TODO update r_NK to optimal value given current GMM parameters
        assert np.allclose(np.sum(r_NK, axis=1), 1.0)
        return r_NK

    def mstep__update_log_pi_K(self, r_NK):
        ''' Perform M-step to update mixture weights pi

        Returned value will optimize the EM loss function for log_pi_K given fixed other parameters

        Args
        ----
        r_NK : 2D array, shape (N, K)
            The n-th row r_NK[n] defines the K-length vector r_n that is non-negative & sums to one.
            Can interpret r_NK[n,k] as the probability of assigning cluster k to n-th example

        Returns
        -------
        log_pi_K : 1D array, shape (K,)
            GMM parameter: Log of mixture weights
            Must satisfy logsumexp(log_pi_K) == 0.0 (which means sum(exp(log_pi_K)) == 1.0)
        '''
        ## TODO compute optimal update of log_pi_K
        log_pi_K = np.log(1.0/self.K * np.ones(self.K))
        return log_pi_K

    def mstep__update_mu_KD(self, r_NK, x_ND):
        ''' Perform M-step to update component means mu

        Returned value will optimize the EM loss function for mu_KD given fixed other parameters

        Args
        ----
        r_NK : 2D array, shape (N, K)
            The n-th row r_NK[n] defines the K-length vector r_n that is non-negative & sums to one.
            Can interpret r_NK[n,k] as the probability of assigning cluster k to n-th example

        Returns
        -------
        mu_KD : 2D array, shape (K, D)
            GMM parameter: Means of all components
            The k-th row is the mean vector for the k-th component
        '''
        ## TODO compute optimal update of mu_KD
        mu_KD = np.zeros((self.K, self.D))
        return mu_KD

    def mstep__update_stddev_KD(self, r_NK, x_ND):
        ''' Perform M-step to update component stddev parameters sigma

        Returned value will optimize the EM loss function for stddev_KD given fixed other parameters

        Args
        ----
        r_NK : 2D array, shape (N, K)
            The n-th row r_NK[n] defines the K-length vector r_n that is non-negative & sums to one.
            Can interpret r_NK[n,k] as the probability of assigning cluster k to n-th example

        Returns
        -------
        stddev_KD : 2D array, shape (K, D)
            GMM parameter: Standard Deviations of all components
            The k-th row is the stddev vector for the k-th component
        '''
        ## TODO compute optimal update of stddev_KD
        stddev_KD = np.ones((self.K, self.D))
        return stddev_KD


    def fit(self, x_ND, x_valid_ND=None, verbose=True):
        ''' Fit this estimator to provided training data using EM algorithm

        Args
        ----
        x_ND : 2D array, shape (N, D)
            Dataset used for training.
            Each row is an observed feature vector of size D
        x_valid_ND : 2D array, shape (Nvalid, D), optional
            Optional, dataset used for heldout validation.
            Each row is an observed feature vector of size D
            If provided, used to measure heldout likelihood at every checkpoint.
            These likelihoods will be recorded in self.history['valid_neg_log_lik_per_pixel']
        verbose : boolean, optional, defaults to True
            If provided, a message will be printed to stdout after every iteration,
            indicating the current training loss and (if possible) validation score.

        Returns
        -------
        self : this GMM object
            Internal attributes log_pi_K, mu_KD, stddev_KD updated.
            Performance metrics stored after every iteration in history 
        '''
        N = np.maximum(x_ND.shape[0], 1.0)

        ## Define initial parameters
        self.log_pi_K, self.mu_KD, self.stddev_KD = self.generate_initial_parameters(x_ND)

        self.history = defaultdict(list)
        start_time_sec = time.time()
        for iter_id in range(self.max_iter + 1):

            ## Loss step
            tr_neg_log_lik = self.calc_negative_log_likelihood(x_ND)
            loss_incomplete = tr_neg_log_lik + self.calc_penalty_stddev()
            self.history['iter'].append(iter_id)
            self.history['train_loss'].append(loss_incomplete)
            self.history['train_loss_per_pixel'].append(loss_incomplete / (N * x_ND.shape[1]))
            self.history['train_neg_log_lik_per_pixel'].append(tr_neg_log_lik / (N * x_ND.shape[1]))

            if x_valid_ND is None:
                va_neg_log_lik_message = ""
            else:
                ## TODO compute the per-pixel negative log likelihood on validation set
                ## Use calc_negative_log_lik and x_valid_ND
                va_neg_log_lik_per_pixel = 0.0
                self.history['valid_neg_log_lik_per_pixel'].append(va_neg_log_lik_per_pixel)
                va_neg_log_lik_message = "| valid score %9.6f" % (self.history['valid_neg_log_lik_per_pixel'][-1])

            ## E step
            r_NK = self.estep__calc_r_NK(x_ND)
            if self.do_double_check_correctness:
                # Verify the loss after the E step is equal to the incomplete loss
                loss_e = self.calc_EM_loss(r_NK, x_ND)
                self.history['train_loss_em'].append(loss_e)
                ## TODO this should pass: assert np.allclose(loss_incomplete, loss_e)

            ## M step
            if r_NK.shape[0] > 1:
                self.log_pi_K = self.mstep__update_log_pi_K(r_NK)
                self.mu_KD = self.mstep__update_mu_KD(r_NK, x_ND)
            self.stddev_KD = self.mstep__update_stddev_KD(r_NK, x_ND)

            if self.do_double_check_correctness:
                # Verify the loss goes down after the M step
                loss_m = self.calc_EM_loss(r_NK, x_ND)
                self.history['train_loss_em'].append(loss_m)
                ## TODO this should pass: assert loss_m + 1e-9 <= loss_e

            if verbose:
                print("iter %4d / %4d after %9.1f sec | train loss % 9.6f %s" % (
                    iter_id, self.max_iter, time.time() - start_time_sec,
                    self.history['train_loss_per_pixel'][-1],
                    va_neg_log_lik_message,
                    ))
            # The iteration stops when (f^k - f^{k+1})/max{|f^k|,|f^{k+1}|,1} <= ftol.
            if iter_id >= 2:
                fnew = self.history['train_loss'][-1]
                fold = self.history['train_loss'][-2]
                numer = (fold - fnew)
                denom = np.max(np.abs([fnew, fold, 1]))
                if numer / denom <= self.ftol:
                    break
