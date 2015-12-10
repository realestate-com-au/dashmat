from input_algorithms.errors import BadSpec, BadSpecValue
from delfick_error import DelfickError, ProgrammerError

class PythonDashingError(DelfickError): pass

# Explicitly make these errors in this context
BadSpec = BadSpec
BadSpecValue = BadSpecValue
ProgrammerError = ProgrammerError

class BadConfiguration(PythonDashingError):
    desc = "Bad configuration"

class BadOptionFormat(PythonDashingError):
    desc = "Bad option format"

class BadOption(PythonDashingError):
    desc = "Bad Option"

class BadYaml(PythonDashingError):
    desc = "Invalid yaml file"

class UserQuit(PythonDashingError):
    desc = "User quit the program"

class BadTask(PythonDashingError):
    desc = "Bad task"

class BadTemplate(PythonDashingError):
    desc = "Bad template"

class BadImport(PythonDashingError):
    desc = "Failed to import"

class MissingModule(PythonDashingError):
    desc = "No such module"

class MissingServerOption(PythonDashingError):
    desc = "Missing server option"
