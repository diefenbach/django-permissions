# django imports
from django import template
from django.template import Variable

import permissions.utils
register = template.Library()


class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission
    for passed object.
    """
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 3:
            raise template.TemplateSyntaxError(
                "'%s' tag takes two arguments" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(bits[1], bits[2], nodelist_true, nodelist_false)

    def __init__(self, obj, codename, nodelist_true, nodelist_false):
        self.obj = Variable(obj)
        self.codename = codename
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        obj = self.obj.resolve(context)
        request = context.get("request")
        if permissions.utils.has_permission(obj, request.user, self.codename):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false

@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNode.handle_token(parser, token)
