#coding=utf-8
import re


"""
//***************************************************
//功能说明：Ubb代码处理
//创建时间： 2009-06-25
//创建人：    杜祖永
//***************************************************
//--------------------修改记录-------------------------
//修改人        修改时间                 修改原因
//----------------------------------------------------
//
//====================================================
//备注：
//
//****************************************************
"""
def transStringTool(aTransString):
    """
    功能说明：格式转化
    --------------------------------
    修改人            修改时间        
    --------------------------------
    杜祖永            2009-06-25
    
    """
    #aTransString = aTransString.replace("&", "&amp;");
    #aTransString = aTransString.replace("<", "&lt;");
    #aTransString = aTransString.replace(">", "&gt;");
    #aTransString = aTransString.replace(" ", "&nbsp;");#空格
    aTransString = aTransString.replace("\n", "<br>");#回车
    
    return aTransString
    
def UbbToHtm(sContent):
    """
    Ubb代码转换
    """
    sContent = transStringTool(sContent)
    #处理表情图片

#    r = new Regex(@"(\[MOD\])([   \S\t]*?)(\[\/MOD\])", RegexOptions.IgnoreCase);
#    for (m = r.Match(sDetail); m.Success; m = m.NextMatch())
#    {
#        sDetail = sDetail.Replace(m.Groups[0].ToString(), "<img src='"+HSIMPortal.Configuration.PortalConfiguration.UrlRoot+"images/ubbimages/tb/" + m.Groups[2].ToString() + ".gif'>");
#    }
    
    reg = '\[MOD\]\d+\[/MOD\]'
    reg2 = '\d+'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        replaceStr = g
        m2 = re.compile(reg2)
        list2 = m2.findall(replaceStr)
        img = '<img src="/site_media/images/ubbimages/tb/'+list2[0]+'.gif" />'
        sContent = sContent.replace(replaceStr, img)
    return sContent

def UbbToText(sContent):
    """
    Ubb代码转换
    """
    sContent = transStringTool(sContent)
    #处理表情图片

#    r = new Regex(@"(\[MOD\])([   \S\t]*?)(\[\/MOD\])", RegexOptions.IgnoreCase);
#    for (m = r.Match(sDetail); m.Success; m = m.NextMatch())
#    {
#        sDetail = sDetail.Replace(m.Groups[0].ToString(), "<img src='"+HSIMPortal.Configuration.PortalConfiguration.UrlRoot+"images/ubbimages/tb/" + m.Groups[2].ToString() + ".gif'>");
#    }
    
    reg = '\[MOD\]\d+\[/MOD\]'
    reg2 = '\d+'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        replaceStr = g
        m2 = re.compile(reg2)
        list2 = m2.findall(replaceStr)
        img = u'表情'+list2[0]
        sContent = sContent.replace(replaceStr, img)
    return sContent

def UbbToText2(sContent):
    """
    Ubb图片转换文字
    """
    sContent = transStringTool(sContent)
    #处理表情图片

#    r = new Regex(@"(\[MOD\])([   \S\t]*?)(\[\/MOD\])", RegexOptions.IgnoreCase);
#    for (m = r.Match(sDetail); m.Success; m = m.NextMatch())
#    {
#        sDetail = sDetail.Replace(m.Groups[0].ToString(), "<img src='"+HSIMPortal.Configuration.PortalConfiguration.UrlRoot+"images/ubbimages/tb/" + m.Groups[2].ToString() + ".gif'>");
#    }
    
    reg = '<img src="/site_media/images/ubbimages/tb/\d+.gif" />'
    reg2 = '\d+'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        replaceStr = g
        m2 = re.compile(reg2)
        list2 = m2.findall(replaceStr)
        img = u'表情'
        sContent = sContent.replace(replaceStr, img)
    return sContent

def UbbToFlash(sContent):
    """
     功能说明：对文本中插入的FLash进行格式转化
    --------------------------------
    修改人            修改时间        
    --------------------------------
    杜祖永            2009-09-21
    """
    width = 520
    height = 390
    #flash
    reg = '\[flash\]/?[^>]+\[/flash\]'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        img = """
            <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="%(w)s" height="%(h)s">
            <param name="movie" value="%(url)s">
            <param name="allowscriptaccess" value="always">
            <embed src="%(url)s" type="application/x-shockwave-flash" width="%(w)s" height="%(h)s" allowfullscreen="true" allowscriptaccess="always"></embed>
            </object>
            """ % {'url':g[7:-8],
                    'w':width,
                    'h':height}
        sContent = sContent.replace(g, img)
        
    #media
    reg = '\[flash=media\]/?[^>]+\[/flash\]'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        img = """
        <object classid="clsid:6bf52a52-394a-11d3-b153-00c04f79faa6" width="%(w)s" height="%(h)s">
            <param name="autostart" value="0">
            <param name="url" value="%(url)s">
            <embed autostart="false" src="%(url)s" type="video/x-ms-wmv" width="%(w)s" height="%(h)s" controls="imagewindow" console="cons"></embed>
            </object>""" % {'url':g[13:-8],
                            'w':width,
                            'h':height}
        sContent = sContent.replace(g, img)
    #real
    reg = '\[flash=real\]/?[^>]+\[/flash\]'
    m = re.compile(reg)
    list = m.findall(sContent)
    for g in list:
        img = """
        <object classid="clsid:cfcdaa03-8be4-11cf-b84b-0020afbbccfa" width="%(w)s" height="%(h)s">
            <param name="autostart" value="0">
            <param name="src" value="%(url)s">
            <param name="controls" value="Imagewindow,controlpanel">
            <param name="console" value="cons">
            <embed autostart="false" src="%(url)s" type="audio/x-pn-realaudio-plugin" width="%(w)s" height="%(h)s" controls="controlpanel" console="cons"></embed>
            </object>
              """ % {'url':g[12:-8],
                            'w':width,
                            'h':height}
        sContent = sContent.replace(g, img)
   
    return sContent
