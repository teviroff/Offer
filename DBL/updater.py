from DBL.config import *
import DBL.json_worker as json_worker
from DBL.parsers.run import parse_all
import DBL.renderer as renderer


def get_opportunities_list():
    names = parse_all()
    opportunities = []
    for json_fname in names:
        opportunities += json_worker.parse_opportunity_json(json_fname)
    return opportunities


def update():
    opportunities = get_opportunities_list()
    renderer.save_md(opportunities[0], 'DBL/rendered/example.md')
    # TODO: API DB
    # TODO: MD - how to save
