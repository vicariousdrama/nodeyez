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
    @media only screen {
        img.imageinlist {
            display: inline;
            height: auto;
            width: 128px;
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
            font-size: 8pt;
            font-weight: 700;
            color: #000000
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
    }
    body {
        margin: 0;
        background-color: #404040;
    }
    </style>
</head>
<body>
    <div id="folderlist">
        <div class="folder"><a href="../">..</a></div>
    <xsl:for-each select="list/directory">
        <xsl:variable name="name">
            <xsl:value-of select="." />
        </xsl:variable>
        <div class="folder"><a href="{$name}"><xsl:value-of select="." /></a></div>
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
        <xsl:variable name="inscriptionid">
            <xsl:value-of select="substring-after(substring-before($name,'.'),'inscription-')" />
        </xsl:variable>
        <xsl:if test="contains('|gif|jpg|png|',concat('|',$extension,'|'))">
            <xsl:if test="not(contains('|774366-2057|774653-658|774718-424|',concat('|',$inscriptionid,'|')))">
                <img class="imageinlist" src="{.}" alt="{.}" />
            </xsl:if>
        </xsl:if>
    </xsl:for-each>
    </div>
    <img id="imageinfocus" />
</body>
</html>
</xsl:template>
</xsl:stylesheet>
