#!/usr/bin/env python3

import sys
import re
import os.path
import glob

# TODO: read extensions, header from files found in sys.path?

# A subset of the languages supported by the Listings latex package
# File extensions mapped to language names
exts = {
    "ada" : "Ada" ,
    "adb" : "Ada" ,
    "ads" : "Ada" ,
    "awk" : "Awk" ,
    "c" : "C" ,
    "h" : "C++" ,
    "hh" : "C++" ,
    "hpp" : "C++" ,
    "cxx" : "C++" ,
    "cpp" : "C++" ,
    "caml" : "Caml" ,
    "ex" : "Euphoria" ,
    "exw" : "Euphoria" ,
    "f" : "Fortran" ,
    "for" : "Fortran" ,
    "f90" : "Fortran" ,
    "fpp" : "Fortran" ,
    "html" : "HTML" ,
    "xhtml" : "HTML" ,
    "has" : "Haskell" ,
    "hs" : "Haskell" ,
    "idl" : "IDL" ,
    "java" : "Java" ,
    # pde = Processing
    "pde" : "Java" ,
    "lsp" : "Lisp" ,
    "lgo" : "Logo" ,
    "ml" : "ML" ,
    "php" : "PHP" ,
    "php3" : "PHP" ,
    "p" : "Pascal" ,
    "pas" : "Pascal" ,
    "pl" : "Perl" ,
    # pl for perl conflicts with pl for Prolog...
    "py" : "Python" ,
    "r" : "R" ,
    "rb" : "Ruby" ,
    "sas" : "SAS" ,
    "sql" : "SQL" ,
    "tex" : "TeX" ,
    "vbs" : "VBScript" ,
    "vhd" : "VHDL" ,
    "vrml" : "VRML" ,
    "v" : "Verilog" ,
    "xml" : "XML" ,
    "xslt" : "XSLT" ,
    "bash" : "bash" ,
    "csh" : "csh" ,
    "ksh" : "ksh" ,
    "sh" : "sh" ,
    "tcl" : "tcl"
}

latexspecials = "\\{}_^#&$%~"
specials_re = re.compile(
    '(%s)' % '|'.join(re.escape(c) for c in latexspecials)
)


def makeTop(output=sys.stdout, show_whitespace="false"):
    # print out the file header
    header = '''
\\documentclass{article}
\\usepackage{layout}
\\usepackage[hmargin=1in,vmargin=1in]{geometry}
\\usepackage{listings}
\\usepackage{color}
% \\usepackage{courier}
% For better handling of unicode (Latin characters, anyway)
\\IfFileExists{lmodern.sty}{\\usepackage{lmodern}}{}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
%\\usepackage[german]{babel}

\\usepackage[colorlinks=true,linkcolor=blue]{hyperref}

\\lstset{
    belowcaptionskip=1\\baselineskip,
    xleftmargin=\\parindent,
    % numbers=left,                   % where to put the line-numbers
    % numberstyle=\\small \\ttfamily \\color[rgb]{0.4,0.4,0.4},
                % style used for the linenumbers
    showspaces=__WHITESPACE__,               % show spaces adding special underscores
    showstringspaces=false,         % underline spaces within strings
    showtabs=__WHITESPACE__,                 % show tabs within strings adding particular underscores
    frame=lines,                    % add a frame around the code
    tabsize=2,                        % default tabsize: 4 spaces
    breaklines=true,                % automatic line breaking
    breakatwhitespace=true,        % automatic breaks should only happen at whitespace
    basicstyle=\\large\\ttfamily\\color[rgb]{0,0,0},
    identifierstyle=\\Large\\color[rgb]{0.3,0.133,0.133},   % colors in variables and function names, if desired.
    keywordstyle=\\Large\\color[rgb]{0.133,0.133,0.6},
    commentstyle=\\large\\color[rgb]{0.133,0.545,0.133},
    stringstyle=\\large\\color[rgb]{0.627,0.126,0.941},
}
\\linespread{1.2}
\\setlength{\\voffset}{-2.0cm}
\\setlength{\\hoffset}{-2.5cm}
\\setlength{\\footskip}{0cm}
\\setlength{\\textheight}{750pt}
\\setlength{\\textwidth}{610pt}
\\setlength{\\marginparwidth}{5pt}


\\begin{document}
% \\layout
\\tableofcontents

'''
    print(header.replace('__WHITESPACE__', show_whitespace), file=output)


def makeBottom(output=sys.stdout):
    print("\\end{document}", file=output)

PREVIOUS_NAMES = []
PARTS_NAME = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']
def make_parts_name(filename):
    '''Return a list of (name, part_name). Such as [('client', 'subsection'), ('__init__', 'subsubsection)]'''
    filename = re.sub('^/', '', filename)

    global PREVIOUS_NAMES

    names = filename.split('/')
    if len(names) > 5:
        t = names[:3]
        s = '/'.join(names[4:])
        t.append(s)
        names = t

    j = 0
    for (i, name) in enumerate(PREVIOUS_NAMES):
        if names[i] != name:
            j = i
            break

    rst = []
    for i in range(j, len(names)):
        rst.append([names[i], PARTS_NAME[i]])

    PREVIOUS_NAMES = names
    return rst


def addListing(filename, custom_heading=None, output=sys.stdout):
    heading = filename
    if custom_heading is not None:
        heading = custom_heading

    # remove DIR part
    heading = re.sub('%s/'%DIR, '', heading)
    heading_escaped = re.sub(specials_re, r'\\\1', heading)

    parts = make_parts_name(heading_escaped)
    print("\\newpage", file=output)
    for part in parts:
        # print("\\section{%s}" % heading_escaped, file=output)
        print("\\%s[%s]{%s}" % (part[1], part[0], heading_escaped), file=output)

    ext = filename.split('.')[-1]
    lang = exts.get(ext, '')
    # uses '' if extension not found in our dictionary
    print("\\lstinputlisting[language=%s]{\"%s\"}" % (lang, filename), file=output)
    print("", file=output)


def main():
    if len(sys.argv) < 2:
        sys.exit('''Usage: %s [-s] FILE [FILE2] [FILE3] [...]
 Outputs .tex file to STDOUT (redirect with \"%s FILE.py > FILE.tex\")
 Languages (for syntax highlighting) determined from file extensions.
 If -s is given as the first argument, the resulting document will display
 whitespace in the code as printable characters.
 ''' % (sys.argv[0], sys.argv[0]))

    if sys.argv[1] == '-s':
        show_whitespace = "true"
        files = sys.argv[2:]  # get all other command line arguments
    else:
        show_whitespace = "false"
        files = sys.argv[1:]  # get all command line arguments

    # Check existence of all files first
    for infile in files:
        if not os.path.isfile(infile):
            sys.exit("File not found: %s" % infile)

    # Make the file (output to STDOUT)
    makeTop(show_whitespace=show_whitespace)
    for infile in files:
        addListing(infile)
    makeBottom()

DIR = '/'
def process_files(files):
    # Check existence of all files first
    for infile in files:
        if not os.path.isfile(infile):
            sys.exit("File not found: %s" % infile)

    # Make the file (output to STDOUT)
    makeTop(show_whitespace="false")
    for infile in files:
        addListing(infile)
    makeBottom()


def process_dir(dir):
    files = glob.glob('%s/**' % (dir), recursive=True)
    # process_files(files)
    print(files)
    print(len(files))

def process_python_dir(dir):
    files = glob.glob('%s/**' % (dir), recursive=True)

    files = [f for f in files if os.path.isfile(f)]
    files = [f for f in files if f.endswith('py')]

    process_files(files)

def process_tensorflow_dir(dir):
    files = glob.glob('%s/**' % (dir), recursive=True)
    ignores = ['kernel_tests', 'keras', 'debug']
    files = [f for f in files if not re.search('/%s/' % '|'.join(ignores), f)]

    files = [f for f in files if os.path.isfile(f)]
    files = [f for f in files if f.endswith('py')]

    # print(files)
    # print(len(files))
    process_files(files)


if __name__ == "__main__":
    # main()
    dir = sys.argv[1]
    DIR = dir
    process_tensorflow_dir(dir)
    # process_python_dir(dir)
