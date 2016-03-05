# -*- coding: utf-8 -*-
import json
import web
import qq_api as API

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

NOT_FOUND = lambda msg: msg if web.notfound(msg) else "404 Page Not Found!"


PAGE = web.template.render("templates", base="layout")

class Pageqq:
    def GET(self, qq='index'):
        if qq=='index':
            return PAGE.Pageqq(qq, [])

        if not qq.isdigit():
            return NOT_FOUND('bad qq num:%r.' % (qq,))
        qq = int(qq)
        qqinfo_list = API.qqinfo(qq)
        for item in qqinfo_list:
            item['QQUrl'] = '/qq/%s.html' % (item['QQNum'],)
            item['QunUrl'] = '/qun/%s.html' % (item['QunNum'],)
        return PAGE.Pageqq(qq, json.dumps(qqinfo_list))

class Pagequn:
    def GET(self, qun='index'):
        if qun=='index':
            return PAGE.Pagequn(qun, [])

        if not qun.isdigit():
            return NOT_FOUND('bad qun num:%r.' % (qun,))
        qun = int(qun)
        quninfo_dict = API.quninfo(qun)
        quninfo_dict['Members'] = API.qunmembers(qun)
        for item in quninfo_dict['Members']:
            item['QQUrl'] = '/qq/%s.html' % (item['QQNum'],)
        return PAGE.Pagequn(qun, json.dumps(quninfo_dict))

class Pagenick:
    def GET(self, nick='index'):
        if nick=='index':
            return PAGE.Pagenick(nick, [])

        if not isinstance(nick, unicode) or len(nick)>=6:
            return NOT_FOUND('bad nick str:%r.' % (nick,))

        qq_list = API.nickqqs(nick)
        qqinfo_dict = API.qqinfo_ex(set(qq_list))
        for _, qqinfo_list in qqinfo_dict.items():
            for item in qqinfo_list:
                item['QQUrl'] = '/qq/%s.html' % (item['QQNum'],)
                item['QunUrl'] = '/qun/%s.html' % (item['QunNum'],)
        return PAGE.Pagenick(nick, json.dumps(qqinfo_dict.values()))

class Home:
    def GET(self, args=None):
        return "Hello World!"

class Apijson:
    def GET(self):
        api = web.input(func="apihelp", args='', indent='', callback='')
        func = getattr(API, api.func, API.apihelp)

        if not getattr(func, 'is_api', False):
            return NOT_FOUND("404 Run Error:%r." % ('bad func name',))

        try:
            args = func.args_parser(api.args, api)
            result = func(args)

            indent = api.indent
            indent=int(indent) if indent and indent.isdigit() else None
            json_str = json.dumps(result, indent=indent)
            return json_str if not api.callback else '%s(%s);' % (api.callback, json_str)
        except Exception as ex:
            return NOT_FOUND("404 Run Error:%r." % (ex,))



class StaticFile:
    def GET(self, sfile):
        web.seeother('/static/'+sfile)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()