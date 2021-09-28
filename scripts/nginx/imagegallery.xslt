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
    @media only screen and (min-width: 1025px) {
        img {
            width: 33%;
            height: auto;
        }
        img.imageinlist {
            display: inline;
            height: auto;
            width: 33%;
            margin: 1px;
            vertical-align: bottom;
        }
        #imagelist {
            width: 100%;
        }
        #imageinfocus {
            display: none;
        }
    }
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        img {
            max-width: calc(100%);
        }
        img.imageinlist {
            display: inline;
            height: 120px;
            margin: 3px;
            vertical-align: bottom;
        }
        #imagelist {
            width: 100%;
            height: 120px;
            overflow-x: auto;
            overflow-y: hidden;
            white-space: nowrap
        }
        #imageinfocus {
            width: 100%;
            height: auto;
            object-fit: contain;
        }
    }
    @media only screen and (max-width: 768px) {
        svg {
            max-width: calc(100%);
            height: auto;
        }
        img {
            max-width: calc(100%);
        }
        img.imageinlist {
            display: inline;
            height: 50px;
            margin: 1px;
            vertical-align: bottom;
        }
        #imagelist {
            width: 100%;
            height: 50px;
            overflow-x: auto;
            overflow-y: hidden;
            white-space: nowrap
        }
        #imageinfocus {
            width: 100%;
            height: auto;
            object-fit: contain;
        }
    }
    body {
        margin: 0;
        background-color: #404040;
    }
    </style>
    <script language="javascript">
    var timeouts = [];
    function clearTimeouts() {
        for (var i=0; i &lt; timeouts.length; i++) {
            clearTimeout(timeouts[i]);
        }
    }
    function removeQuerystring(v) {
        if (v.indexOf("?") != -1) { v = v.split("?")[0]; }
        return v;
    }
    function imageRefresh(img, timeout) {
        setTimeout(function() {
            var d = new Date;
            var http = removeQuerystring(img.src);
            img.src = http + '?d=' + d.getTime();
        }, timeout);
    }
    activeimagesrc = '';
    function rotateImages() {
        var imagesavailable = document.querySelectorAll(".imageinlist");
        timeout = 10000;
        if (activeimagesrc == '' &amp;&amp; imagesavailable.length > 0) {
            activeimagesrc = removeQuerystring(imagesavailable[0].getAttribute("src"));
            timeout = 1;
        } else {
            imagefound = false;
            for (var i = 0; i &lt; imagesavailable.length; i++) {
                var currentimagesrc = removeQuerystring(imagesavailable[i].getAttribute("src"));
                if (currentimagesrc.indexOf(activeimagesrc) > -1) {
                    imagefound = true;
                    if (i &lt; imagesavailable.length - 1) {
                        activeimagesrc = removeQuerystring(imagesavailable[i+1].getAttribute("src"));
                    } else {
                        activeimagesrc = removeQuerystring(imagesavailable[0].getAttribute("src"));
                    }
                    break;
                }
            }
            if (!imagefound) {
                console.log("image was not found");
            }
        }
        clearTimeouts();
        timeouts.push(setTimeout(function() {displayfocusedimage();}, timeout));
    }
    function focuson(img) {
        activeimagesrc = removeQuerystring(img.getAttribute("src"));
        displayfocusedimage();
    }
    function displayfocusedimage() {
        var d = new Date;
        imageinfocus.src = activeimagesrc + '?d=' + d.getTime();
        rotateImages();
    }
    window.addEventListener('load', rotateImages);
    </script>
</head>
<body>
<svg version="1.0" xmlns="http://www.w3.org/2000/svg"
 width="300.000000pt" height="33.000000pt" viewBox="0 0 300.000000 33.000000"
 preserveAspectRatio="xMidYMid meet">
<metadata>
Created by potrace 1.10, written by Peter Selinger 2001-2011
</metadata>
<g transform="translate(0.000000,33.000000) scale(0.100000,-0.100000)"
fill="#666666" stroke="none">
<path d="M1636 318 c5 -7 -17 -12 -38 -9 -4 0 -20 -16 -37 -36 l-30 -36 -8 34
c-8 29 -14 34 -43 37 -36 4 -50 -9 -50 -45 0 -33 -18 -28 -41 12 -18 30 -26
35 -59 35 -21 0 -42 -6 -48 -12 -5 -7 -10 -65 -10 -128 -1 -133 7 -153 60
-148 31 3 33 5 36 46 2 23 8 42 13 42 6 0 8 -4 4 -9 -3 -6 3 -14 12 -20 10 -6
15 -11 10 -11 -4 0 4 -13 18 -29 22 -24 31 -27 57 -22 25 5 34 13 40 39 8 30
9 31 27 14 52 -50 67 -57 116 -57 30 0 53 5 58 13 5 7 12 10 18 7 5 -4 9 -1 9
5 0 6 4 9 9 6 5 -3 11 1 15 9 8 23 34 18 38 -7 3 -21 9 -23 73 -26 73 -3 145
18 145 44 0 28 20 23 28 -8 l8 -33 103 -5 c58 -3 106 -1 112 5 15 15 11 61 -7
76 -9 7 -31 12 -50 11 -20 -2 -34 2 -34 9 0 6 6 9 14 6 8 -3 27 -2 43 2 31 8
39 40 18 76 -9 16 -8 23 6 37 17 16 21 13 33 -32 0 -3 11 -16 24 -30 24 -26
24 -26 22 -91 -2 -54 14 -72 62 -67 33 3 33 3 36 60 2 38 11 72 27 100 14 24
25 39 25 33 0 -5 4 -5 8 2 4 6 7 -31 8 -83 0 -52 5 -99 10 -104 11 -11 425
-16 443 -6 15 9 14 59 -1 74 -7 7 -29 12 -50 12 -40 0 -48 10 -23 30 8 7 15
19 15 26 0 8 4 14 9 14 29 0 66 110 42 124 -10 7 -69 8 -329 7 -170 0 -207 -7
-210 -36 -2 -22 -39 -15 -50 10 l-12 25 -144 0 c-141 0 -157 -3 -162 -32 -1
-5 -2 -11 -3 -14 0 -3 -13 3 -28 13 -48 33 -76 39 -142 34 l-64 -6 -11 -38
-11 -38 -13 31 c-8 16 -18 28 -22 25 -5 -3 -13 3 -19 12 -6 10 -11 15 -11 10
0 -4 -13 -1 -29 7 -29 15 -73 18 -65 4z m-232 -108 c27 -44 49 -80 51 -80 1 0
0 36 -3 80 l-5 80 27 0 26 0 0 -125 0 -125 -24 0 c-20 0 -34 15 -75 82 l-51
82 0 -82 c0 -81 0 -82 -25 -82 l-25 0 0 125 0 125 28 0 c23 0 34 -11 76 -80z
m346 52 c55 -56 48 -165 -13 -202 -54 -33 -137 -21 -170 24 -19 28 -27 87 -17
125 15 57 50 81 117 81 47 0 59 -4 83 -28z m249 0 c34 -33 46 -88 31 -142 -15
-56 -56 -80 -137 -80 l-62 0 -3 125 -3 125 73 0 c67 0 76 -2 101 -28z m271 8
c0 -18 -7 -20 -70 -20 l-70 0 0 -30 0 -30 65 0 c58 0 65 -2 65 -20 0 -18 -7
-20 -65 -20 l-65 0 0 -33 0 -33 70 4 c70 4 70 4 70 -22 l0 -26 -95 0 -95 0 0
125 0 125 95 0 c88 0 95 -1 95 -20z m105 -30 l29 -49 28 49 c24 42 33 50 58
50 l30 0 -45 -69 c-40 -61 -45 -76 -45 -125 0 -54 -1 -56 -27 -56 -27 0 -28 1
-24 51 3 46 -1 56 -43 120 -25 38 -46 71 -46 74 0 3 13 5 28 5 23 0 33 -9 57
-50z m355 30 c0 -18 -7 -20 -70 -20 l-70 0 0 -31 0 -31 65 4 c62 3 65 2 65
-19 0 -21 -4 -23 -64 -23 l-64 0 2 -31 1 -32 69 -1 c63 -1 69 -3 72 -23 4 -23
2 -23 -96 -23 l-100 0 0 125 0 125 95 0 c88 0 95 -1 95 -20z m220 -1 c0 -12
-29 -57 -65 -100 -36 -43 -65 -80 -65 -81 0 -2 32 -2 70 0 70 4 70 4 70 -22
l0 -26 -104 0 -105 0 2 25 c1 13 30 58 65 99 34 42 62 78 62 81 0 3 -25 5 -55
5 -48 0 -55 2 -55 20 0 19 7 20 90 20 85 0 90 -1 90 -21z m-127 -58 c7 -9 8
-12 1 -8 -6 3 -17 -5 -24 -18 -7 -14 -17 -25 -22 -25 -4 0 -8 -7 -8 -15 0 -8
-9 -19 -20 -25 -22 -12 -100 -11 -100 1 0 4 16 6 36 4 32 -2 38 1 49 28 11 26
10 35 -2 54 -15 23 -15 23 32 21 26 -2 51 -9 58 -17z m-1296 -103 c-3 -8 -6
-5 -6 6 -1 11 2 17 5 13 3 -3 4 -12 1 -19z"/>
<path d="M1620 230 c-29 -29 -28 -99 3 -128 29 -27 61 -28 87 -2 27 27 28 110
2 133 -25 23 -68 21 -92 -3z m70 -13 c10 -7 16 -29 17 -55 1 -24 -1 -41 -4
-38 -4 3 -12 1 -18 -4 -7 -6 -23 -9 -36 -7 -21 4 -24 10 -25 51 -1 40 2 49 20
56 28 11 28 11 46 -3z"/>
<path d="M1880 166 l0 -85 38 6 c54 8 62 19 62 79 0 59 -21 84 -72 84 l-28 0
0 -84z m65 49 c13 -4 14 -9 4 -26 -7 -15 -8 -19 0 -15 7 5 10 -4 8 -26 -2 -28
-6 -33 -30 -33 -26 -1 -27 1 -27 57 0 46 3 56 15 53 8 -3 22 -7 30 -10z"/>
<path d="M13 309 c-32 -33 10 -141 85 -220 31 -32 59 -56 63 -53 4 2 10 0 14
-6 3 -5 21 -10 40 -10 19 0 37 -5 40 -10 9 -14 115 -13 115 1 0 7 9 9 21 6 12
-3 18 -3 15 0 -3 4 16 21 43 39 27 18 56 48 65 65 15 31 15 34 -4 54 -32 34
-139 84 -240 111 -116 31 -239 42 -257 23z m160 -15 l37 -7 0 -86 c1 -47 5
-105 9 -128 10 -52 0 -55 -55 -14 -78 57 -126 127 -139 204 l-7 37 58 0 c33 0
76 -3 97 -6z m105 -50 c-9 -19 -9 -34 1 -60 10 -29 10 -38 -1 -51 -7 -9 -12
-19 -11 -22 2 -3 0 -15 -3 -25 -13 -39 -33 25 -33 104 0 76 7 91 39 83 16 -4
17 -9 8 -29z m182 -56 c28 -18 50 -36 50 -39 0 -14 -103 -101 -135 -115 -19
-8 -53 -14 -75 -14 l-41 0 16 31 c22 42 55 176 49 194 -8 20 66 -11 136 -57z
m-154 4 c-11 -10 -15 4 -8 28 l7 25 3 -23 c2 -13 1 -26 -2 -30z"/>
<path d="M126 242 c-3 -5 1 -9 9 -9 8 0 12 4 9 9 -3 4 -7 8 -9 8 -2 0 -6 -4
-9 -8z"/>
<path d="M60 229 c0 -5 5 -7 10 -4 6 3 10 8 10 11 0 2 -4 4 -10 4 -5 0 -10 -5
-10 -11z"/>
<path d="M106 183 c-6 -14 -5 -15 5 -6 7 7 10 15 7 18 -3 3 -9 -2 -12 -12z"/>
<path d="M90 146 c0 -2 8 -10 18 -17 15 -13 16 -12 3 4 -13 16 -21 21 -21 13z"/>
<path d="M440 150 c-12 -7 -10 -9 7 -7 12 0 19 5 17 9 -6 10 -6 10 -24 -2z"/>
<path d="M406 137 c3 -10 9 -15 12 -12 3 3 0 11 -7 18 -10 9 -11 8 -5 -6z"/>
<path d="M378 103 c7 -3 16 -2 19 1 4 3 -2 6 -13 5 -11 0 -14 -3 -6 -6z"/>
<path d="M985 305 c-115 -25 -200 -55 -265 -93 -84 -49 -87 -65 -21 -132 27
-28 51 -51 53 -51 14 1 48 -13 48 -20 0 -5 27 -9 60 -9 33 0 60 4 60 10 0 6
-18 10 -40 10 -68 0 -157 49 -196 107 -16 26 -16 27 7 46 13 11 54 35 92 53
l67 34 0 -29 c0 -39 46 -186 63 -199 15 -12 88 -21 81 -10 -5 7 3 9 22 7 3 0
15 10 26 23 11 13 25 22 30 20 5 -1 8 1 5 5 -4 9 29 44 36 37 9 -10 58 137 55
168 l-3 33 -60 2 c-33 1 -87 -4 -120 -12z m162 -44 c-10 -79 -68 -163 -143
-207 -25 -15 -47 -25 -49 -22 -2 2 1 37 6 78 6 41 9 98 7 127 -5 60 -7 59 116
62 l69 1 -6 -39z m-208 -79 c-1 -79 -15 -172 -18 -116 -1 11 -6 25 -13 32 -7
7 -12 41 -13 79 0 38 -4 74 -8 80 -5 9 -3 11 6 7 8 -3 18 0 22 5 16 27 25 -6
24 -87z m-60 20 c1 -7 -3 -10 -9 -7 -5 3 -10 18 -9 33 0 24 1 25 9 7 5 -11 9
-26 9 -33z"/>
<path d="M1031 270 c0 -8 4 -22 9 -30 12 -18 12 -2 0 25 -6 13 -9 15 -9 5z"/>
<path d="M1090 199 c0 -8 -7 -27 -15 -43 -12 -23 -12 -26 -1 -17 15 13 30 60
21 69 -3 3 -5 -1 -5 -9z"/>
<path d="M1039 103 c-13 -16 -12 -17 4 -4 16 13 21 21 13 21 -2 0 -10 -8 -17
-17z"/>
<path d="M1171 204 c0 -11 3 -14 6 -6 3 7 2 16 -1 19 -3 4 -6 -2 -5 -13z"/>
<path d="M755 120 c3 -5 8 -10 11 -10 2 0 4 5 4 10 0 6 -5 10 -11 10 -5 0 -7
-4 -4 -10z"/>
<path d="M785 100 c3 -5 8 -10 11 -10 2 0 4 5 4 10 0 6 -5 10 -11 10 -5 0 -7
-4 -4 -10z"/>
</g>
</svg>

    <div id="imagelist">
    <xsl:for-each select="list/file">
        <img class="imageinlist" src="{.}" alt="{.}" onload="imageRefresh(this, 10000);" onclick="focuson(this);" />
    </xsl:for-each>
    </div>
    <img id="imageinfocus" />
</body>
</html>
</xsl:template>
</xsl:stylesheet>
