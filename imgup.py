from math import ceil
import os
from typing import List
import requests
import json
import argparse
import logging
import re
from lxml.html import fromstring
import asyncio
import pyimgbox
from time import time
from datetime import datetime

PTPIMG_APIKEY = ""
HDB_USER_NAME = ""
HDB_PASS_KEY = ""

HDB_COOKIE = "" #Optional

FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("img_uploader")
logger.setLevel(logging.INFO)

ImageHost = {
    "PTP": "ptpimg",
    "HDB": "hdbimg",
    "PTer": "imgbox",
    "NP": "imgbox",
    "BHD": "imgbox",
    "MTV": "ptpimg"
}

OutputFileName = {
    "c": "Comparison",
    "p": "Preview"
}

sitemapping = {"pter": "PTer", "bhd": "BHD", "mtv": "MTV",
               "ptp": "PTP", "np": "NP", "hdb": "HDB"}


class BBCodeGen(object):
    def __init__(
        self,
        site: str,
        upload_type: str,
        url: List[List[str]],
        thumb: List[List[str]],
        screen_types: List[str],
        bbcode_to_file: bool = False
    ):
        self.site = site
        self.upload_type = upload_type
        self.isComparision = True if upload_type == 'c' else False
        self.urls = url
        self.thumbs = thumb
        self.screen_types = screen_types
        self.bbcode_to_file = bbcode_to_file

    def FormatImgBBCode(self, comparsion_img_sep: str = " ", max_preview_img_per_row: int = 2) -> str:
        bb = ""
        num_img_groups = len(self.urls[0])
        if self.isComparision:
            for index in range(0, num_img_groups):
                if self.thumbs:
                    bb += comparsion_img_sep.join(
                        [f"[url={self.urls[i][index]}][img]{self.thumbs[i][index]}[/img][/url]" for i in range(0, len(self.urls))])
                else:
                    bb += comparsion_img_sep.join(
                        [f"{self.urls[i][index]}" for i in range(0, len(self.urls))])
                bb += "\n\n"
        else:
            # for index in range(0, len(self.urls), max_preview_img_per_row):
            max_rows = ceil(len(self.urls[0])/max_preview_img_per_row)

            for index in range(0, max_rows):
                start = index*max_preview_img_per_row
                if (start + max_preview_img_per_row) < num_img_groups:
                    end = start + max_preview_img_per_row
                else:
                    end = num_img_groups

                if self.thumbs:
                    bb += " ".join([f"[url={self.urls[0][i]}][img]{self.thumbs[0][i]}[/img][/url]"
                                    for i in range(start, end)])
                else:
                    bb += " ".join([f"[img]{self.urls[0][i]}[/img]"
                                    for i in range(start, end)])
                bb += "\n"
        return bb

    def MakeBBCodeHDB(self):
        bb = ""
        bb += f"[center][size=4][b][color=Blue]"
        bb += f"{' Vs '.join(self.screen_types)}"
        bb += "[/color][/b][/size]\n"
        bb += self.FormatImgBBCode(comparsion_img_sep=" ",
                                   max_preview_img_per_row=2)
        bb += "[/center]\n"
        return bb

    def MakeBBCodePTP(self):
        bb = ""
        if self.isComparision:
            bb += f"[comparison="
            bb += f"{','.join(self.screen_types)}"
            bb += "]\n"
        bb += self.FormatImgBBCode(comparsion_img_sep="\n",
                                   max_preview_img_per_row=1)
        if self.isComparision:
            bb += f"[/comparison]\n"
        return bb

    def MakeBBCodePTER(self):
        bb = ""
        bb += f"[center][size=4][b][color=Blue]"
        bb += f"{' Vs '.join(self.screen_types)}"
        bb += "[/color][/b][/size]\n"

        if len(self.screen_types) == 1:
            imgToken = "[img]"
        else:
            imgToken = f"[img{len(self.screen_types)}]"
        num_img_groups = len(self.urls[0])
        for index in range(0, num_img_groups):
            if self.thumbs:
                bb += " ".join(
                    [f"[url={self.urls[i][index]}]{imgToken}{self.thumbs[i][index]}[/img][/url]" for i in range(0, len(self.urls))])
            else:
                bb += " ".join(
                    [f"[img]{self.urls[i][index]}[/img]" for i in range(0, len(self.urls))])
            bb += "\n"

        bb += "[/center]\n"
        return bb

    def MakeBBCodeNP(self):
        bb = ""
        bb += f"[center][size=4][b][color=Blue]"
        bb += f"{' Vs '.join(self.screen_types)}"
        bb += "[/color][/b][/size]\n"
        bb += self.FormatImgBBCode(comparsion_img_sep=" ",
                                   max_preview_img_per_row=1)
        bb += "[/center]\n"
        return bb

    def MakeBBCodeBHD(self):
        bb = ""
        if self.isComparision:
            bb += f"[comparison="
            bb += f"{','.join(self.screen_types)}"
            bb += "]\n"
            num_img_groups = len(self.urls[0])
            for index in range(0, num_img_groups):
                bb += "\n".join(
                    [f"[img]{self.urls[i][index]}[/img]" for i in range(0, len(self.urls))])
                bb += "\n\n"
            bb += f"[/comparison]\n"
        else:
            bb += self.FormatImgBBCode(comparsion_img_sep=" ",
                                       max_preview_img_per_row=2)
        return bb

    def MakeBBCodeMTV(self):
        bb = ""
        if self.isComparision:
            bb += f"[comparison="
            bb += f"{','.join(self.screen_types)}"
            bb += "]\n"
        bb += self.FormatImgBBCode(comparsion_img_sep="\n",
                                   max_preview_img_per_row=1)
        if self.isComparision:
            bb += f"[/comparison]\n"
        return bb

    def MakeBBCode(self):
        BBCode = getattr(self, 'MakeBBCode'+self.site.upper())()
        print(f"\n{self.site} BBCODE:")
        print(f"{BBCode}\n")

        if self.bbcode_to_file:
            if self.isComparision:
                compare_type = 'Vs'.join(self.screen_types)
                file_name = f"{self.site}{OutputFileName[self.upload_type]}_{compare_type}.txt"
            else:
                file_name = f"{self.site}{OutputFileName[self.upload_type]}.txt"

            with open(file_name, "w") as f:
                f.write(BBCode)


class UpImgBase(object):
    def __init__(
        self,
        file_list: List[str],
        upload_type: str,
        img_type: str
    ):
        def GetFrameNumAndTypes(filepaths: List[str], imgType: str):
            files = [file.split('-')[0] for file in filepaths]
            FileType = [file.split(
                '-')[1].replace(f".{imgType}", "") for file in filepaths]

            FileType = list(dict.fromkeys(FileType))
            Addorder = ['Source', 'Source(gamma fixed)', 'Gammafixed',
                        'Gamma fixed', 'Filtered', 'Filtered(Deband)', 'Encode']
            OrderedType = []

            for type in Addorder:
                OrderedType += [type] if type in FileType else []

            OrderedType += [type for type in FileType if type not in Addorder]
            files = list(dict.fromkeys(files))
            return sorted(files, key=lambda x: int(x)), OrderedType

        self.file_list = file_list
        self.upload_type = upload_type
        self.img_type = img_type

        self.isComparision = True if upload_type == 'c' else False
        if self.isComparision:
            self.FrameNums, self.screen_types = GetFrameNumAndTypes(
                file_list, self.img_type)
            logger.debug(f"Frames {self.FrameNums}")
            logger.debug(f"types {self.FrameNums}")
        else:
            self.screen_types = ["Preview"]

    def FormatImgLink(self, urls, thumbs):
        num_screen_types = len(self.screen_types)
        url = []
        thumb = []
        for type in range(0, num_screen_types):
            url.append(urls[type::num_screen_types])
            if thumbs:
                thumb.append(thumbs[type::num_screen_types])

        return url, thumb, self.screen_types


class UpImageImgbox(UpImgBase):
    def __init__(
        self,
        file_list: List,
        upload_type: str = None,
        img_type: str = "png",
    ):
        UpImgBase.__init__(self, file_list, upload_type, img_type)

    def set_gallery_name(self, gallery_name):
        self.gallery_name = gallery_name if gallery_name is not None else "imgBox_UP_" + \
            datetime.now().strftime("%Y%m%d_%H:%M:%S")

    def Upload(self):
        async def upload_img():
            async with pyimgbox.Gallery(title=f"{self.gallery_name}") as gallery:
                gallery.thumb_width = 350
                urls = []
                thumbs = []
                if self.isComparision:
                    for Frame in self.FrameNums:
                        for screen_type in self.screen_types:
                            filename = Frame+'-' + \
                                screen_type+f'.{self.img_type}'
                            sub = await gallery.upload(filename)
                            urls.append(sub['image_url'])
                            thumbs.append(sub['thumbnail_url'])
                            logger.info(
                                f"ImgBox: {filename} was uploaded successfully to gallery {self.gallery_name}")
                else:
                    for filename in self.file_list:
                        sub = await gallery.upload(filename)
                        urls.append(sub['image_url'])
                        thumbs.append(sub['thumbnail_url'])
                        logger.info(
                            f"ImgBox: {filename} was uploaded successfully to gallery {self.gallery_name}")
                return self.FormatImgLink(urls, thumbs)

        return asyncio.run(upload_img())


class UpImagePTP(UpImgBase):
    def __init__(
        self,
        file_list: List,
        upload_type: str = None,
        img_type: str = "png",
    ):
        UpImgBase.__init__(self, file_list, upload_type, img_type)

    def set_ptp_api_key(self, api_key):
        self.PTP_API_KEY = api_key

    """
    Part of code is from https://github.com/LeiShi1313/Differential/blob/main/differential/utils/image/ptpimg.py
    """

    def upload_img(self, filename: str) -> str:
        data = {'api_key': self.PTP_API_KEY}
        files = {'file-upload[0]': open(filename, 'rb')}
        req = requests.post('https://ptpimg.me/upload.php',
                            data=data, files=files)
        try:
            res = req.json()
        except json.decoder.JSONDecodeError:
            res = {}
        if not req.ok:
            print(
                f"Failed to upload img: HTTP {req.status_code}, reason: {req.reason}")
            return None
        if len(res) < 1 or 'code' not in res[0] or 'ext' not in res[0]:
            print(f"Failed to get img link")
            return None

        logger.info(
            f"PTPImg: {filename} was uploaded successfully.")
        return f"https://ptpimg.me/{res[0].get('code')}.{res[0].get('ext')}"

    def Upload(self):
        urls = []
        if self.isComparision:
            for Frame in self.FrameNums:
                for screen_type in self.screen_types:
                    filename = Frame+'-'+screen_type+f'.{self.img_type}'
                    urls.append(self.upload_img(filename))
        else:
            for filename in self.file_list:
                urls.append(self.upload_img(filename))

        return self.FormatImgLink(urls, None)


class UpImageHDBCookie(UpImgBase):
    def __init__(
        self,
        file_list: List,
        upload_type: str = None,
        img_type: str = "png",
    ):
        UpImgBase.__init__(self, file_list, upload_type, img_type)

    def set_hdb_cookie(self, cookie: str):
        self.HDB_COOKIE = cookie

    def set_gallery_name(self, gallery_name: str):
        self.gallery_name = gallery_name

    def get_hdb_uploadid(self) -> str:
        req = requests.get("https://img.hdbits.org",
                           headers={"cookie": self.HDB_COOKIE})
        m = re.search(r"uploadid=([a-zA-Z0-9]{15})", req.text)
        if m:
            return m.groups()[0]
        else:
            raise RuntimeError()

    def get_hdb_exist_gallery_id(self) -> str:
        req = requests.get(
            f"https://img.hdbits.org/listgallery?search={self.gallery_name}", headers={"cookie": self.HDB_COOKIE})
        if not req.ok:
            logger.critical(
                f"Failed to get gallery id: HTTP {req.status_code}, reason: {req.reason}")
            raise RuntimeError()

        if req.json() == []:
            logger.info("No existing gallery")
            return None

        data = req.json()[0]
        if data.get("error"):
            logger.critical(
                f"Failed to get gallery id: Code {req.json()['error'].get('code')}, message: {req.json()['error]'].get('message')}"
            )
            raise RuntimeError()

        logger.debug(f"GetGalleryId:{data['id']}, {data['gn']}")
        return data["id"]

    """
    Part of code is from https://github.com/LeiShi1313/Differential/blob/main/differential/utils/image/hdbits.py
    """

    def upload_file(self, filename: str):
        gallery_option = 2 if self.exist_gallery_id else 1
        exist_gallery = self.exist_gallery_id if self.exist_gallery_id else 1
        gallery_name = self.gallery_name if self.gallery_name else self.hdb_upload_id
        data = {
            "name": filename,
            "thumbsize": "w300",
            "galleryoption": gallery_option,
            "galleryname": gallery_name,
            "existgallery": exist_gallery,
        }
        files = {
            "file": open(filename, "rb"),
        }
        req = requests.post(
            f"https://img.hdbits.org/upload.php?uploadid={self.hdb_upload_id}",
            data=data,
            files=files,
            headers=self.http_headers,
        )

        if not req.ok:
            logger.critical(
                f"Upload failed: HTTP {req.status_code}, reason: {req.reason}")
            raise RuntimeError()
        elif req.json().get("error"):
            logger.critical(
                f"Upload failed: Code {req.json()['error'].get('code')}, message: {req.json()['error]'].get('message')}"
            )
            raise RuntimeError()
        logger.info(
            f"HdbImg: {filename} was uploaded successfully to gallery {gallery_name}")

    def get_img_link(self, numImgs: int):
        req = requests.get(
            f"https://img.hdbits.org/done/{self.hdb_upload_id}", headers=self.http_headers)
        if not req.ok:
            logger.critical(
                f"Failed to get img link: HTTP {req.status_code}, reason: {req.reason}")
            raise RuntimeError()

        root = fromstring(req.content)
        textareas = root.xpath("*//textarea")
        if not textareas:
            logger.critical(f"Failed to get img link: {root}")
            raise RuntimeError()
        urls = textareas[1].text.split("\n")[-numImgs:]
        thumbs = textareas[2].text.split("\n")[-numImgs:]
        if len(urls) != len(thumbs):
            logging.critical(f"Failed to get img link: {root}")
            raise RuntimeError()

        thumbs = [thumb.replace("i.hdbits.org", "t.hdbits.org").replace(
            ".png", ".jpg") for thumb in thumbs]
        return urls, thumbs

    def Upload(self):
        self.http_headers = {
            "cookie": self.HDB_COOKIE,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29"
        }
        self.hdb_upload_id = self.get_hdb_uploadid()
        self.exist_gallery_id = self.get_hdb_exist_gallery_id()

        logger.debug(f"HdbImg upload_id {self.hdb_upload_id}")

        if self.isComparision:
            for Frame in self.FrameNums:
                for screen_type in self.screen_types:
                    filename = Frame+'-'+screen_type+f'.{self.img_type}'
                    self.upload_file(filename)

            urls, thumbs = self.get_img_link(
                len(self.screen_types)*len(self.FrameNums))
        else:
            for filename in self.file_list:
                self.upload_file(filename)

            urls, thumbs = self.get_img_link(len(self.file_list))

        return self.FormatImgLink(urls, thumbs)


class UpImageHDBAPI(UpImgBase):
    def __init__(
        self,
        file_list: List,
        upload_type: str = None,
        img_type: str = "png",
    ):
        UpImgBase.__init__(self, file_list, upload_type, img_type)

    def set_hdb_user_name(self, name):
        self.hdb_user_name = name

    def set_hdb_pass_key(self, key):
        self.hdb_pass_key = key

    def set_gallery_name(self, gallery_name):
        self.gallery_name = gallery_name if gallery_name is not None else "HdbImg_UP_" + \
            datetime.now().strftime("%Y%m%d_%H:%M:%S")

    def upload_files(self, Files: List[str]):
        data = {
            "username": self.hdb_user_name,
            "passkey": self.hdb_pass_key,
            "thumbsize": "w300",
            "galleryoption": 1,
            "galleryname": self.gallery_name,
            # "existgallery":1,  # no official API to find exist gallery id (try cookie based upload)
        }

        UpFiles = ((
            f"images_files[{index}]", (Files[index], open(Files[index], "rb"))
        ) for index in range(0, len(Files)))

        req = requests.post(
            f"https://img.hdbits.org/upload_api.php",
            data=data,
            files=UpFiles
        )

        if not req.ok:
            logger.critical(
                f"Upload failed: HTTP {req.status_code}, reason: {req.reason}")
            raise RuntimeError()

        if '[url=https:' not in req.text:
            logger.critical(
                f"Upload failed: {req.text}"
            )
            raise RuntimeError()

        urls = []
        thumbs = []
        for bbcode in req.text.split(' '):
            m = re.search('\[url=(.*)\]\[img\](.*)\[/img\]', bbcode)
            urls.append(m.groups(0)[0])
            thumbs.append(m.groups(0)[1])

        logger.info(
            f"HdbImg: {' '.join(Files)} were uploaded successfully to gallery {self.gallery_name}")
        return urls, thumbs

    def Upload(self):
        Files = []
        urls = []
        thumbs = []
        if self.isComparision:
            for Frame in self.FrameNums:
                for screen_type in self.screen_types:
                    filename = Frame+'-'+screen_type+f'.{self.img_type}'
                    Files.append(filename)
        else:
            for filename in self.file_list:
                Files.append(filename)

        urls, thumbs = self.upload_files(Files)
        return self.FormatImgLink(urls, thumbs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--site", help="site name(hdb,ptp,pter,np)",
                        required=True, nargs='*', default=['PTer'])
    parser.add_argument("-t", "--type", help="p:Preview(default) "
                        "c:Comparision(images must be named like FrameNum-Type.png, Type can be Source/Encode/Filtered/...)",
                        required=False, default='p')
    parser.add_argument("-i", "--imgtype", help="Imgtype(png/jpg)",
                        required=False, default='png')
    parser.add_argument("-f", "--tofile", help="Save BBCode to file",
                        action='store_true', default=False)
    parser.add_argument("-g", "--gallery", help="HDB/imgbox gallery name",
                        required=False, default=None)
    parser.add_argument("-d", "--debuglvl", help="debug level",
                        required=False, default="info")
    parser.add_argument("-c", "--cookiebased", help="HDBImg Cookie Based(Default OFF)",
                        required=False, action='store_true', default=False)

    args = parser.parse_args()

    if args.type not in ['p', 'c']:
        print("type should be either p(preview) or c(comparison)")
        exit(1)

    Log_level = {'info': logging.INFO, "debug": logging.DEBUG}
    logger.setLevel(Log_level[args.debuglvl])

    sites = [sitemapping[site]
             if site in sitemapping else site for site in args.site]

    Hosts = [ImageHost[site] for site in sites]
    Hosts = list(dict.fromkeys(Hosts))

    filenames = next(os.walk(os.getcwd()), (None, None, []))[2]
    Imgfiles = sorted(
        [file for file in filenames if file.endswith(f'.{args.imgtype}')])

    if Imgfiles == []:
        logger.critical(f"No {args.imgtype} files found at current directory")
        exit(0)

    logger.debug(Imgfiles)

    url = {}
    thumb = {}
    screen_types = {}

    ImageProcClasses = {
        "hdbimg": UpImageHDBAPI if args.cookiebased == False else UpImageHDBCookie,
        "ptpimg": UpImagePTP,
        "imgbox": UpImageImgbox,
    }

    for host in Hosts:
        imgUP = ImageProcClasses[host](Imgfiles, args.type, args.imgtype)

        if host == "hdbimg":
            if args.cookiebased:
                imgUP.set_hdb_cookie(HDB_COOKIE)
            else:
                imgUP.set_hdb_user_name(HDB_USER_NAME)
                imgUP.set_hdb_pass_key(HDB_PASS_KEY)

            imgUP.set_gallery_name(args.gallery)
        elif host == "ptpimg":
            imgUP.set_ptp_api_key(PTPIMG_APIKEY)
        elif host == "imgbox":
            imgUP.set_gallery_name(args.gallery)

        url[host], thumb[host], screen_types[host] = imgUP.Upload()

    for site in sites:
        host = ImageHost[site]
        BBCodeGen(site, args.type, url[host],
                  thumb[host], screen_types[host], args.tofile).MakeBBCode()
