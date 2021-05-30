import shutil
import os
from bs4 import BeautifulSoup as bs
from zipfile import ZipFile

tar_dir = "/home/leonard/Downloads/~/Downloads/FR/collec/"
textTree = {
    "chap_01": [
        "Prologue.htm",
        "第一章.htm",
        "第二章.htm",
        "第三章.htm",
        "第四章.htm",
        "第五章.htm",
        "第六章.htm",
        "第七章.htm",
        "第八章.htm"
    ],
    "chap_02": [
        "部分设定.htm",
        "EP9.htm",
        "EP10.htm",
        "EP11.htm",
        "EP12.htm",
        "EP13.htm",
        "EP14.htm",
        "EP15.htm",
        "EP16.htm"
    ]
}
figTree = {
    "chap_01_fig": ["cp_01_%.2d.jpg" % k for k in range(1, 21)],
    "chap_02_fig": ["cp_02_%.2d.jpg" % k for k in range(1, 21)]
}
cover = "cp_01_01.jpg"

bookmeta = {
    "title": "Fate/Requiem",
    "creator": "wzdlc1996"
}

def getContent(filename):
    with open(filename, "rb") as f:
        cont = f.read()
    htmPage = bs(cont, "html.parser")
    return "<html>\n<body>\n{}\n</body>\n</html>".format(htmPage.find(id="content"))


def makeTree():
    try:
        os.mkdir("./temp")
    except FileExistsError:
        print("remove the temp folder")
        return
    with open("./temp/mimetype", "w") as f:
        f.write("application/epub+zip")
    os.mkdir("./temp/META-INF")
    with open("./temp/META-INF/container.xml", "w") as f:
        f.write(
            """<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>"""
        )
    os.mkdir("./temp/OEBPS")
    os.mkdir("./temp/OEBPS/text")

    files = []
    ind = 0
    for x in textTree:
        dir_name = "text/{}".format(x)
        os.mkdir("./temp/OEBPS/" + dir_name)
        for ls in textTree[x]:
            ind += 1
            sec_name = "%.2d.html" % ind
            files.append("{}/{}".format(dir_name, sec_name))
            with open("./temp/OEBPS/{}/{}".format(dir_name, sec_name), "w") as f:
                f.write(getContent(tar_dir + ls))

    os.mkdir("./temp/OEBPS/images")
    imgs = []
    for x in figTree:
        imgs.append("{}.html".format(x))
        with open("./temp/OEBPS/{}.html".format(x), "w") as f:
            f.write("<html><body>")
            for ls in figTree[x]:
                shutil.copyfile(tar_dir + ls, "./temp/OEBPS/images/{}".format(ls))

                f.write(
                    "<img src=\"images/{}\" />\n".format(ls)
                )
            f.write("</body></html>")


    shutil.copyfile(tar_dir + cover, "./temp/OEBPS/images/cover")

    with open("./temp/OEBPS/content.opf", "w") as f:
        metas = "\n".join(["<dc:{}>{}</dc:{}>".format(x, v, x) for _, (x, v) in enumerate(bookmeta.items())])
        manis = "\n".join(
            ["<item id=\"{}\" href=\"{}\" media-type=\"application/xhtml+xml\"/>".format(x, x) for x in (files + imgs)]
        )

        spines = "\n".join(
            ["<itemref idref=\"{}\" />".format(x) for x in (files + imgs)]
        )

        f.write(
        """<?xml version="1.0" encoding="UTF-8" ?>
<package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
{}
<meta name="cover" content="cover" />
</metadata>
<manifest>
{}
<item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
<item id="cover" href="images/cover" media-type="image/jpeg"/>
</manifest>
<spine toc="ncx">
{}
</spine>
</package>
""".format(metas, manis, spines))

    navmap = []
    ind = -1
    indf = -1
    for cp in textTree:
        for sec in textTree[cp]:
            ind += 1
            navmap.append("""<navPoint id='{}' playOrder='{}'>
<navLabel>
<text>chapter: {}</text>
</navLabel>
<content src='{}' />
</navPoint>""".format(files[ind], len(navmap) + 1, "%.3d" % (ind + 1), files[ind]))

        indf += 1
        navmap.append("""<navPoint id='{}' playOrder='{}'>
<navLabel>
<text>images</text>
</navLabel>
<content src='{}' />
</navPoint>
""".format(imgs[indf], len(navmap) + 1, imgs[indf]))


    ncx = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head>
  <meta name="dtb:uid" content=" "/>
  <meta name="dtb:depth" content="-1"/>
  <meta name="dtb:totalPageCount" content="0"/>
  <meta name="dtb:maxPageNumber" content="0"/>
</head>
 <docTitle><text></text></docTitle>
 <docAuthor><text></text></docAuthor>
<navMap>
{}
</navMap>
</ncx>
    """.format("\n".join(navmap))

    with open("./temp/OEBPS/content.ncx", "w") as f:
        f.write(ncx)

    epub = ZipFile("book.epub", "w")
    os.chdir("./temp")
    for d, ds, fs in os.walk("."):
        for f in fs:
            epub.write(os.path.join(d, f))
    epub.close()
    #shutil.rmtree("../temp")
    



if __name__ == "__main__":
    makeTree()





