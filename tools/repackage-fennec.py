#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# https://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/latest-mozilla-central-android/gecko-unsigned-unaligned.apk

from __future__ import print_function

import os
import errno
import sys

import argparse
import shutil
import tempfile
import subprocess

# parse command line arguments
parser = argparse.ArgumentParser(description="Re-package Fennec Nightly for local Android Services development.")
parser.add_argument("-v", dest="verbose", action="store_true", default=True, help="verbose output")
parser.add_argument("input", default="gecko-unsigned-unaligned.apk", help="Unsigned and unaligned APK filename.")
parser.add_argument("output", default="gecko.apk", help="Signed and aligned APK filename.")
args = parser.parse_args(sys.argv[1:])

def verbose(*xargs):
    if args.verbose:
        print(*xargs, file=sys.stderr)

class FennecRepackager:
    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

    def repackage(self):
        verbose("Re-packaging", self.input_filename, "to", self.output_filename)

        temp_dir = tempfile.mkdtemp()
        verbose("Created temporary directory", temp_dir)

        try:
            gecko = self._repackage(temp_dir)
            verbose("Re-packaged", gecko)

            shutil.copy(gecko, self.output_filename)
            verbose("Wrote to", self.output_filename)
        finally:
            if temp_dir is not None:
                shutil.rmtree(temp_dir)
                verbose("Deleted temporary directory", temp_dir)

    def _ensure_debugkeystore(self):
        path = os.path.expanduser("~/.android")

        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        keystore = os.path.join(path, "debug.keystore")

        if not os.path.exists(keystore):
            # we can create an android debug keystore.
            args = [ "keytool",
                     "-genkey",
                     "-v",
                     "-keystore", keystore,
                     "-storepass", "android",
                     "-alias", "androiddebugkey",
                     "-keypass", "android",
                     "-dname", "CN=Android Debug,O=Android,C=US" ]
            subprocess.check_call(args)

        return keystore

    def _repackage(self, temp_dir):
        gecko_u = os.path.join(temp_dir, "gecko.u.apk")
        shutil.copy(self.input_filename, gecko_u)

        keystore = self._ensure_debugkeystore()

        # jarsigner updates APK in place.
        args = [ "jarsigner",
                 "-digestalg", "SHA1",
                 "-sigalg", "MD5withRSA",
                 "-keystore", keystore,
                 "-storepass", "android",
                 gecko_u,
                 "androiddebugkey" ]
        subprocess.check_call(args)

        # zipalign outputs a new file.
        gecko = os.path.join(temp_dir, "gecko.apk")
        args = [ "zipalign",
                 "-f", "4",
                 gecko_u,
                 gecko ]
        subprocess.check_call(args)

        return gecko

# ~/Mozilla/test $ zipalign -f 4 gecko.u.apk gecko.apk
# ~/Mozilla/test $ adb install gecko.apk

        # import urllib

        # gecko_uu = os.path.join(temp_dir, "gecko.uu.apk")
        # urllib.urlretrieve("https://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/latest-mozilla-central-android/gecko-unsigned-unaligned.apk", gecko_uu)



frp = FennecRepackager(args.input, args.output)
frp.repackage()
