import click
import sample.webdriver as webdriver

# TODO add a -k --keyfile containing username: xxx and password: xxxpip
# @click.option('-k', '--keyfile', callback=set_default, is_eager=True)

@click.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-c', '--command',
    type = click.Choice(['status', 'start', 'stop', 'force-stop', 'reset']),
    help = 'command to send to ipmi interface',
    show_default = True,
    required = True,
    default = 'status'
    )
@click.argument('host', envvar = 'ipmi_host')
def cli(username, password, host, command):
    """sends acpi commands to an ipmi host"""

    click.echo('Command: {}'.format(command))
    click.echo('Connecting to: {}...'.format(host))

    try:
        with webdriver.Caravel(host, username, password) as caravel:
            # access remote controls
            click.echo('Connected!')
            controls = webdriver.RemoteControl(caravel)
            command_launch = getattr(controls, command)
            click.echo('Ipmi status: {}'.format(controls.status()))

            try:
                command_launch()
            except ValueError as e:
                click.echo('Error: {}'.format(e))

    except ValueError as e:
        click.echo('Error: {}'.format(e))
    except RuntimeError as e:
        click.echo('Error: {}'.format(e))
