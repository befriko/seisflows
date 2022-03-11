#!/usr/bin/env python
"""
This is the custom class for an NLCG optimization schema.
It supercedes the `seisflows.optimize.base` class
"""
import sys
import logging

from seisflows3.config import custom_import, SeisFlowsPathsParameters
from seisflows3.plugins import optimize

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class NLCG(custom_import("optimize", "base")):
    """
    Nonlinear conjugate gradient method
    """
    # Class-specific logger accessed using self.logger                           
    logger = logging.getLogger(__name__).getChild(__qualname__)       

    def __init__(self):
        """
        These parameters should not be set by the user.
        Attributes are initialized as NoneTypes for clarity and docstrings.

        :type NLCG: Class
        :param NLCG: plugin NLCG class that controls the machinery of the
            NLCG optimization schema
        """
        super().__init__()
        self.NLCG = None

    @property
    def required(self):
        """
        A hard definition of paths and parameters required by this class,
        alongside their necessity for the class and their string explanations.
        """
        sf = SeisFlowsPathsParameters(super().required)

        # Define the Parameters required by this module
        sf.par("NLCGMAX", required=False, default="null", par_type=float,
               docstr="NLCG periodic restart interval, between 1 and inf")

        sf.par("NLCGTHRESH", required=False, default="null", par_type=float,
               docstr="NLCG conjugacy restart threshold, between 1 and inf")

        return sf

    def check(self, validate=True):
        """
        Checks parameters, paths, and dependencies
        """
        if validate:
            self.required.validate()
        super().check(validate=False)

        assert(PAR.LINESEARCH.upper() == "BRACKET"), \
            f"NLCG requires a bracketing line search algorithm"

    def setup(self):
        """
        Set up the NLCG optimization schema
        """
        super().setup()
        self.NLCG = getattr(optimize, 'NLCG')(path=PATH.OPTIMIZE,
                                              maxiter=PAR.NLCGMAX,
                                              thresh=PAR.NLCGTHRESH,
                                              precond=self.precond,
                                              verbose=PAR.VERBOSE)

    def compute_direction(self):
        """
        Overwrite the Base compute direction class
        """
        # g_new = self.load('g_new')
        p_new, self.restarted = self.NLCG()
        self.save(self.p_new, p_new)

    def restart(self):
        """
        Overwrite the Base restart class and include a restart of the NLCG
        """
        super().restart()
        self.NLCG.restart()



