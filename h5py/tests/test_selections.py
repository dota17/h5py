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

        # Field does not apear in named typed
        with self.assertRaises(ValueError):
            out, format = sel2.read_dtypes(dt, ('j', 'k'))

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

        dsid = self.f.create_dataset('y', (1,)).id
        with self.assertRaises(RuntimeError):
            shape, selection = sel2.read_selections_scalar(dsid, (1,))

class TestSelection(BaseSelection):

    """ High-level routes to generate a selection
    """

    def test_selection(self):
        dset = self.f.create_dataset('dset', (100,100))
        regref = dset.regionref[0:100, 0:100]

        # args is numpy.ndarray, return a FancySelection
        st = sel.select((10,), np.array([1,2,3], dtype='b'), dset)
        self.assertIsInstance(st, sel.FancySelection)

        self.assertEqual(st.mshape, (3,100))
        self.assertEqual(st.array_shape, ())

        # expand shape
        self.assertEqual(st.expand_shape(()), ())
        with self.assertRaises(TypeError):
            st.expand_shape((4,100))

        # broadcast in FancySelection
        st.broadcast((5,100))

        # args is int, return a SimpleSelection
        st2 = sel.select((10,), 1, dset)
        self.assertIsInstance(st2, sel.SimpleSelection)

        self.assertEqual(st2.mshape, (1,100))
        self.assertEqual(st2.array_shape, (100,))

        # expand shape
        self.assertEqual(st2.expand_shape(()), (1,1))
        with self.assertRaises(TypeError):
            st2.expand_shape((4,100))

        # broadcast in SimpleSelection
        st2.broadcast((5,100))

        # args is RegionReference, but dataset is None
        with self.assertRaises(TypeError):
            sel.select((100,), regref, None)

        # args is RegionReference, but its shape doesn't match dataset shape
        with self.assertRaises(TypeError):
            sel.select((100,), regref, dset)

        # args is a Selection instance, return a FancySelection
        st3 = sel.select((100,100), st, dset)
        self.assertIsInstance(st, sel.FancySelection)

        # args is a single Selection instance, but args shape doesn't match Shape
        with self.assertRaises(TypeError):
            sel.select((100,), st, dset)
