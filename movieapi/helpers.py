import json
from datetime import date

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.forms.models import model_to_dict


def all_json_response(model_cls):
    """
    Takes a Model's all values, serializes it, and returns a Json Response
    :param model_cls: A model from models.py
    :return: Json Response
    """

    # Get all values from model
    all_values = model_cls.objects.values()

    # serialize to json
    all_json = json.dumps(list(all_values), cls=DjangoJSONEncoder)

    # return as Json Response
    return HttpResponse(all_json, content_type='application/json')


def qs_json_response(qs):
    """
    Takes a value queryset, serializes it, and returns a Json Response
    :param qs: A value queryset
    :return: Json Response
    """

    qs_json = json.dumps(list(qs), cls=DjangoJSONEncoder)

    # return as Json Response
    return HttpResponse(qs_json, content_type='application/json')


def model_to_json(model):
    def date_to_str(o):
        if isinstance(o, date):
            return o.__str__()

    model = model_to_dict(model)
    return json.dumps(model, default=date_to_str)
