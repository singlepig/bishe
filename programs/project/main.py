#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import urllib
import web
import qrcode
try:
    from PIL import Image
except ImportError:
    import Image
from lib.mime import ImageMIME
from lib import charset

web.config.debug = True
urls = (
    '/', 'Index',  # 首页
    '/qr', 'QR',  # 二维码图片
    '/.*', 'Index',
)

# 应用模板
render = web.template.render('templates')
app = web.application(urls, globals())


class Index(object):
    """首页
    """
    def GET(self):
        return render.index()


class QR(object):
    """处理传来的数据并显示 QR Code 二维码图片
    """
    def handle_parameter(self, chl, chld, chs):
        """处理表单提交的变量
        """
        if len(chl) > 2953:  # 最大容量
            raise web.badrequest()
        chld = chld.upper()
        # chld 是非必需参数，有默认值
        if not chld:
            chld = 'M|4'
        # 处理 chld 参数值
        chld = chld.split('|')
        if len(chld) == 2:  # e.g. 'M|2'
            try:
                border = int(chld[1])  # 二维码与图片的边距
            except:
                border = 4
        elif len(chld) == 1:  # e.g. 'M'
            border = 4
        level = chld[0]  # 纠错级别
        if level not in ['L', 'M', 'Q', 'H']:
            level = 'M'  # 默认纠错级别
        if border < 0:
            border = 4

        try:
            chs = chs.lower()
            size = tuple([int(i) for i in chs.split('x')])
        except:
            raise web.badrequest()
        else:
            # 处理负数及零的情况，
            # 同时限制图片大小，防止图片太大导致系统死机
            if (size[0] * size[1] == 0 or size[0] < 0 or size[1] < 0 or (
                    size[0] > 600) or size[1] > 600):
                raise web.badrequest()

        # 由于生成的二维码图片是个正方形，所以由 size 的最小值组成的正方形
        # 来限制二维码图片大小
        square_size = size[0] if size[0] <= size[1] else size[1]
        # L,M,Q,H 纠错级别下 1~40 版本的最大容量(Binary)
        l_max = [17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321,
                 367, 425, 458, 520, 586, 644, 718, 792, 858, 929,
                 1003, 1091, 1171, 1273, 1367, 1465, 1528, 1628,
                 1732, 1840, 1952, 2068, 2188, 2303, 2431, 2563,
                 2699, 2809, 2953]
        m_max = [14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251,
                 287, 331, 362, 412, 450, 504, 560, 624, 666, 711,
                 779, 857, 911, 997, 1059, 1125, 1190, 1264, 1370,
                 1452, 1538, 1628, 1722, 1809, 1911, 1989, 2099,
                 2213, 2331]
        q_max = [11, 20, 32, 46, 60, 74, 86, 108, 130, 151, 177,
                 203, 241, 258, 292, 322, 364, 394, 442, 482, 509,
                 565, 611, 661, 715, 751, 805, 868, 908, 982, 1030,
                 1112, 1168, 1228, 1283, 1351, 1423, 1499, 1579, 1663]
        h_max = [7, 14, 24, 34, 44, 58, 64, 84, 98, 119, 137, 155,
                 177, 194, 220, 250, 280, 310, 338, 382, 403, 439,
                 461, 511, 535, 593, 625, 658, 698, 742, 790, 842,
                 898, 958, 983, 1051, 1093, 1139, 1219, 1273]

        # 根据纠错级别及字符数选定版本。
        if level == 'L':
            for i in l_max:
                if len(chl) < i:
                    version = l_max.index(i) + 1
                    break
            else:  # 如果超出了该纠错级别所能处理的最大字符数，抛出错误异常
                raise web.badrequest()
            error_correction = qrcode.constants.ERROR_CORRECT_L
        elif level == 'M':
            for i in m_max:
                if len(chl) < i:
                    version = m_max.index(i) + 1
                    break
            else:
                raise web.badrequest()
            error_correction = qrcode.constants.ERROR_CORRECT_M
        elif level == 'Q':
            for i in q_max:
                if len(chl) < i:
                    version = q_max.index(i) + 1
                    break
            else:
                raise web.badrequest()
            error_correction = qrcode.constants.ERROR_CORRECT_Q
        elif level == 'H':
            for i in h_max:
                if len(chl) < i:
                    version = h_max.index(i) + 1
                    break
            else:
                raise web.badrequest()
            error_correction = qrcode.constants.ERROR_CORRECT_H

        # 根据 python-qrcode 源码、square_size 及 version 参数求 box_size
        box_size = square_size / ((version * 4 + 17) + border * 2)
        # print box_size
        args = {'version': version,
                'error_correction': error_correction,
                'box_size': box_size,
                'border': border,
                'content': chl,
                'size': size
                }
        return args

    def show_image(self, **args):
        """返回图片 MIME 及 内容，用于显示图片
        """
        version = args['version']
        error_correction = args['error_correction']
        box_size = args['box_size']
        border = args['border']
        content = args['content']
        size = args['size']

        if box_size == 0:
            im = Image.new("1", (1, 1), "white")  # 空白图片
        else:
            # 生成二维码
            qr = qrcode.QRCode(
                version=version,
                error_correction=error_correction,
                box_size=box_size,
                border=border,
            )
            qr.add_data(content)
            qr.make(fit=True)
            im = qr.make_image()

        # im.show()
        # 将生成的二维码图片保存到内存中，用于下面的缩放处理
        temp_img = cStringIO.StringIO()
        im.save(temp_img, 'png')
        img_data = temp_img.getvalue()  # 获取图片内容
        im = Image.open(cStringIO.StringIO(img_data))
        x, y = im.size  # 生成的二维码图片大小
        rx, ry = size  # 用户请求的图片大小

        new_im = Image.new("1", (rx, ry), "white")
        # 将二维码图片粘贴到空白图片中并保持二维码图片居中
        paste_size = ((rx - x) / 2, (ry - y) / 2, (rx - x) / 2 + x,
                      (ry - y) / 2 + y)  # 粘贴位置
        new_im.paste(im, paste_size)  # 若位置全为负值则缩放并填充整个目标图片

        temp_img.write('')
        new_im.save(temp_img, 'png')  # 保存粘贴好的图片
        new_im_data = temp_img.getvalue()
        # 图片 MIME 类型
        MIME = ImageMIME().get_image_type(new_im_data)

        temp_img.close()  # 释放内存
        return (MIME, new_im_data)

    def GET(self):
        # TODO 解决 IE 浏览器下地址栏输入中文出现编码错误的情况

        # 能直接在地址栏输入非 ASCII 字符的参数值（非 IE 浏览器），后台自动解码
        # querys = web.ctx.query # 它及 web.input() 将字符都变成了类似 u'%B3%B5' 导致不能解码
        # 解决非 IE 浏览器下地址栏输入中文出现的编码问题， IE 浏览器暂时无解
        querys = web.ctx.env['QUERY_STRING']
        if querys == '':
            return web.badrequest()

        querys = querys.split('&')
        try:
            # 分割参数，能处理类似 'chl===hello&chls=200x200&chld=M|3'
            values = [x.split('=', 1) for x in querys]
            querys = {}
            for i in values:
                if len(i) == 1 and i[0] == 'chld':  # chld 是非必需参数
                    querys.setdefault(i[0], 'M|4')
                elif len(i) == 2 and i[0] in ['chl', 'chs', 'chld']:
                    querys.setdefault(i[0], i[1])
            # print querys
        except:
            return web.badrequest()

        chl = querys.get('chl')
        chl = chl.replace('+', '%20')  # 解决空格变加号，替换空格为 '%20'
        chs = querys.get('chs')
        if chl is None or chs is None:
            return web.badrequest()
        chld = querys.get('chld', 'M|4')

        chl = urllib.unquote(chl)
        chl = charset.encode(chl)  # 将字符串解码然后按 utf8 编码
        if chl is None:
            return web.badrequest()
        # print repr(chl)
        # TODO 如果编码不是 utf8，编码(quote())后重定向到 UTF8 编码后的链接
        args = self.handle_parameter(chl, chld, chs)
        MIME, data = self.show_image(**args)
        web.header('Content-Type', MIME)
        return data

    def POST(self):
        """处理 POST 数据
        """
        querys = web.input(chs='300x300')
        # 因为 web.input() 的返回的是 unicode 编码的数据，
        # 所以将数据按 utf8 编码以便用来生成二维码
        chl = querys.chl.encode('utf8')
        chs = querys.chs
        if chl is None or chs is None:
            return web.badrequest()
        chld = querys.chld
        args = self.handle_parameter(chl, chld, chs)
        MIME, data = self.show_image(**args)
        web.header('Content-Type', MIME)
        return data

if __name__ == '__main__':
    # web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
