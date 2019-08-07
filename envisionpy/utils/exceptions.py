
def format_error(error):
# Return a list with error type and message.
    return [type(error).__name__, str(error)]

class EnvisionError(Exception):
    pass
class HandlerNotFoundError(EnvisionError):
    ''' Error used for non-critical unhandled requests.
        User does not know when raised.'''
    pass

class InvalidRequestError(EnvisionError):
    ''' Error used for invalid requests, such as invalid parameters.
        Should generate an alert so user knows something did not work. 
    '''
    pass

class ProcessorNotFoundError(EnvisionError):
    pass

class BadHDF5Error(EnvisionError):
    pass

# TODO: Custom parse errors