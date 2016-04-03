from dashmat.core_modules.base import Module

class Status(Module):

    @classmethod
    def npm_deps(self):
        return {
              "moment": "^2.11.2"
            }
