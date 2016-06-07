#coding=utf-8
import inspect, os, datetime
import logging, random
import StringIO

from PIL import Image, ImageDraw, ImageFont, ImageColor

from django.http import HttpResponse

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)


def get_color():
    """
    get random color
    """
    colors = ['Black', 'Orange', 'Red', 'Brown', 'DarkBlue', 'Purple',
              'DarkCyan', 'DarkBlue']
    return ImageColor.getrgb(colors[random.randrange(1, 9)-1])


def get_font():
    """
    get random font-size
    """
    try:
        # print 'BASE_DIR2=', BASE_DIR
        return ImageFont.truetype(BASE_DIR + "/VeraIt.ttf", random.randrange(25, 35, 5))

    except Exception, e:
        return ImageFont.truetype("/Virtualenv/esms/VeraIt.ttf", random.randrange(25, 35, 5))


def make_check_code_image(request): 
    """
    make code image
    """
    try:
        color = ImageColor.getrgb('white')
        im = Image.new('RGB',(90,32), color) 
        draw = ImageDraw.Draw(im)

        rand_str = ''
        codeArr = ['a','b','c','d','e','f','g','h','k','m','n','q','r','s','t','u','v','w','x','y','z']
        codeArr += ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','U','V','W','X','Y','Z']
        codeArr = codeArr + ['1','2','3','4','5','6','7','8','9']
        for i in range(4):
            rand_str += codeArr[random.randint(0, 53)]
        color = ImageColor.getrgb('LightGray')
        for i in range(200):
            x = random.randrange(1,90)
            y = random.randrange(1,32)
            draw.point((x, y), fill=color)

        draw.text((3, 1), rand_str[0], fill=get_color(), font=get_font())
        draw.text((23, 1), rand_str[1], fill=get_color(), font=get_font())
        draw.text((43, 1), rand_str[2], fill=get_color(), font=get_font())
        draw.text((63, 1), rand_str[3], fill=get_color(), font=get_font())
        draw.line((0, 10, 85, 20), fill=get_color())
        del draw
        
        request.session['checkcode'] = rand_str  
        buf = StringIO.StringIO()
        im.save(buf, 'gif')
        # buf.closed
        return HttpResponse(buf.getvalue(), 'image/gif')
    except Exception, e:
        log.error("%s:%s" % (inspect.stack()[0][3], e))
