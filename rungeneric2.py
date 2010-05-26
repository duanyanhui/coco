#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Routines for the comparison of 2 algorithms.
Synopsis:
    python path_to_folder/bbob_pproc/runcomp2.py [OPTIONS] FOLDER_NAME1 FOLDER_NAME2...
Help:
    python path_to_folder/bbob_pproc/runcomp2.py -h

"""

from __future__ import absolute_import

import os
import sys
import glob
import warnings
import getopt
from pdb import set_trace

# Add the path to bbob_pproc
if __name__ == "__main__":
    # append path without trailing '/bbob_pproc', using os.sep fails in mingw32
    #sys.path.append(filepath.replace('\\', '/').rsplit('/', 1)[0])
    (filepath, filename) = os.path.split(sys.argv[0])
    #Test system independent method:
    sys.path.append(os.path.join(filepath, os.path.pardir))

from bbob_pproc import pprldistr
from bbob_pproc.pproc import DataSetList, processInputArgs
from bbob_pproc.comp2 import ppfig2, pprldistr2, pptable2, ppscatter

# Used by getopt:
shortoptlist = "hvo:"
longoptlist = ["help", "output-dir", "noisy", "noise-free", "fig-only",
               "rld-only", "tab-only", "sca-only", "verbose"]

#CLASS DEFINITIONS

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


#FUNCTION DEFINITIONS

def usage():
    print main.__doc__

def main(argv=None):
    """Generates some outputs from BBOB experiment data sets of two algorithms.

    Provided with some data, this routine outputs figure and TeX files in the
    folder 'cmp2data' needed for the compilation of the latex document
    templateBBOBcmparticle.tex. These output files will contain performance
    tables, performance scaling figures, scatter plot figures and empirical
    cumulative distribution figures. On subsequent executions, new files will
    be added to the output directory, overwriting existing files in the
    process.

    Keyword arguments:
    argv -- list of strings containing options and arguments. If not given,
    sys.argv is accessed.

    argv must list folders containing BBOB data files. Each of these folders
    should correspond to the data of ONE algorithm.

    Furthermore, argv can begin with, in any order, facultative option flags
    listed below.

        -h, --help

            display this message

        -v, --verbose

            verbose mode, prints out operations. When not in verbose mode, no
            output is to be expected, except for errors.

        -o, --output-dir OUTPUTDIR

            change the default output directory ('cmp2data') to OUTPUTDIR

        --noise-free, --noisy

            restrain the post-processing to part of the data set only. Actually
            quicken the post-processing since it loads only part of the pickle
            files.

        --fig-only, --rld-only, --tab-only, --sca-only

            these options can be used to output respectively the ERT graphs
            figures, run length distribution figures or the comparison tables
            scatter plot figures only. Any combination of these options results
            in no output.

    Exceptions raised:
    Usage -- Gives back a usage message.

    Examples:

    * Calling the runcomp2.py interface from the command line:

        $ python bbob_pproc/runcomp2.py -v Alg0-baseline Alg1-of-interest

    will post-process the data from folders Alg0-baseline and Alg1-of-interest,
    the former containing data for the reference algorithm (zero-th) and the
    latter data for the algorithm of concern (first). The results will be
    output in folder cmp2data. The -v option adds verbosity.

    * From the python interactive shell (requires that the path to this
      package is in python search path):

        >>> from bbob_pproc import runcomp2
        >>> runcomp2.main('-o outputfolder PSO DEPSO'.split())

    This will execute the post-processing on the data found in folder
    PSO and DEPSO. The -o option changes the output folder from the default
    cmp2data to outputfolder.

    """

    if argv is None:
        argv = sys.argv[1:]
        # The zero-th input argument which is the name of the calling script is
        # disregarded.

    try:

        try:
            opts, args = getopt.getopt(argv, shortoptlist, longoptlist)
        except getopt.error, msg:
             raise Usage(msg)

        if not (args):
            usage()
            sys.exit()

        isfigure = True
        isrldistr = True
        istable = True
        isscatter = True
        isNoisy = False
        isNoiseFree = False # Discern noisy and noisefree data?
        verbose = False
        outputdir = 'cmp2data'

        #Process options
        for o, a in opts:
            if o in ("-v","--verbose"):
                verbose = True
            elif o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-o", "--output-dir"):
                outputdir = a
            elif o == "--fig-only":
                isrldistr = False
                istable = False
                isscatter = False
            elif o == "--rld-only":
                isfigure = False
                istable = False
                isscatter = False
            elif o == "--tab-only":
                isfigure = False
                isrldistr = False
                isscatter = False
            elif o == "--sca-only":
                isfigure = False
                isrldistr = False
                istable = False
            elif o == "--noisy":
                isNoisy = True
            elif o == "--noise-free":
                isNoiseFree = True
            else:
                assert False, "unhandled option"

        from bbob_pproc import bbob2010 as inset # input settings
        # is here because variables setting could be modified by flags

        if (not verbose):
            warnings.simplefilter('ignore')

        print ("BBOB Post-processing: will generate comparison " +
               "data in folder %s" % outputdir)
        print "  this might take several minutes."

        dsList, sortedAlgs, dictAlg = processInputArgs(args, verbose=verbose)

        if not dsList:
            sys.exit()

        for i in dictAlg:
            if isNoisy and not isNoiseFree:
                dictAlg[i] = dictAlg[i].dictByNoise().get('nzall', DataSetList())
            if isNoiseFree and not isNoisy:
                dictAlg[i] = dictAlg[i].dictByNoise().get('noiselessall', DataSetList())

        for i in dsList:
            if not i.dim in (2, 3, 5, 10, 20):
                continue

            #### The following lines are BBOB 2009 checking.###################
            # Deterministic algorithms
            #if i.algId in ('Original DIRECT', ):
                #tmpInstancesOfInterest = instancesOfInterestDet
            #else:
                #tmpInstancesOfInterest = instancesOfInterest
            #if ((dict((j, i.itrials.count(j)) for j in set(i.itrials)) <
                #tmpInstancesOfInterest) and
                #(dict((j, i.itrials.count(j)) for j in set(i.itrials)) <
                #instancesOfInterest2010)):
                #warnings.warn('The data of %s do not list ' %(i) +
                              #'the correct instances ' +
                              #'of function F%d or the ' %(i.funcId) +
                              #'correct number of trials for each.')
            ###################################################################

            if (dict((j, i.itrials.count(j)) for j in set(i.itrials)) <
                inset.instancesOfInterest):
                warnings.warn('The data of %s do not list ' %(i) +
                              'the correct instances ' +
                              'of function F%d.' %(i.funcId))

        if len(sortedAlgs) < 2:
            raise Usage('Expect data from two different algorithms, could ' +
                        'only find one.')
        elif len(sortedAlgs) > 2:
            warnings.warn('Data from folders: %s ' % (sortedAlgs) +
                          'were found, the first two will be processed.')

        # Group by algorithm
        dsList0 = dictAlg[sortedAlgs[0]]
        if not dsList0:
            raise Usage('Could not find data for algorithm %s.' % (sortedAlgs[0]))

        dsList1 = dictAlg[sortedAlgs[1]]
        if not dsList1:
            raise Usage('Could not find data for algorithm %s.' % (sortedAlgs[0]))

        tmppath0, alg0name = os.path.split(sortedAlgs[0].rstrip(os.sep))
        tmppath1, alg1name = os.path.split(sortedAlgs[1].rstrip(os.sep))
        #Trick for having different algorithm names in the tables...
        #Does not really work.
        #while alg0name == alg1name:
        #    tmppath0, alg0name = os.path.split(tmppath0)
        #    tmppath1, alg1name = os.path.split(tmppath1)
        #
        #    if not tmppath0 and not tmppath1:
        #        break
        #    else:
        #        if not tmppath0:
        #            tmppath0 = alg0name
        #        if not tmppath1:
        #            tmppath1 = alg1name
        #assert alg0name != alg1name
        # should not be a problem, these are only used in the tables.
        for i in dsList0:
            i.algId = alg0name
        for i in dsList1:
            i.algId = alg1name

        if isfigure or isrldistr or istable or isscatter:
            if not os.path.exists(outputdir):
                os.mkdir(outputdir)
                if verbose:
                    print 'Folder %s was created.' % (outputdir)

        dictFN0 = dsList0.dictByNoise()
        dictFN1 = dsList1.dictByNoise()
        k0 = set(dictFN0.keys())
        k1 = set(dictFN1.keys())
        symdiff = k1 ^ k0
        if symdiff: # symmetric difference
            tmpdict = {}
            for i, noisegrp in enumerate(symdiff):
                if noisegrp == 'nzall':
                    tmp = 'noisy'
                elif noisegrp == 'noiselessall':
                    tmp = 'noiseless'

                if dictFN0.has_key(noisegrp):
                    tmp2 = sortedAlgs[0]
                elif dictFN1.has_key(noisegrp):
                    tmp2 = sortedAlgs[1]

                tmpdict.setdefault(tmp2, []).append(tmp)

            txt = []
            for i, j in tmpdict.iteritems():
                txt.append('Only input folder %s lists %s data.'
                            % (i, ' and '.join(j)))
            raise Usage('Data Mismatch: \n  ' + ' '.join(txt)
                        + '\nTry using --noise-free or --noisy flags.')

        if isfigure:
            ppfig2.main2(dsList0, dsList1, 1e-8, outputdir, verbose)
            print "log ERT1/ERT0 vs target function values done."

        if isrldistr:
            if len(dictFN0) > 1 or len(dictFN1) > 1:
                warnings.warn('Data for functions from both the noisy and ' +
                              'non-noisy testbeds have been found. Their ' +
                              'results will be mixed in the "all functions" ' +
                              'ECDF figures.')

            dictDim0 = dsList0.dictByDim()
            dictDim1 = dsList1.dictByDim()

            for dim in set(dictDim0.keys()) | set(dictDim1.keys()):
                if dim in inset.rldDimsOfInterest:
                    try:
                        pprldistr2.main2(dictDim0[dim], dictDim1[dim],
                                         inset.rldValsOfInterest,
                                         outputdir, 'dim%02dall' % dim, verbose)
                    except KeyError:
                        warnings.warn('Could not find some data in %d-D.'
                                      % (dim))
                        continue

                    dictFG0 = dictDim0[dim].dictByFuncGroup()
                    dictFG1 = dictDim1[dim].dictByFuncGroup()

                    for fGroup in set(dictFG0.keys()) | set(dictFG1.keys()):
                        pprldistr2.main2(dictFG0[fGroup], dictFG1[fGroup],
                                         inset.rldValsOfInterest,
                                         outputdir, 'dim%02d%s' % (dim, fGroup),
                                         verbose)

                    dictFN0 = dictDim0[dim].dictByNoise()
                    dictFN1 = dictDim1[dim].dictByNoise()

                    for fGroup in set(dictFN0.keys()) | set(dictFN1.keys()):
                        pprldistr2.main2(dictFN0[fGroup], dictFN1[fGroup],
                                         inset.rldValsOfInterest, outputdir,
                                         'dim%02d%s' % (dim, fGroup),
                                         verbose)
            print "ECDF absolute target graphs done."

            for dim in set(dictDim0.keys()) | set(dictDim1.keys()):
                pprldistr.fmax = None #Resetting the max final value
                pprldistr.evalfmax = None #Resetting the max #fevalsfactor
                if dim in inset.rldDimsOfInterest:
                    try:
                        pprldistr.comp(dictDim0[dim], dictDim1[dim],
                                       inset.rldValsOfInterest, True,
                                       outputdir, 'dim%02dall' % dim, verbose)
                    except KeyError:
                        warnings.warn('Could not find some data in %d-D.'
                                      % (dim))
                        continue

                    dictFG0 = dictDim0[dim].dictByFuncGroup()
                    dictFG1 = dictDim1[dim].dictByFuncGroup()

                    for fGroup in set(dictFG0.keys()) | set(dictFG1.keys()):
                        pprldistr.comp(dictFG0[fGroup], dictFG1[fGroup],
                                       inset.rldValsOfInterest, True, outputdir,
                                       'dim%02d%s' % (dim, fGroup), verbose)

                    dictFN0 = dictDim0[dim].dictByNoise()
                    dictFN1 = dictDim1[dim].dictByNoise()
                    for fGroup in set(dictFN0.keys()) | set(dictFN1.keys()):
                        pprldistr.comp(dictFN0[fGroup], dictFN1[fGroup],
                                       inset.rldValsOfInterest, True, outputdir,
                                       'dim%02d%s' % (dim, fGroup), verbose)

            print "ECDF dashed-solid graphs done."

        if istable:
            dictNG0 = dsList0.dictByNoise()
            dictNG1 = dsList1.dictByNoise()

            for nGroup in set(dictNG0.keys()) & set(dictNG1.keys()):
                pptable2.main2(dictNG0[nGroup], dictFN1[nGroup],
                               inset.tabDimsOfInterest, outputdir,
                               '%s' % (nGroup), verbose)

        if isscatter:
            ppscatter.main(dsList0, dsList1, outputdir, verbose=verbose)
            print "Scatter plots done."

        if isfigure or isrldistr or istable or isscatter:
            print "Output data written to folder %s." % outputdir

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use -h or --help"
        return 2

if __name__ == "__main__":
   sys.exit(main())
