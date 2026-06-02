# -*- coding: utf-8 -*-
# Thin launcher — PyInstaller entry script.
#
# ALL application logic lives in the Cython-compiled `apppp_integrated`
# extension module (apppp_integrated.*.pyd, native machine code). Importing it
# executes the entire app, because apppp_integrated runs its UI build and
# `app.mainloop()` at module level.
#
# The frozen bytecode of THIS file contains no application logic, so extracting
# the PyInstaller entry reveals nothing. The real code is one-way compiled native
# code in the .pyd; the plaintext bytecode of the source is stripped from the PYZ
# by the build spec (a.pure filter).
import apppp_integrated  # noqa: F401,E401
