""" Test netcdf4 backend """

from __future__ import with_statement
import os
import sys
import pdb
from numpy.testing import TestCase, assert_array_equal, assert_equal
from pymc.examples import disaster_model
from pymc import MCMC
import pymc
import pymc.database
import torsionfit.netcdf4 as netcdf4
import torsionfit.sqlite_plus as sqlite_plus
from pymc.tests.test_database import TestPickle, TestSqlite
import numpy as np
import nose
import warnings

testdir = 'testresults'
try:
    os.mkdir(testdir)
except:
    pass


class test_backend_attribution(TestCase):

    def test_raise(self):
        self.assertRaises(AttributeError, MCMC, disaster_model, 'heysugar')

    def test_import(self):
        self.assertRaises(ImportError, MCMC, disaster_model, '__test_import__')


class TestNetcdf4(TestPickle):
    #name = 'netcdf4'

    @classmethod
    def setUpClass(self):
        #if 'netcdf4' not in dir(pymc.database):
         #   raise nose.SkipTest

        self.S = pymc.MCMC(disaster_model, db=netcdf4, dbname=os.path.join(testdir, 'Disaster.netcdf4'), dbmode='w')
        self.S.use_step_method(pymc.Metropolis, self.S.early_mean, tally=True)
        self.S.use_step_method(pymc.Metropolis, self.S.late_mean, tally=True)

    def load(self):
        return netcdf4.load(os.path.join(testdir, 'Disaster.netcdf4'))

#    def test_data(self):
#        self.db = self.load()
#        assert_array_equal(self.db.disasters, disaster_model.disaster_array)
#        self.db.close()
#        del self.db


class TestSqlitePlus(TestSqlite):

    @classmethod
    def setUpClass(self):

        self.S = pymc.MCMC(disaster_model, db=sqlite_plus, dbname=os.path.join(testdir, 'Disaster.sqlite'), dbmode='w')

    def load(self):
        return sqlite_plus.load(os.path.join(testdir, 'Disaster.sqlite'))

    def test_yrestore_state(self):

        original_filters = warnings.filters[:]
        warnings.simplefilter("ignore")

        try:
            db = self.load()
            S = pymc.MCMC(disaster_model, db=db)
            S.use_step_method(pymc.Metropolis, S.early_mean)
            S.use_step_method(pymc.Metropolis, S.late_mean)
            S.sample(10, progress_bar=0)
            sm = S.step_methods.pop()
            assert_equal(sm.accepted + sm.rejected, 75)
        finally:
            warnings.filters = original_filters
