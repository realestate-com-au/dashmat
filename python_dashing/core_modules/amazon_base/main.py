from python_dashing.core_modules.base import Module

from input_algorithms.errors import BadSpecValue
from input_algorithms import spec_base as sb
import logging
import base64

class kms_secret_spec(sb.Spec):
    def normalise(self, meta, val):
        val = sb.dictionary_spec().normalise(meta, val)
        if "plain" in val:
            return val["plain"]
        elif "kms" in val:
            val = sb.set_options(
                  kms = sb.required(sb.string_spec())
                , location = sb.required(sb.string_spec())
                ).normalise(meta, val)
            return lambda: __import__("boto3").client("kms", val['location']).decrypt(CiphertextBlob=base64.b64decode(val['kms']))['Plaintext'].decode('utf-8')

class AmazonBase(Module):
    relative_to = "python_dashing.core_modules.amazon_base"

    @classmethod
    def requirements(kls):
        return ["boto3"]

    @classmethod
    def register_configuration(kls):
        return {(0, "kms_secrets"): sb.dictof(sb.string_spec(), kms_secret_spec())}

