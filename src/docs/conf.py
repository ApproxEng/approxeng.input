# General information about the project.
project = u'Approximate Engineering - Input'
copyright = u'2017 to 2024 Tom Oinn'
author = u'Tom Oinn'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '2.6.4'
# The full version, including alpha/beta/rc tags.
release = '2.6.4'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    'sphinx.ext.mathjax',
    'sphinx.ext.inheritance_diagram',
]

# Configure graphviz to generate PNG and set up some default colours and graph styling. We were using SVGs here, but
# it seems that pythonhosted.org isn't setting their MIME type correctly and is therefore failing to display.
graphviz_output_format = 'png'
graphviz_dark_colour = '#343131'
graphviz_background_colour = 'linen'
graphviz_dot_args = ['-Gbgcolor=transparent', '-Nshape=rectangle', '-Nfontname=courier', '-Nfontsize=12', '-Nheight=0',
                     '-Nwidth=0', '-Nfillcolor={}'.format(graphviz_background_colour),
                     '-Ncolor={}'.format(graphviz_dark_colour), '-Nstyle=filled',
                     '-Nfontcolor={}'.format(graphviz_dark_colour), '-Efontcolor={}'.format(graphviz_dark_colour),
                     '-Ecolor={}'.format(graphviz_dark_colour)]

source_suffix = '.rst'
master_doc = 'index'
nitpicky = True
language = 'en'
today_fmt = '%B %d, %Y'


# Define skip rules to exclude some functions and other members from autodoc
def skip(app, what, name, obj, skip, options):
    if name == "__init__":
        return False
    if name == "as_dict" or name == "from_dict":
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `to do` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

# Configures links into the main Python language docs
intersphinx_mapping = {'python': ('https://docs.python.org/3.11', None),
                       'evdev': ('https://python-evdev.readthedocs.io/en/latest/', None)}

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
html_use_opensearch = 'https://approxeng.github.io/approxeng.input'

# This is the file name suffix for HTML files (e.g. ".xhtml").
html_file_suffix = '.html'

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
html_search_language = 'en'
