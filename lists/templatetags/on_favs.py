from django import template
from lists import models as list_models

register = template.Library()


@register.simple_tag(takes_context=True)
def on_favs(context, room):
    user = context.request.user
    if not user.is_anonymous:
        _list = list_models.List.objects.get_or_none(
            user=user, name="My Favourites Room"
        )
        if _list:
            return room in _list.rooms.all()
        return False
