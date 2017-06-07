from __future__ import print_function, division
import numpy as np
import unittest
import inspect

from six import iteritems
from collections import OrderedDict

from smt.problems import Carre, TensorProduct
from smt.sampling import LHS

from smt.utils.sm_test_case import SMTestCase
from smt.utils.silence import Silence

from smt.methods import LS, PA2, KPLS
try:
    from smt.methods import IDW, RBF, RMTC, RMTB
    compiled_available = True
except:
    compiled_available = False


print_output = False

class Test(SMTestCase):

    def setUp(self):
        ndim = 3
        nt = 500
        ne = 100

        problems = OrderedDict()
        problems['carre'] = Carre(ndim=ndim)

        sms = OrderedDict()
        if compiled_available:
            sms['RMTC'] = RMTC(num_elements=6)
            sms['RMTB'] = RMTB(order=4, num_ctrl_pts=10)

        self.nt = nt
        self.ne = ne
        self.problems = problems
        self.sms = sms

    def run_test(self, sname, extrap_train=False, extrap_predict=False):
        prob = self.problems['carre']
        sampling = LHS(xlimits=prob.xlimits)

        np.random.seed(0)
        xt = sampling(self.nt)
        yt = prob(xt)

        sm0 = self.sms[sname]

        sm = sm0.__class__()
        sm.options = sm0.options.clone()
        if sm.options.is_declared('xlimits'):
            sm.options['xlimits'] = prob.xlimits
        sm.options['print_global'] = False

        x = np.zeros((1, xt.shape[1]))
        x[0, :] = prob.xlimits[:, 1] + 1.0
        y = prob(x)

        sm.training_points = {'exact': {}}
        sm.add_training_points('exact', xt, yt)
        if extrap_train:
            sm.add_training_points('exact', x, y)

        with Silence():
            sm.train()

        if extrap_predict:
            sm.predict(x)

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTC(self):
        self.run_test('RMTC', False, False)

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTC_train(self):
        with self.assertRaises(Exception) as context:
            self.run_test('RMTC', True, False)
        self.assertEqual(str(context.exception),
                         'Training points above max for 0')

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTC_predict(self):
        self.run_test('RMTC', False, True)

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTB(self):
        self.run_test('RMTB', False, False)

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTB_train(self):
        with self.assertRaises(Exception) as context:
            self.run_test('RMTB', True, False)
        self.assertEqual(str(context.exception),
                         'Training points above max for 0')

    @unittest.skipIf(not compiled_available, 'Compiled Fortran libraries not available')
    def test_RMTB_predict(self):
        self.run_test('RMTB', False, True)


if __name__ == '__main__':
    unittest.main()
