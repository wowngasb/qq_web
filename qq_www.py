# -*- coding: utf-8 -*-
import json
import web
import qq_api as API

web.config.debug = False

urls = (
    '/api', 'Apijson',
    '/qq/(.*).html', 'Pageqq',
    '/qun/(.*).html', 'Pagequn',
    '/nick/(.*).html', 'Pagenick',
    '/qq/', 'Pageqq',
    '/qun/', 'Pagequn',
    '/nick/', 'Pagenick',
    '/(.*.ico)', 'StaticFile',
    '/(.*)', 'Home',
)

NOT_FOUND = lambda msg: web.notfound(msg) if msg else web.HTTPError("404 Page Not Found!")


PAGE = web.template.render("templates", base="layout")

class Pageqq:
    def GET(self, qq='index'):
        qq = qq if qq else 'index'
        if qq=='index':
            return PAGE.Pageqq(0, [])

        if not qq.isdigit():
            raise NOT_FOUND('bad qq num:%r.' % (qq,))
        qq = int(qq)
        qqinfo_list = API.qqinfo(qq)

        return PAGE.Pageqq(qq, json.dumps(qqinfo_list))

class Pagequn:
    def GET(self, qun='index'):
        qun = qun if qun else 'index'
        if qun=='index':
            return PAGE.Pagequn(0, [])

        if not qun.isdigit():
            raise NOT_FOUND('bad qun num:%r.' % (qun,))
        qun = int(qun)
        quninfo_dict = API.quninfo(qun)
        quninfo_dict['Members'] = API.qunmembers(qun)

        return PAGE.Pagequn(qun, json.dumps(quninfo_dict))

class Pagenick:
    def GET(self, nick='index'):
        nick = nick if nick else 'index'
        if nick=='index':
            return PAGE.Pagenick('', [])

        if not isinstance(nick, unicode):
            raise NOT_FOUND('bad nick str:%r.' % (nick,))
        nick_list = nick.split()
        qq_list = set()
        for _nick in nick_list:
            _qq_list = set(API.nickqqs(_nick))
            qq_list = _qq_list if not qq_list else qq_list.intersection(_qq_list)

        qqinfo_dict = API.qqinfo_ex(qq_list)
        nick_info = {
            'Qqlist': list(qq_list),
            'QunList': dict(qqinfo_dict),
        }
        return PAGE.Pagenick(nick, json.dumps(nick_info))

class Home:
    def GET(self, args=None):
        return "Hello World!"

class Apijson:
    def GET(self):
        api = web.input(func="apihelp", args='', indent='', callback='')
        api = api if api else 'apihelp'
        func = getattr(API, api.func, API.apihelp)

        if not getattr(func, 'is_api', False):
            raise NOT_FOUND("404 Run Error:%r." % ('bad func name',))

        try:
            args = func.args_parser(api.args, api)
            result = func(args)

            indent = api.indent
            indent=int(indent) if indent and indent.isdigit() else None
            json_str = json.dumps(result, indent=indent)
            return json_str if not api.callback else '%s(%s);' % (api.callback, json_str)
        except Exception as ex:
            raise NOT_FOUND("404 Run Error:%r." % (ex,))



class StaticFile:
    def GET(self, sfile):
        web.seeother('/static/'+sfile)


if __name__ == "__main__":
    app = web.application(urls, globals(), autoreload=True)
    app.run()