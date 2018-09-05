class RequestDataException(Exception):
    
    def __init__(self, message):
        super(RequestDataException, self).__init__(message)
