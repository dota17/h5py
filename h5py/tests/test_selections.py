# This file is part of h5py, a Python interface to the HDF5 library.
#
# http://www.h5py.org
#
# Copyright 2008-2013 Andrew Collette and contributors
#
# License:  Standard 3-clause BSD; see "license.txt" for full license terms
#           and contributor agreement.

"""
    Tests for the (internal) selections module
"""

import numpy as np
import h5py
import h5py._hl.selections as sel
import h5py._hl.selections2 as sel2

from .common import TestCase, ut

class BaseSelection(TestCase):
    def setUp(self):
        self.f = h5py.File(self.mktemp(), 'w')
        self.dsid = self.f.create_dataset('x', ()).id

    def tearDown(self):
        if self.f:
            self.f.close()

class TestTypeGeneration(BaseSelection):

    """
        Internal feature: Determine output types from dataset dtype and fields.
    """

    def test_simple(self):
        """ Non-compound types are handled appropriately """
        dt = np.dtype('i')
        out, format = sel2.read_dtypes(dt, ())
        self.assertEqual(out, format)
        self.assertEqual(out, np.dtype('i'))

    def test_simple_fieldexc(self):
        """ Field names for non-field types raises ValueError """
        dt = np.dtype('i')
        with self.assertRaises(ValueError):
            out, format = sel2.read_dtypes(dt, ('a',))

    def test_compound_simple(self):
        """ Compound types with elemental subtypes """
        dt = np.dtype( [('a','i'), ('b','f'), ('c','|S10')] )

        # Implicit selection of all fields -> all fields
        out, format = sel2.read_dtypes(dt, ())
        self.assertEqual(out, format)
        self.assertEqual(out, dt)

        # Explicit selection of fields -> requested fields
        out, format = sel2.read_dtypes(dt, ('a','b'))
        self.assertEqual(out, format)
        self.assertEqual(out, np.dtype( [('a','i'), ('b','f')] ))

        # Explicit selection of exactly one field -> no fields
        out, format = sel2.read_dtypes(dt, ('a',))
        self.assertEqual(out, np.dtype('i'))
        self.assertEqual(format, np.dtype( [('a','i')] ))


class TestScalarSliceRules(BaseSelection):

    """
        Internal feature: selections rules for scalar datasets
    """

    def test_args(self):
        """ Permissible arguments for scalar slicing """
        shape, selection = sel2.read_selections_scalar(self.dsid, ())
        self.assertEqual(shape, None)
        self.assertEqual(selection.get_select_npoints(), 1)

        shape, selection = sel2.read_selections_scalar(self.dsid, (Ellipsis,))
        self.assertEqual(shape, ())
        self.assertEqual(selection.get_select_npoints(), 1)

        with self.assertRaises(ValueError):
            shape, selection = sel2.read_selections_scalar(self.dsid, (1,))

class TestSelection(BaseSelection):
    def test_selection(self):
        #args = (h5py.RegionReference,)
        #dset1 = self.f.create_dataset('dset', (10,10))
        #regref = dset1.regionref[...]
        #select = sel.select((10,), args, dset1)
        pass
