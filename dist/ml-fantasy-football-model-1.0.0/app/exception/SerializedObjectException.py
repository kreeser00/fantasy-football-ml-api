class SerializedObjectException(Exception):
    
    def __init__(self, message):
        super(SerializedObjectException, self).__init__(message)
