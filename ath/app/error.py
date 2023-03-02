class ServiceError(Exception):
    ...


class ParsingCsvError(ServiceError):
    ...


class BadSampleError(ServiceError):
    ...
