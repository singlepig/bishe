#!/usr/bin/env python
# encoding: utf-8

#Name:      qrcode.py
#Author:    singlepig
#e-mail:    gys.nanjing@gmail.com


'''QR二维码解码程序'''

import zbar
import Image
import sys
import qrcode

def encodeQR(version=None, error_correction='M', box_size=10, border=2, *content):
    '''生成QR码'''
    # 二维码版本号 version
    # 纠错等级 error_correction
    # box的大小 box_size
    # 二维码图像的边界宽度,单位box. border
    # 需要写入二维码的内容 content
    # 二维码图像的尺寸,单位pixel.  size
    ec_dict={
    'L':qrcode.constants.ERROR_CORRECT_L,
    'M':qrcode.constants.ERROR_CORRECT_M,
    'H':qrcode.constants.ERROR_CORRECT_H,
    'Q':qrcode.constants.ERROR_CORRECT_Q}

    if box_size <= 0:
        box_size = 10
    if version <= 0:
        version = None
    if ec_dict.has_key(error_correction):
        error_correction = ec_dict[error_correction]
    else:
        error_correction = ec_dict['M']
    '''
    print 'version : %s'
        'error_correction : %s'
        'box_size : %s'
        'border : %s'
        'content : %s' % (version, error_correction, box_size, border, content)
    '''
    # 生成二维码
    try:
        qr = qrcode.QRCode(
            version = version,
            error_correction = error_correction,
            box_size = box_size,
            border = border
            )
    except Exception, e:
        print e
    qr.add_data(content)
    qr.make(fit = True)
    img = qr.make_image()
    return img

def decodeQR(fileName):
    '''解析QR码'''
    scanner = zbar.ImageScanner()
    scanner.parse_config("enable")
    pil = Image.open(fileName).convert('L')
    width, height = pil.size
    raw = pil.tostring()
    image = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(image)
    data = ''
    for symbol in image:
        data+=symbol.data
    del(image)
    return data

def showArgs(args):
    '''show args given in commandline. '''
    print 'there are %s args.' %  len(args)
    for n in xrange(len(args)):
        print 'args[%s]: %s' % (n, args[n])
    print "=========="

def showHelp(args):
    '''show help infomation.'''
    print "Usage:"
    print "encode: " + args[0] + " -e [text] [image file name]"
    print "decode: " + args[0] + " -d [version=None] [error_correction='M'] [box_size=10] [border=2] *content [imgae file name]"
    print "\n\nReport problems to singlepig on gys.nanjing@gmail.com"

def main(*args):
    print args
    args=list(args)
    showArgs(args)
    if len(args)==1 or len(args)==2 or args[1]== '-h' or args[1]== '--help':
        '''When given -h/--help or with only 1 or 2 args, show help info.'''
        showHelp(args)

    elif args[1]=='-d':
        '''-d means decode the qrcode image file.'''
        try:
            print "infomation in %s is: " % args[2]
            print decodeQR(args[2])
        except:
            pass
    elif args[1]=='-e':
        '''-e means encode message to qrcode image file.'''
        try:
            #print "generated file: " + encodeQR(args[2],args[3])
            print 'encode args is:' + args[2:-1]
            img = encodeQR(args[2:-1])
            img.save(args[-1])
        except Exception, e:
            raise e
    else:
        print 'Illegal arguments.'

if __name__ == '__main__':
    main(*sys.argv[0:])
