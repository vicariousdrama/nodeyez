<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8" indent="yes" />
<xsl:template match="/">
<xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
<html>
<head>
    <title><xsl:value-of select="$title" /></title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
    img.imageinlist {
        display: inline;
        height: 128px;
        width: 128px;
        object-fit: cover;
        margin: 0px;
        vertical-align: bottom;
    }
    #imagelist {
        width: 100%;
    }
    .folder {
        display: inline-block;
        overflow-wrap: hidden;
        width: 128px;
        height: 85px;
        margin: 0 auto;
        margin-top: 10px;
        position: relative;
        background-color: rgba(239,228,176,255);
        border-radius: 0 6px 6px 6px;
        box-shadow: 4px 4px 7px rgba(0,0,0,0.59);
        font-family: arial;
        font-size: 12pt;
        font-weight: 700;
        color: #444;
	text-align: center;
    }
    .folder:before {
        content: '';
        width: 50%;
        height: 12px;
        border-radius: 0 20px 0 0;
        background-color: rgba(239,228,176,255);
        position: absolute;
        top: -12px;
        left: 0px;
    }
    .textfile {
        background:#eee;
        background:-moz-linear-gradient(top, #ddd 0, #eee 15%, #fff 40%, #fff 70%, #eee 100%);
        background:-webkit-linear-gradient(top, #ddd 0, #eee 15%, #fff 40%, #fff 70%, #eee 100%);
        border:1px solid #ccc;
        -moz-border-radius:3px 15px 3px 3px;
        -webkit-border-radius:3px 15px 3px 3px;
        border-radius:3px 15px 3px 3px;
        -moz-box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        -webkit-box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        display: inline-block;
        width: 76px;
        height: 100px;
        position:relative;
        Ztext-indent:-9999em;
        margin-bottom: 12px;
        margin-top: 12px;
        margin-left: 25px;
        margin-right: 25px;
    }
    .textfile:before {
        content: '';
        position: absolute;
        right:0;
        width: 16px;
        height: 16px;
        background:#ccc;
        background:-moz-linear-gradient(45deg, #fff 0,  #eee 50%, #ccc 100%);
        background:-webkit-linear-gradient(45deg, #fff 0,  #eee 50%, #ccc 100%);
        box-shadow:rgba(0,0,0,0.05) -1px 1px 1px, inset white 0 0 1px;
        border-bottom:1px solid #ccc;
        border-left:1px solid #ccc;
        -moz-border-radius:0 14px 0 0;
        -webkit-border-radius:0 14px 0 0;
        border-radius:0 10px 0 0;
    }
    .textfile:after {
        content:"";
        display:block;
        position:absolute;
        left:0;
        top:0;
        width: 55%;
        margin: 15% 15% 0;
        background:#ccc;
        background:-moz-linear-gradient(top, #ccc 0, #ccc 20%, #fff 20%, #fff 40%, #ccc 40%, #ccc 60%, #fff 60%, #fff 80%, #ccc 80%, #ccc 100%);
        background:-webkit-linear-gradient(top, #ccc 0, #ccc 20%, #fff 20%, #fff 40%, #ccc 40%, #ccc 60%, #fff 60%, #fff 80%, #ccc 80%, #ccc 100%);
        height: 25%;
    }
    .otherfile {
        background:#99e;
        background:-moz-linear-gradient(top, #ddd 0, #99e 15%, #fff 40%, #fff 70%, #99e 100%);
        background:-webkit-linear-gradient(top, #ddd 0, #99e 15%, #fff 40%, #fff 70%, #99e 100%);
        border:1px solid #ccc;
        -moz-border-radius:3px 15px 3px 3px;
        -webkit-border-radius:3px 15px 3px 3px;
        border-radius:3px 15px 3px 3px;
        -moz-box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        -webkit-box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        box-shadow:inset rgba(255,255,255,0.8) 0 1px 1px;
        display: inline-block;
        width: 76px;
        height: 100px;
        position:relative;
        Ztext-indent:-9999em;
        margin-bottom: 12px;
        margin-top: 12px;
        margin-left: 25px;
        margin-right: 25px;
    }
    .otherfile:before {
        content: '';
        position: absolute;
        right:0;
        width: 16px;
        height: 16px;
        background:#ccc;
        background:-moz-linear-gradient(45deg, #fff 0,  #eee 50%, #ccc 100%);
        background:-webkit-linear-gradient(45deg, #fff 0,  #eee 50%, #ccc 100%);
        box-shadow:rgba(0,0,0,0.05) -1px 1px 1px, inset white 0 0 1px;
        border-bottom:1px solid #ccc;
        border-left:1px solid #ccc;
        -moz-border-radius:0 14px 0 0;
        -webkit-border-radius:0 14px 0 0;
        border-radius:0 10px 0 0;
    }
    .otherfile:after {
        content:"";
        display:block;
        position:absolute;
        left:0;
        top:0;
        width: 55%;
        margin: 15% 15% 0;
        background:#ccc;
        background:-moz-linear-gradient(top, #ccc 0, #ccc 20%, #fff 20%, #fff 40%, #ccc 40%, #ccc 60%, #fff 60%, #fff 80%, #ccc 80%, #ccc 100%);
        background:-webkit-linear-gradient(top, #ccc 0, #ccc 20%, #fff 20%, #fff 40%, #ccc 40%, #ccc 60%, #fff 60%, #fff 80%, #ccc 80%, #ccc 100%);
        height: 25%;
    }
    .filelabel {
        font-family:arial;
        font-size:12pt;
        font-weight:700;
        color:#444;
        text-align:center;
        padding-top: 40px;
    }
    body {
        margin: 0;
        background-color: #404040;
    }
    </style>
</head>
<body>
    <div id="folderlist">
    <a href="../"><div class="folder">(Up One Level)</div></a>
    <xsl:for-each select="list/directory">
        <xsl:variable name="name">
            <xsl:value-of select="." />
        </xsl:variable>
        <a href="{$name}"><div class="folder"><xsl:value-of select="." /></div></a>
    </xsl:for-each>
    </div>
    <div id="imagelist">
    <xsl:for-each select="list/file">
        <xsl:variable name="name">
            <xsl:value-of select="."/>
        </xsl:variable>
        <xsl:variable name="extension">
            <xsl:value-of select="substring-after($name, '.')" />
        </xsl:variable>
        <xsl:variable name="prefixremoved">
            <xsl:choose>
                <xsl:when test="starts-with($name,'inscription-')">
                    <xsl:value-of select="substring-after($name,'inscription-')" />
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$name" />
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="inscriptionid">
            <xsl:value-of select="substring-before($prefixremoved,'.')" />
        </xsl:variable>
        <xsl:variable name="blocknumber">
            <xsl:value-of select="number(substring-before($inscriptionid,'-'))" />
        </xsl:variable>
        <xsl:variable name="txidx">
            <xsl:value-of select="number(substring-after($inscriptionid,'-'))" />
        </xsl:variable>

        <xsl:if test="true() or ($blocknumber &lt;= 775079)">
            <xsl:if test="not(contains('|774366-2057|774653-658|774718-424|774783-1743|774783-1841|',concat('|',$inscriptionid,'|')))">
            <xsl:if test="not(contains('|774787-756|774792-2014|774804-3311|775073-857|775079-964|',concat('|',$inscriptionid,'|')))">
                <xsl:choose>
                <xsl:when test="contains('|bmp|gif|jpeg|jpg|png|svg|tiff|tif|webp|',concat('|',$extension,'|'))">
                    <a href="{$name}"><img class="imageinlist" src="{.}" alt="{.}" /></a>
                </xsl:when>
                <xsl:when test="contains('|html|txt|',concat('|',$extension,'|'))">
                    <a href="{$name}"><div class="textfile"><div class="filelabel"><xsl:value-of select="$blocknumber" /><br/><xsl:value-of select="$txidx" /><br/><xsl:value-of select="$extension" /></div></div></a>
                </xsl:when>
                <xsl:otherwise>
                    <a href="{$name}"><div class="otherfile"><div class="filelabel"><xsl:value-of select="$blocknumber" /><br/><xsl:value-of select="$txidx" /><br/><xsl:value-of select="$extension" /></div></div></a>
                </xsl:otherwise>
                </xsl:choose>
            </xsl:if>
            </xsl:if>
        </xsl:if>
    </xsl:for-each>
    </div>
    <img id="imageinfocus" />
</body>
</html>
</xsl:template>
</xsl:stylesheet>
