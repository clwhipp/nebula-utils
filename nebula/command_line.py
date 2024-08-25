import click

from nebula.app.issue import issue
# from nebula.app.policy import policy

@click.group()
def entry_point():
    pass

entry_point.add_command(issue)
# entry_point.add_command(policy)

def main():
    entry_point()
