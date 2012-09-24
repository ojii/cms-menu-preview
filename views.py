import hashlib
import urllib
from classytags.utils import TemplateConstant
from cms.api import create_page
from cms.models import Page
from cms.test_utils.util.context_managers import SettingsOverride
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.management import call_command
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.test import RequestFactory
from django.views.generic import TemplateView
from menus.templatetags.menu_tags import ShowMenu



class DummyTokens(list):
    def __init__(self, *tokens):
        super(DummyTokens, self).__init__(['show_menu'] + list(tokens))

    def split_contents(self):
        return self


class DummyParser(object):
    def compile_filter(self, token):
        return TemplateConstant(token)
dummy_parser = DummyParser()


class RenderForm(forms.Form):
    tree = forms.CharField()
    from_level = forms.CharField()
    to_level = forms.CharField()
    extra_active = forms.CharField()
    extra_inactive = forms.CharField()


def calculate_hash(data):
    key = urllib.urlencode(sorted(data.items()))
    return hashlib.md5(key).hexdigest()


def flatten(nodes):
    flat = []
    for node in nodes:
        flat.append({
            'name': node.title,
            'children': flatten(node.children)
        })
    return flat

def nice_name(name):
    return name.strip()[1:].rstrip('*').strip()

def get_indent(line):
    indent = 0
    for char in line:
        if char == '-':
            return indent
        elif char == ' ':
            indent += 1
        elif char == '\t':
            indent += 4
        else:
            raise Exception("Invalid line %r" % line)
    raise Exception("Invalid line %r" % line)

def parse(data):
    lines = [line for line in data.splitlines() if line.strip()]
    indented = []
    parent_stack = [-1]
    current_indent = 0
    for id, line in enumerate(lines):
        indent = get_indent(line)
        if indent == current_indent:
            parent = parent_stack[-1]
        elif indent > current_indent:
            parent_stack.append(indented[-1][0])
            parent = parent_stack[-1]
        elif indent < current_indent:
            del parent_stack[-1]
            parent = parent_stack[-1]
        current_indent = indent
        indented.append((id, line, parent))
    tree = {-1: {
        'children': [],
        'name': 'root',
        'url': '/'
    }
    }
    selected = None
    for id, raw, parent in indented:
        name = nice_name(raw)
        page = {
            'children': [],
            'name': name,
            'url': tree[parent]['url'] + slugify(name) + '/' if id != 0 else '/'
        }
        tree[parent]['children'].append(page)
        tree[id] = page
        if raw.endswith('*'):
            selected = id
    if selected is None:
        raise Exception("No page selected!")
    return tree[-1]['children'], tree[selected]['url']

def _load(site, tree, parent=None):
    for data in tree:
        page = create_page(data['name'], 'dummy.html', 'en', slug=slugify(data['name']), published=True, in_navigation=True, parent=parent, site=site)
        _load(site, data['children'], parent=Page.objects.get(pk=page.pk))

def load_tree(site, data, parent=None):
    tree, selected = parse(data)
    _load(site, tree, parent)
    return selected


def build(tree, from_level, to_level, extra_active, extra_inactive):
    call_command('syncdb', interactive=False)
    site = Site.objects.create(domain='dummy', name='dummy')
    current = load_tree(site, tree)
    request = RequestFactory().get(current)
    request.user = AnonymousUser()
    tokens = DummyTokens(from_level, to_level, extra_inactive, extra_active)
    context = RequestContext(request)
    with SettingsOverride(SITE_ID=site.pk):
        Site.objects.clear_cache()
        ShowMenu(dummy_parser, tokens).render(context)
    nodes = context['children']
    flat = flatten(nodes)
    def _rec(nodes, level=0):
        lines = []
        indent = '    ' *  level
        for node in nodes:
            lines.append('%s- %s' % (indent, node['name']))
            lines.extend(_rec(node['children'], level+1))
        return lines
    return '\n'.join(_rec(flat))


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, *args, **kwargs):
        return self.render_to_response({'tree': '''- home
    - subpage
    - other sub page
- top level page
- other top level page *'''})

    def post(self, *args, **kwargs):
        form = RenderForm(self.request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors.as_text())
        data = form.cleaned_data
        cache_key = calculate_hash(data)
        output = cache.get(cache_key, None)
        if not output:
            output = build(**data)
            cache.set(cache_key, output)
        data['output'] = output
        return self.render_to_response(data)

