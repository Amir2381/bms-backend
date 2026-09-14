class ImportError(Exception):
    """Base exception for data import errors."""


class UnsupportedFileTypeError(ImportError):
    """Raised when the uploaded file type is not supported."""


class FileTooLargeError(ImportError):
    """Raised when the uploaded file exceeds the maximum allowed size."""


class EmptyFileError(ImportError):
    """Raised when the uploaded file is empty."""


class InvalidImportRowError(ImportError):
    """Raised when an imported row contains invalid data."""


class MissingRequiredColumnError(ImportError):
    """Raised when a required column is missing."""


class InvalidImportValueError(ImportError):
    """Raised when an imported value cannot be converted."""


class ImportedProductNotFoundError(ImportError):
    """Raised when an imported product cannot be found."""


class ImportedSellerNotFoundError(ImportError):
    """Raised when an imported seller cannot be found."""
