import os
import json
import click
from click.exceptions import ClickException
import telstra_pn

tpns = None


@click.group()
@click.option('--debug', is_flag=True)
@click.option('--headers/--no-headers', default=False)
@click.option('-o',
              '--output',
              default='text',
              type=click.Choice(['text', 'json'], case_sensitive=False))
@click.pass_context
def cli(ctx, output, headers, debug):
    global tpns
    ctx.ensure_object(dict)
    ctx.obj['output'] = output
    ctx.obj['headers'] = headers
    if debug:
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True
    tpns = telstra_pn.Session(token=os.environ['TPNTOKEN'])


# Endpoints

@cli.command()
@click.pass_context
def endpoints(ctx):
    '''Interact with TPN endpoints'''
    ctx.obj['eps'] = tpns.endpoints
    ctx.obj['names'] = [
        ('Name', 'name'),
        ('UUID', 'endpointuuid'),
        ('Type', 'type'),
        ('Creation Date', 'creationdate'),
        ('Datacenter Code', 'datacentercode'),
        ('Last Modified Date', 'lastmodifieddate'),
        ('Enabled', 'enabled'),
        ('Status', 'status'),
    ]


# Datacentres


@cli.group()
@click.pass_context
def dc(ctx):
    '''Interact with TPN datacentres'''
    ctx.obj['dcs'] = tpns.datacentres
    ctx.obj['names'] = [
        ('Code', 'datacentercode'),
        ('Name', 'datacentername'),
        ('UUID', 'datacenteruuid'),
        ('City', 'cityname'),
        ('Country', 'countryname')
    ]


@dc.command()
@click.pass_context
def list(ctx):
    '''list TPN datacenters'''
    dcs = ctx.obj['dcs']
    output_list(dcs, ctx)


@dc.command()
@click.argument('datacenter')
@click.pass_context
def info(ctx, datacenter):
    '''
    show information about a TPN datacenter

    DATACENTER is the code or uuid for a TPN datacenter
    '''
    dc = ctx.obj['dcs'][datacenter]
    if dc:
        output_single(dc, ctx)
    else:
        if ctx.obj['output'] == 'text':
            click.echo(f'datacenter {datacenter} not found')
        else:
            click.echo('{}')


def output_single(data: dict, ctx: object) -> None:
    if ctx.obj['output'] == 'text':
        output_single_text(data, ctx)
        return

    if ctx.obj['output'] == 'json':
        output_single_json(data, ctx)
        return

    raise ClickException(exit_code=1)


def output_single_text(data: dict, ctx: object) -> None:
    names = ctx.obj['names']
    if not data:
        click.echo('not found')

    if names is None:
        names = [(x, x) for x in data.keys()]
    for (name, key) in names:
        click.echo(f'{name}: {data[key]}')


def output_single_json(data: dict, ctx: object) -> None:
    outitem = {}
    for (name, key) in ctx.obj['names']:
        outitem[name] = data[key]

    click.echo(json.dumps(outitem))


def output_list(data: dict, ctx: object) -> None:
    if ctx.obj['output'] == 'text':
        output_list_text(data, ctx)
        return

    if ctx.obj['output'] == 'json':
        output_list_json(data, ctx)
        return

    raise ClickException(exit_code=1)


def output_list_text(data: dict, ctx: object) -> None:
    names = ctx.obj['names']
    widths = {name[1]: len(name[0]) for name in names}
    print(widths)
    for item in data:
        for (name, key) in names:
            print(item[key])
            if widths[key] < len(item[key]):
                widths[key] = len(item[key])


    if ctx.obj['headers']:
        output = ''
        for (name, key) in names:
            output += '{item:<{width}} '.format(item=name,
                                                width=widths[key])
        click.echo(output)
        output = ''
        for (name, key) in names:
            output += '-'*widths[key] + ' '
        click.echo(output)

    for item in data:
        output = ''
        for (name, key) in names:
            output += '{item:<{width}} '.format(item=item[key],
                                                width=widths[key])
        click.echo(output)


def output_list_json(data: dict, ctx: object) -> None:
    names = ctx.obj['names']
    outdata = []
    for item in data:
        outitem = {}
        for (name, key) in names:
            outitem[name] = item[key]
        outdata.append(outitem)

    click.echo(json.dumps(outdata))
