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


def encodeQR():
	'''生成QR码'''


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
    print "decode: " + args[0] + " -d [imgae file name]"
    print "\n\nReport problems to singlepig on gys.nanjing@gmail.com"






if __name__ == '__main__':
    args=sys.argv
    showArgs(args)
    if len(args)==1 or len(args)==2 or args[1]== '-h' or args[1]== '--help':
        '''When given -h/--help or with only 1/2 args, show help info.'''
        showHelp(args)
    elif args[1]=='-d':
        '''decode the qrcode image file.'''
        try:
            print "infomation in %s is: " % args[2]
            print decodeQR(args[2])
        except:
            pass
    elif args[1]=='-e':
        try:
            print "generated file: " + gen_qrpic(args[2],args[3])
        except:
            pass
    else:
        print 'Illegal arguments.'
