# importing the necessary libraries
# import os
# from io import BytesIO

import pdfkit
from django.conf import settings
# from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa

# defining the function to convert an HTML file to a PDF file
# https://qna.habr.com/q/536178?
# def fetch_pdf_resources(uri, rel):
#     """
#     Convert HTML URIs to absolute system paths so xhtml2pdf can access those
#     resources
#     """
#     uri_for_finder = uri
#     if uri_for_finder[0] == "/":
#         uri_for_finder = uri_for_finder[1:]
#     result = finders.find(uri_for_finder)
#     if result:
#             if not isinstance(result, (list, tuple)):
#                     result = [result]
#             result = list(os.path.realpath(path) for path in result)
#             path=result[0]
#     else:
#             sUrl = settings.STATIC_URL        # Typically /static/
#             sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
#             mUrl = settings.MEDIA_URL         # Typically /media/
#             mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

#             if uri.startswith(mUrl):
#                     path = os.path.join(mRoot, uri.replace(mUrl, ""))
#             elif uri.startswith(sUrl):
#                     path = os.path.join(sRoot, uri.replace(sUrl, ""))
#             else:
#                     return uri

#     # make sure that file exists
#     if not os.path.isfile(path):
#             raise Exception(
#                     'media URI must start with %s or %s' % (sUrl, mUrl)
#             )
#     return path    
    # return os.path.join(str(settings.BASE_DIR), settings.STATIC_ROOT,uri)
    # if uri.startswith("https"):
    #     return uri
    # else:
        # return os.path.join(str(settings.BASE_DIR), "main/static",uri)
    # if uri == "/main/arial.ttf":
    #     return "/run/media/dav/share_win_linux/Pythow_Work_Dir/LearnProject/Django/MyTimer/my_timer_project/main/static/main/arial.ttf"
    # if uri.find(settings.MEDIA_URL) != -1:
    #     path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    # elif uri.find(settings.STATIC_URL) != -1:
    #     path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    # else:
    #     path = None
    # return path
    
# def html_to_pdf(template_src, context_dict = None):
#     if context_dict is None:
#         context_dict = {}
#     template = get_template(template_src)
#     html  = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8', link_callback=fetch_pdf_resources)
#     # pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-16")), result, encoding='UTF-16')
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None

def html_to_pdf(template_src, context_dict = None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html_content  = template.render(context_dict)
    # config = pdfkit.configuration(wkhtmltopdf=settings.PDF_WKHTMLTOPDF)
    pdf = pdfkit.PDFKit(html_content, "string").to_pdf()
    return HttpResponse(pdf, content_type='application/pdf')  # Generates the response as pdf response.    
    # pdfkit.from_string(html, 'out.pdf')
    # with open("out.pdf", 'rb') as pdf:
    #     response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
    # os.remove("out.pdf")  # remove the locally created pdf file.
    # return response

