# encoding: utf-8
# Project auto-generated at: ...
# Copyright (C) 2012 Mustachioed Maven.

import os

import pystache

def run(sys_argv):
    """
    Print a greeting to stdout.

    """
    user_input = sys_argv[1]

    template_dir = os.path.join(os.path.dirname(__file__), os.pardir, 'templates')
    template_path = os.path.join(template_dir, 'hello.mustache')

    renderer = pystache.Renderer(search_dirs=[template_dir])
    renderered = renderer.render_path(template_path, {'to': user_input})

    print(renderered)
