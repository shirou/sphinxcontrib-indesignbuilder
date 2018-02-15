Sphinx Indesign Builder
================================================

THIS IS NOT COMPLETED AT ALL YET.

Sphinx builder for Indesign XML format.


install
----------------

- Sphinx 1.6 or higher is required
- Python3 is recommended

::

  pip install sphinxcontrib-indesignbuilder


and add `'sphinxcontrib.indesignbuilder'` in extensions in your conf.py.

::

   extensions = [
       'sphinxcontrib.indesignbuilder',
   ]


How to use
------------

This package provides two builder

- indesign
- singleindesign

::

   make indesign

or::

   make singleindesign

Related
----------

ReVIEW
  https://github.com/kmuto/review
