# IPython profile configuration file (not for execution).
# Symlink to the directory of all tutorial notebooks to apply 
# default settings.

# matplotlibrc customisation
c.InlineBackend.rc = {}

# Set default figure dpi
c.InlineBackend.rc.update({"figure.dpi": 80})

# Font tips (for future reference)
# - Refresh matplotlib font cache: matplotlib.font_manager._rebuild()

# Display figures in vector format
#c.InlineBackend.figure_formats = {'pdf', 'svg'}

# Display figures in raster format
c.InlineBackend.figure_formats = {'png', 'jpg'}
#c.InlineBackend.print_figure_kwargs.update({'quality' : 95})
