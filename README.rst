G-Code Tools
============

Tools for low-level manipulation of G-Code files. Currently includes:

- ``gcode-transform.py``: transform G-Code coordinates, allowing
  translation and rotation along Z of a pre-sliced file.

Python 3 and Numpy are required. On a Debian/Ubuntu system, run::

  sudo apt-get install python3 python3-numpy

to install the required dependencies, then run the command with
``--help`` for a brief introduction. Usage should be self-explanatory::

  ./gcode-transform.py --rotate 90 input.gcode > output.gcode

Will rotate ``input.gcode`` 90 degrees along Z over the center 125x100
(bed center on Prusa i3 printers) and write the results to
``output.gcode``.


Authors and Copyright
=====================

| Copyright(c) 2021 by wave++ "Yuri D'Elia" <wavexx@thregr.org>
| Distributed under the GNU GPLv3+ license, WITHOUT ANY WARRANTY.

``gcode-tools``'s GIT repository is publicly accessible at:

https://github.com/wavexx/gcode-tools
