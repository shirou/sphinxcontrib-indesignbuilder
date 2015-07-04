Sphinx Indesign Builder 
================================================

THIS IS NOT COMPLETED AT ALL YET.

Sphinx builder for Indesign XML format.


install
----------------

::

  pip install sphinxcontrib-indesignbuilder


and add `'sphinxcontrib.indesignbuilder'` in extensions in your conf.py.

::

   extensions = [
       'sphinx.ext.ifconfig',
       'sphinxcontrib.indesignbuilder',
   ]


builder
------------

This package provides two builder

- indesign
- singleindesign

You can add these line to invoke builder.

::

   indesign:
           $(SPHINXBUILD) -b indesign $(ALLSPHINXOPTS) $(BUILDDIR)/indesign
           @echo
           @echo "Build finished. The XML files are in $(BUILDDIR)/indesign."
   singleindesign:
           $(SPHINXBUILD) -b singleindesign $(ALLSPHINXOPTS) $(BUILDDIR)/singleindesign
           @echo
           @echo "Build finished. The XML file is in $(BUILDDIR)/singleindesign."

Related
----------

ReVIEW
  https://github.com/kmuto/review





