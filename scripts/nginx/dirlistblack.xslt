<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8" indent="yes" />
<xsl:template match="/">
<xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
<html>
<head>
    <title><xsl:value-of select="$title" /></title>
    <style>
        h1 {font-family:ubuntu;font-size:24pt;}
        td {font-family:'lucida console';font-size:10pt;padding:0px 5px 0px 5px;}
        div {column-count: 3;}
        .path {color:#cccc00}
    </style>
</head>
<body bgcolor="#000000" link="#008000" vlink="#008000" text="#999900">
<h1>Autoindex of Files <span class="path"><xsl:value-of select="$title" /></span></h1>
<hr />
<div>
<table>
    <tr><td><a href="../">../</a></td><td></td><td></td></tr>
    <xsl:for-each select="list/directory">
        <xsl:variable name="name">
            <xsl:value-of select="."/>
        </xsl:variable>
    <tr><td><a href="{$name}"><xsl:value-of select="."/></a></td><td></td><td></td></tr>
    </xsl:for-each>
    <xsl:for-each select="list/file">
        <xsl:variable name="name">
            <xsl:value-of select="."/>
        </xsl:variable>
        <xsl:variable name="size">
            <xsl:if test="string-length(@size) &gt; 0">
                <xsl:if test="number(@size) &gt; 0">
                    <xsl:choose>
                        <xsl:when test="round(@size div 1024) &lt; 1"><xsl:value-of select="@size" /></xsl:when>
                        <xsl:when test="round(@size div 1048576) &lt; 1"><xsl:value-of select="format-number((@size div 1024), '0.0')" />K</xsl:when>
                        <xsl:otherwise><xsl:value-of select="format-number((@size div 1048576), '0.00')" />M</xsl:otherwise>
                    </xsl:choose>
                </xsl:if>
            </xsl:if>
        </xsl:variable>
        <xsl:variable name="date">
            <xsl:value-of select="substring(@mtime,1,4)"/>-<xsl:value-of select="substring(@mtime,6,2)"/>-<xsl:value-of select="substring(@mtime,9,2)"/><xsl:text> </xsl:text>
            <xsl:value-of select="substring(@mtime,12,2)"/>:<xsl:value-of select="substring(@mtime,15,2)"/>:<xsl:value-of select="substring(@mtime,18,2)"/>
        </xsl:variable>
    <tr>
        <td><a href="{$name}"><xsl:value-of select="."/></a></td>
        <td><xsl:value-of select="$date"/></td>
        <td align="right"><xsl:value-of select="$size"/></td>
    </tr>
    </xsl:for-each>
</table>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
