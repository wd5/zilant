# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.core.mail import send_mail
from django.core.paginator import QuerySetPaginator

def render_to_response(request, template_name, context_dict=None):
    from django.shortcuts import render_to_response as _render_to_response
    context = RequestContext(request, context_dict or {})
    return _render_to_response(template_name, context_instance=context)


def validate_page_number(page, total):
    if page:
        try:
            page = int(page)
            if 1 <= page <= total:
                return page
        except ValueError:
            pass
    return 1


def make_pages(querySet, items_at_page=20, current_page=None):
    pages = QuerySetPaginator(querySet, items_at_page)

    page_number = validate_page_number(current_page, pages.num_pages)
    posts = pages.page(page_number).object_list
    context = {'items': posts}

    context.update(other_pages(page_number, pages.num_pages))
    return context


def other_pages(page, total):
    return {
        'pages': range(1, total + 1),
        'showed_pages': [p for p in range(1, total + 1) if abs(p - page) <= 4],
        'page_number': page,
        'first_page': page != 1 and 1 or None,
        'prev_page': page != 1 and page - 1 or None,
        'next_page': page != total and page + 1 or None,
        'last_page': page != total and total or None,
        'show_pagination': total > 1,
        }
