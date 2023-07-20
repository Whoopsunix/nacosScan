from moudle import jwtToken
from moudle import apiBypass
import click


class UrlOption(click.Option):
    def __init__(self, *args, **kwargs):
        # 设置自定义选项属性
        kwargs.setdefault('type', str)  # 设置选项的类型
        kwargs.setdefault('metavar', '<url>')  # 设置选项的显示名称
        kwargs.setdefault('help', 'search by url')  # 设置选项的帮助提示
        super().__init__(*args, **kwargs)


class UrlsOption(click.Option):
    def __init__(self, *args, **kwargs):
        # 设置自定义选项属性
        kwargs.setdefault('type', click.File('r'))  # 设置选项的类型
        kwargs.setdefault('metavar', '<file>')  # 设置选项的显示名称
        kwargs.setdefault('help', 'load url from file')  # 设置选项的帮助提示
        super().__init__(*args, **kwargs)


CONTEXT_SETTINGS = dict(
    help_option_names=['--help', '-help', '-h', '--h'],
    default_map={
    }
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True, help='show version')
def run(version):
    '''
        https://github.com/Whoopsunix/nacosScan \n
        eg:\n
            python3 nacosScan.py jwt -h \n
            python3 nacosScan.py api -h \n
                            By. Whoopsunix
    '''
    if version:
        print("v1.0")
    pass


@run.command('jwt', help='default jwtToken vul')
@click.option('-u', '--url', cls=UrlOption)
@click.option('-uf', '--urls', cls=UrlsOption)
@click.option('-t', '--accesstoken', type=str, metavar='<str>', help='you can change accessToken')
@click.option('-user', '--username', type=str, metavar='<str>', help='input username')
@click.option('-pass', '--password', type=str, metavar='<str>', help='input password')
def run_jwt_vul(url, urls, accesstoken, username, password):
    jwttoken = jwtToken.Manager(url, urls, accesstoken, username, password)
    jwttoken.run()


@run.command('api', help='api bypass add user')
@click.option('-u', '--url', cls=UrlOption)
@click.option('-uf', '--urls', cls=UrlsOption)
@click.option('-user', '--username', type=str, metavar='<str>', help='username default is nasin')
@click.option('-pass', '--password', type=str, metavar='<str>', help='password default is natan')
def api_bypass(url, urls, username, password):
    apibypass = apiBypass.Manager(url, urls, username, password)
    apibypass.run()
