from functools import partial
from functools import update_wrapper

__author__ = "Christopher Henderson"
__copyright__ = "Copyright 2015, Christopher Henderson"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Christopher Henderson"
__email__ = "chris@chenderson.org"


class Decorator(object):

    '''
    Defines an interface for class based decorators.

    PURPOSE:

    The normal protocol of a decorator dictates that an __init__
    and a __call__ should be defined. If __init__ accepts only one
    argument, then it will be given the function to be decorated and can be
    used without parenthesis. E.G.:

        @my_decorator
        def some_func():
            pass

    If __init__ takes in arguments related to the decorator itself, then
    __call__ must accept the decorated function and return the desired wrapper.
    The result being that a decorator that takens in optional arguments can
    end up looking like this:

        @my_decorator(verbose=True)
        def some_func():
            pass

        @my_decorator()
        def some_other_func():
            pass

    This is cumbersome and leads to confusion on whether or not a particuler
    no-argument decorator requires parenthesis or not.

    In addition, many programmers newer to Python are at a loss on how to pass
    self to a decorated instance method.

    As such, the purpose of the Decorator class is to abstract away the
    nuances of function wrapping, __call__ behavior, and non-data descriptors.

    PROTOCAL:

    When inheriting from this class the typical protocol for writing a
    decorator class changes slightly.

    __decorator__:
        Must be overriden.
        This is where the decorating behavior should be written, as opposed
        to __call__.

    __wrap__:
        Optionally overriden.
        Defines how this class wraps a target function.

    The wrapped function can be found at self.function.

    SIMPLE EXAMPLE:

    ############################################################################
    class Logged(Decorator):

        def __decorator__(self, *args, **kwargs):
            print ("Now calling {FUNC}".format(FUNC=self.function.__name__))
            function_result = self.function(*args, **kwargs)
            print ("Finished {FUNC}".format(FUNC=self.function.__name__))
            return function_result

    @Logged
    def add(a, b):
        return a + b

    result = add(1, 2)
    print (result)
    ############################################################################

    OUTPUTS:
        Now calling add
        Finished add
        3

    COMPLEX EXAMPLE:

    ############################################################################
    class Logged(Decorator):

        def __init__(self, function=None, verbose=False):
            self.verbose = verbose
            super(Logged, self).__init__(function)

        def __decorator__(self, *args, **kwargs):
            if self.verbose:
                print ("Now calling {FUNC}".format(
                    FUNC=self.function.__name__)
                )
            function_result = self.function(*args, **kwargs)
            if self.verbose:
                print ("Finished {FUNC}".format(
                    FUNC=self.function.__name__)
                )
            return function_result

    class Math(object):

        @staticmethod
        @Logged
        def add(a, b):
            return a + b

        @staticmethod
        @Logged(verbose=True)
        def subract(a, b):
            return a - b

    print (Math.add(1, 2))
    print (Math.subract(2, 1))
    ############################################################################

    OUTPUTS:
        3
        Now calling subract
        Finished subract
        1
    '''

    def __init__(self, function=None):
        '''
        If function is left undefined, then function wrapping is deferred
        until the first time __call__ is executed.
        '''
        self.function = function
        if function:
            self.__wrap__(function)

    def __decorator__(self, *args, **kwargs):
        '''
        __decorator__ must be defined by the inheriting classes as a surrogate
        to __call__. That is, behavior that you would be typically placed under
        __call__ should be placed under __decorator__ instead.
        '''
        raise NotImplementedError("Call behavior is not defined in this abstract class")

    def __wrap__(self, function):
        '''
        Called at the time when the decorating class is
        given its function to wrap.
        '''
        self.function = function
        update_wrapper(self, function)
        return self

    def __call__(self, *args, **kwargs):
        '''
        Depending on how this decorator was defined, __call__ will either
        execute the target function or it will wrap the target function.

        If a function was received during instantation then __decorator__ will
        be called immediately as we have already succesfully wrapped the
        target function.

        Otherwise this decorator was given keyword arguments,
        which means function wrapping was deferred until now.
        '''
        if self.function:
            return self.__decorator__(*args, **kwargs)
        return self.__wrap__(args[0])

    def __get__(self, instance, klass=None):
        '''
        Non-data descriptor for inserting an instance as the first parameter
        to __call__ if this object is being accessed as a member.
        '''
        if instance is None:
            return self
        return partial(self, instance)
