from unittest import TestCase
import stage
import os
import sys


__author__ = 'mhenry'


class TestStage(TestCase):
    def test_stage(self):
        os.chdir("Y:\RPE\RPE 3.5.2\RPE 3.5.2 Hotfix 8")
        stage.stage('.hotfix\spec.xml', 'd:\\hotfixbuilds', False)
