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
covers = [
    "cp_01_01.jpg",
    "cp_02_04.jpg"
    ]

bookmeta = {
    "title": "Fate/Requiem",
    "creator": "wzdlc1996"
}


def getContent(filename):
    with open(filename, "rb") as f:
        cont = f.read()
    htmPage = bs(cont, "html.parser")
    cont = htmPage.find(id="content").text
    cont = cont.split("\n")
    cont = "\n".join(["<p>{}</p><br>".format(x.replace("\xa0", "")) for x in cont])
    return "<html>\n<body>\n{}\n</body>\n</html>".format(cont)


def id_omit_slash(idstr):
    return idstr.replace("/", "_")


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
            (
                "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
                "<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n"
                "<rootfiles>"
                "<rootfile full-path=\"OEBPS/content.opf\" media-type=\"application/oebps-package+xml\"/>"
                "</rootfiles>\n"
                "</container>"
            )
        )
    os.mkdir("./temp/OEBPS")
    os.mkdir("./temp/OEBPS/text")

    # Generate the text directory
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

    ind = 0
    cov_indx = []
    for cover in covers:
        shutil.copyfile(tar_dir + cover, "./temp/OEBPS/images/cover{}".format(ind))
        with open("./temp/OEBPS/cover{}.html".format(ind), "w") as f:
            f.write(
                (
                    "<html><body>"
                    "<img src=\"images/cover{}\" />"
                    "</body></html>"
                ).format(ind)
            )
        cov_indx.append("cover{}.html".format(ind))
        ind += 1


    with open("./temp/OEBPS/content.opf", "w") as f:
        # opf file specifies the order of contents
        metas = "\n".join(["<dc:{}>{}</dc:{}>".format(x, v, x) for _, (x, v) in enumerate(bookmeta.items())])
        manis = "\n".join(
            [
                "<item id=\"{}\" href=\"{}\" media-type=\"application/xhtml+xml\"/>".format(
                    id_omit_slash(x), x
                ) for x in (cov_indx + files + imgs)
            ]
        )

        spines = "\n".join(
            ["<itemref idref=\"{}\" />".format(id_omit_slash(x)) for x in (cov_indx + files + imgs)]
        )

        f.write(
            (
                "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
                "<package version=\"2.0\" unique-identifier=\"PrimaryID\" xmlns=\"http://www.idpf.org/2007/opf\">\n"
                "<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">\n"
                "{}\n"
                "</metadata>\n"
                "<manifest>\n"
                "{}\n"
                "<item id=\"ncx\" href=\"content.ncx\" media-type=\"application/x-dtbncx+xml\"/>\n"
                "<item id=\"cover\" href=\"images/cover\" media-type=\"image/jpeg\"/>\n"
                "</manifest>\n"
                "<spine toc=\"ncx\">{}</spine>\n"
                "</package>"
            ).format(metas, manis, spines)
        )

    navmap = []
    ind = -1
    indf = -1
    for cp in textTree:
        indf += 1
        navmap.append(
            (
                "<navPoint id='{}' playOrder='{}'>"
                "<navLabel>"
                "<text>cover</text>"
                "</navLabel>"
                "<content src='{}' />"
                "</navPoint>"
            ).format(id_omit_slash(cov_indx[indf]), len(navmap) + 1, cov_indx[indf])
        )
        for sec in textTree[cp]:
            ind += 1
            navmap.append(
                (
                    "<navPoint id='{}' playOrder='{}'>"
                    "<navLabel>"
                    "<text>chapter: {}</text>"
                    "</navLabel>"
                    "<content src='{}' />"
                    "</navPoint>"
                ).format(id_omit_slash(files[ind]), len(navmap) + 1, "%.3d" % (ind + 1), files[ind])
            )


        navmap.append(
            (
                    "<navPoint id='{}' playOrder='{}'>"
                    "<navLabel><text>images</text></navLabel>"
                    "<content src='{}' />"
                    "</navPoint>\n"
             ).format(id_omit_slash(imgs[indf]), len(navmap) + 1, imgs[indf])
        )

    ncx = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<!DOCTYPE ncx PUBLIC \"-//NISO//DTD ncx 2005-1//EN\" \"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd\">\n"
        "<ncx version=\"2005-1\" xmlns=\"http://www.daisy.org/z3986/2005/ncx/\">\n"
        "<head>\n"
        "<meta name=\"dtb:uid\" content=\" \"/>\n"
        "<meta name=\"dtb:depth\" content=\"-1\"/>\n"
        "<meta name=\"dtb:totalPageCount\" content=\"0\"/>\n"
        "<meta name=\"dtb:maxPageNumber\" content=\"0\"/>\n"
        "</head>\n"
        "<docTitle><text>test</text></docTitle>\n"
        "<docAuthor><text>test</text></docAuthor>\n"
        "<navMap>{}</navMap>\n"
        "</ncx>"
    ).format("\n".join(navmap))

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





