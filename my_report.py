from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus import Image
import datetime

def create_pdf():
    my_doc = SimpleDocTemplate('myfile.pdf')
    flowables = []

    # f = open('area.jpg', 'rb')
    # im = Image(f)
    sample_style_sheet = getSampleStyleSheet()
    paragraph_1 = Paragraph('16472.88', sample_style_sheet['Heading1'])
    paragraph_2 = Paragraph('California', sample_style_sheet['BodyText'])
    paragraph_3 = Paragraph('Beef 228.7 Dairy 929.95', sample_style_sheet['BodyText'])
    paragraph_4 = Paragraph('Fruits 8736.4 Veggies 21434', sample_style_sheet['BodyText'])
    paragraph_5 = Paragraph('Wheel 249.3 Corn 34.6', sample_style_sheet['BodyText'])
    flowables.append(paragraph_1)
    flowables.append(paragraph_2)
    flowables.append(paragraph_3)
    flowables.append(paragraph_4)
    flowables.append(paragraph_5)
    # flowables.append(im)

    custom_body_style = sample_style_sheet['BodyText']
    custom_body_style.fontSize = 10
    paragraph = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    paragraph = 'Otchet sozdan byl v ' + paragraph
    paragraph_6 = Paragraph(paragraph, custom_body_style)
    flowables.append(paragraph_6)

    my_doc.build(flowables)
