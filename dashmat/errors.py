from input_algorithms.errors import BadSpec, BadSpecValue
from delfick_error import DelfickError, ProgrammerError

class DashMatError(DelfickError): pass

# Explicitly make these errors in this context
BadSpec = BadSpec
BadSpecValue = BadSpecValue
ProgrammerError = ProgrammerError

class BadConfiguration(DashMatError):
    desc = "Bad configuration"

class BadOptionFormat(DashMatError):
    desc = "Bad option format"

class BadOption(DashMatError):
    desc = "Bad Option"

class BadYaml(DashMatError):
    desc = "Invalid yaml file"

class UserQuit(DashMatError):
    desc = "User quit the program"

class BadTask(DashMatError):
    desc = "Bad task"

class BadTemplate(DashMatError):
    desc = "Bad template"

class BadImport(DashMatError):
    desc = "Failed to import"

class MissingModule(DashMatError):
    desc = "No such module"

class MissingServerOption(DashMatError):
    desc = "Missing server option"

class UnknownModule(DashMatError):
    desc = "Unknown module"

