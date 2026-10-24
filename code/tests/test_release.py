"""Artifact integrity checks whose failures affect clean-checkout reproducibility."""
import os
from pathlib import Path
import tempfile
import unittest
from test_core import ROOT
from package_submission import build_archive


class ArchiveReproducibilityTests(unittest.TestCase):
    def test_zip_ignores_checkout_mtime_and_line_ending(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as directory:
            root=Path(directory); source=root/'main.py'; source.write_bytes(b'print(1)\r\n')
            a=root/'a.zip'; build_archive(a,[source],root)
            source.write_bytes(b'print(1)\n'); os.utime(source,(1700000000,1700000000))
            b=root/'b.zip'; build_archive(b,[source],root)
            self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_zip_member_input_order_cannot_change_hash(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as directory:
            root=Path(directory); a=root/'a.py'; b=root/'b.py'
            a.write_text('a'); b.write_text('b')
            first=root/'first.zip'; second=root/'second.zip'
            build_archive(first,[a,b],root); build_archive(second,[b,a],root)
            self.assertEqual(first.read_bytes(),second.read_bytes())

if __name__=='__main__': unittest.main()
