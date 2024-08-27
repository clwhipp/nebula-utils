import click

from nebula.app.issue import issue
from nebula.app.config import firewall

@click.group()
def entry_point():
    pass

entry_point.add_command(issue)
entry_point.add_command(firewall)

def main():
    entry_point()
