# coding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'serpentine.settings'
from datetime import datetime
from gps.models import Trace, Trace_point
from gps import lib


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


    def get_matching_segments(self, tr1,tr2):
        start = datetime.now()
        print(start)
        tr = Trace.objects.get(id=tr1)
        segments = tr.get_matching_segments(tr2)
        print [(segment[0],segment[-1]) for segment in segments]
        end = datetime.now()
        print(end)
        print('total time spent: ' + str(end - start))
