import click
import sample.webdriver as webdriver

# TODO add a -k --keyfile containing username: xxx and password: xxxpip
# @click.option('-k', '--keyfile', callback=set_default, is_eager=True)

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.argument('host', envvar='ipmi_host')
def cli(ctx, username, password, host):
    """sends acpi commands to an ipmi host"""

    click.echo('connecting to {}'.format(host))

    with webdriver.Caravel(host, username, password) as caravel:
        controls = webdriver.RemoteControl(caravel)
        controls.stop()

    ### to put in the right place (to only display ipmi host status) ###
    # if ctx.invoked_subcommand is None:
    #     click.echo('I was invoked without subcommand')
    # else:
    #     click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
    ####################################################################

@cli.command()
def start():
    """start ipmi host"""
    click.echo('hello ')
