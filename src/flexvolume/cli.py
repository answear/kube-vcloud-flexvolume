#!/usr/bin/env python

import sys
import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS,
             invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.secho(ctx.get_help())
    else:
        click.echo(ctx.invoked_subcommand)
