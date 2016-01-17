"""
Use Docker to create an instance of node that will transform jsx into javascript.
"""

from harpoon.option_spec.harpoon_specs import HarpoonSpec
from harpoon.option_spec.image_objs import Mount
from harpoon.executor import docker_context
from harpoon.ship.builder import Builder
from harpoon.ship.runner import Runner

from option_merge.converter import Converter
from option_merge import MergedOptions

from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta

from textwrap import dedent
import pkg_resources
import collections
import json
import sys

mtime = 1450492585

class ReactServer(object):

    def default_npm_deps(self):
        return {
              "babel-core": "^6.3.17"
            , "babel-loader": "^6.2.0"
            , "babel-polyfill": "^6.3.14"
            , "babel-preset-react": "^6.3.13"
            , "babel-preset-es2015": "^6.3.13"
            , "babel-plugin-transform-object-rest-spread": "^6.3.13"

            , "css-loader": "^0.23.0"
            , "style-loader": "^0.13.0"
            , "imports-loader": "^0.6.5"
            , "exports-loader": "^0.6.2"

            , "react": "^0.14.3"
            , "react-dom": "^0.14.3"

            , "webpack": "^1.12.9"
            , "whatwg-fetch": "^0.10.1"
            }

    def prepare(self, npm_deps, compiled_static_folder):
        ctxt = docker_context()
        harpoon_options = {
              "docker_context": ctxt
            , "no_intervention": True
            , "docker_context_maker": docker_context
            }
        self.harpoon = HarpoonSpec().harpoon_spec.normalise(Meta({}, []), harpoon_options)

        config_root = pkg_resources.resource_filename(__package__, "")

        deps = self.default_npm_deps()
        deps.update(npm_deps)

        image_name = "python-dashing-jsx-builder"
        everything = MergedOptions(dont_prefix=[dictobj])
        everything.update(
            { "harpoon": self.harpoon
            , "config_root": config_root
            , "images":
              { image_name:
                { "harpoon": self.harpoon
                , "configuration": everything
                , "volumes":
                  { "mount":
                    [ [ compiled_static_folder, "/compiled" ]
                    ]
                  }
                , "context":
                  { "enabled" : False
                  }
                , "persistence":
                  { "action": "npm install && npm dedup"
                  , "folders": ["/project/node_modules", "/usr/lib/node_modules"]
                  }
                , "commands":
                  [ "FROM gliderlabs/alpine:3.2"

                  , "RUN apk-install bash nodejs"
                  , "RUN npm install -g npm"

                  , "RUN mkdir /project"
                  , "WORKDIR /project"
                  , [ "ADD"
                    , { "dest": "/project/package.json"
                      , "content": json.dumps(
                          { "name": "python-dashing"
                          , "version": "0.1.0"
                          , "dependencies": collections.OrderedDict(sorted(deps.items()))
                          }
                        , sort_keys=True
                        )
                      , "mtime": mtime
                      }
                    ]
                  ]
                }
              }
            }
          )

        def convert_image(path, val):
            meta = Meta(everything, [(part, "") for part in path.path])
            return HarpoonSpec().image_spec.normalise(meta, val)
        everything.add_converter(Converter(convert=convert_image, convert_path=["images", image_name]))
        everything.converters.activate()

        self.image = everything[["images", image_name]]
        Builder().make_image(self.image, {self.image.name: self.image})

    def build_webpack(self, input_dir):
        command = "cd /modules && ln -s /project/node_modules . && /project/node_modules/.bin/webpack"
        image = self.image.clone()

        image.bash = command

        image.volumes = image.volumes.clone()
        image.volumes.mount = list(image.volumes.mount)
        image.volumes.mount.append(Mount(input_dir, "/modules", "rw"))

        Runner().run_container(image, {image.name: image})

