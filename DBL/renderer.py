from jinja2 import Template
import codecs


TEMPLATES_PATH = 'DBL/templates/'
CARD_TEMPLATE_FNAME = 'card.md'


def render_card(opportunity_info):
    with open(f'{TEMPLATES_PATH}{CARD_TEMPLATE_FNAME}', 'r') as file:
        template = Template(file.read(), trim_blocks=True)
    return template.render(opp=opportunity_info)


def save_md(opportunity_info, output_fname):
    rendered_file = render_card(opportunity_info)
    output_file = codecs.open(output_fname, 'w', 'utf-8')
    output_file.write(rendered_file)
    output_file.close()
