import json
from django.test.client import encode_multipart
from django.utils import six
from rest_framework import VERSION, exceptions, serializers, status
from rest_framework.compat import (
    INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS, coreapi,
    template_render
)
from rest_framework.exceptions import ParseError
from rest_framework.request import is_form_media_type, override_method
from rest_framework.settings import api_settings
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from collections import ChainMap, defaultdict


class APIRenderer(JSONRenderer):

    app_version = settings.APP_VERSION

    ALLOWED_METHODS = ('GET', 'POST', 'PUT', 'DELETE',)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return bytes()
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS
        response_code = renderer_context["response"].status_code
        cleaned_data = {
            "status": response_code,

        }
        if renderer_context["request"].method in self.ALLOWED_METHODS:
            if response_code >= 200 and response_code < 300:
                cleaned_data["data"] = data
                cleaned_data["errors"] = None
                cleaned_data["meta"] = {
                    "app_version": self.app_version,
                }
            else:
                # arr = [{"%s" % k: "%s" % data[k][0]} if isinstance(
                # data[k], list) else {"%s" % k: "%s" % data[k]} for k, v in
                # data.items()]
                a = defaultdict(dict)
                for k, v in data.items():
                    if isinstance(v, dict):
                        d = defaultdict(dict)
                        for key, items in v.items():
                            d[key] = items[0]
                        a[k] = d
                    elif isinstance(v, list):
                        a[k] = v[0]
                    else:
                        a[k] = v
                cleaned_data["errors"] = dict(a)
                cleaned_data["data"] = None
        else:
            cleaned_data["data"] = data

        ret = json.dumps(
            cleaned_data, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            separators=separators
        )
        # On python 2.x json.dumps() returns bytestrings if ensure_ascii=True,
        # but if ensure_ascii=False, the return type is underspecified,
        # and may (or may not) be unicode.
        # On python 3.x json.dumps() returns unicode strings.
        if isinstance(ret, six.text_type):
            # We always fully escape \u2028 and \u2029 to ensure we output JSON
            # that is a strict javascript subset. If bytes were returned
            # by json.dumps() then we don't have these characters in any case.
            # See: http://timelessrepo.com/json-isnt-a-javascript-subset
            ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
            return bytes(ret.encode('utf-8'))
        return ret


class SessionAPIRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return bytes()
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS
        response_code = renderer_context["response"].status_code
        cleaned_data = {
            "status": response_code,
        }
        if response_code >= 200 and response_code < 300:
            cleaned_data["data"] = data
            cleaned_data["errors"] = None
        else:
            cleaned_data["errors"] = data
            cleaned_data["data"] = None
        ret = json.dumps(
            cleaned_data, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            separators=separators
        )
        # On python 2.x json.dumps() returns bytestrings if ensure_ascii=True,
        # but if ensure_ascii=False, the return type is underspecified,
        # and may (or may not) be unicode.
        # On python 3.x json.dumps() returns unicode strings.
        if isinstance(ret, six.text_type):
            # We always fully escape \u2028 and \u2029 to ensure we output JSON
            # that is a strict javascript subset. If bytes were returned
            # by json.dumps() then we don't have these characters in any case.
            # See: http://timelessrepo.com/json-isnt-a-javascript-subset
            ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
            return bytes(ret.encode('utf-8'))
        return ret
