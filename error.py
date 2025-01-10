# -*- coding: utf-8 -*-

class BastionError(Exception):
    'base class of bastion exception'

class TaskTypeNotFoundError(Exception):
    'no task type found'

class FsxInvalidError(BastionError):
    'error in handling fsx file system'

class FsxNotFoundError(BastionError):
    'error if fsx file system not found'

class FsxNoQueryResultError(BastionError):
    'no element found in Fsxref db'

class FsxExistsError(BastionError):
    'fsx filesystem already exists'

class FsxExportingFailedError(BastionError):
    'fsx filesystem exporting  failed'
