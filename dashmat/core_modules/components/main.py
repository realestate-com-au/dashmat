from dashmat.core_modules.base import Module

class Components(Module):

    @classmethod
    def npm_deps(self):
        return {
              "chart.js": "^1.0.2"
            , "react-chartjs": "^0.6.0"
            }
