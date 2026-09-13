class ImportError(Exception):
    """Base exception for data import errors."""


class UnsupportedFileTypeError(ImportError):
    """Raised when the uploaded file type is not supported."""


class FileTooLargeError(ImportError):
    """Raised when the uploaded file exceeds the maximum allowed size."""


class EmptyFileError(ImportError):
    """Raised when the uploaded file is empty."""
