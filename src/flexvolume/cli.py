from __future__ import print_function

import sys
import json
import click

GENERIC_SUCCESS = {"status": "Success"}
GENERIC_FAILURE = {"status": "Failure"}

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS,
             invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.secho(ctx.get_help())

def error(msg):
    print(json.dumps(msg), file=sys.stderr)
    sys.exit(1)

def info(msg):
    print(json.dumps(msg), file=sys.stdout)
    sys.exit(0)

