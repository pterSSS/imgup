# imgup
压制对比图/一般截图, 上传图床，生成bbcode工具  
 
图床支持ptpimg/hdbimg/imgbox  
站点支持hdb,ptp,pter,np(nexusphp架构),mtv,bhd  
站点和使用图床的对应关系如下  
   HDB: hdbimg  
   PTP/MTV: ptpimg  
   pter/np/bhd: imgbox     
使用同一图床的多个站点，只上传一次  

使用说明  
1. 安装python3 下面的说明为windows平台(Linux平台也测试通过)  

2. 修改imgup.py，在文件最前面填入自己的HDB username/passkey, PTPimg API key。注意不要泄露带有key的文件。  
   HDB_COOKIE 如果不使用cookie上传方式可以不填（cookie方式可支持多次上传截图到同一gallery)   

3. 复制imgup.py 到python3安装目录下的Lib, 例如c:\python39\Lib  

4. 把requirements.txt放到某个目录下,比如E:\imgup，运行命令安装依赖库  
   (需要管理权限进入命令行) 

    E:\imgup>**pip install -r requirements.txt**  

5. 在截图目录下运行脚本，脚本会寻找当前目录的png/jpg文件。  

   对比图要求文件名为{帧号}-Source.png，{帧号}-Filtered.png,{帧号}-Encode.png, {帧号}-GroupA.png 等  
   一般预览截图没有文件名要求，任意png/jpg即可

6. 测试命令是否正常运行  

E:\imgup>**python -m imgup -h**  
usage: imgup.py [-h] -s [SITE ...] [-t TYPE] [-i IMGTYPE] [-f] [-g GALLERY] [-d DEBUGLVL] [-c]  

optional arguments:  
  -h, --help            show this help message and exit  
  -s [SITE ...], --site [SITE ...]
                        site name(hdb,ptp,pter,np)  
  -t TYPE, --type TYPE  p:Preview(default) c:Comparision(images must be named like FrameNum-Type.png, Type can be
                        Source/Encode/Filtered/...)  
  -i IMGTYPE, --imgtype IMGTYPE
                        Imgtype(png/jpg)  
  -f, --tofile          Save BBCode to file  
  -g GALLERY, --gallery GALLERY
                        HDB/imgbox gallery name  
  -d DEBUGLVL, --debuglvl DEBUGLVL
                        debug level  
  -c, --cookiebased     HDBImg Cookie Based(Default OFF)  

参数说明:   
   -s 可指定单个或多个需要传截图，生成bbcode的站点  
   -t p(一般预览图)  c(对比图,需要按照上面的格式命名) 可省略，默认为一般预览图  
   -i png或jpg，可省略，默认png   
   -f 是否输出bbcode到文本文件，可省略，默认为否  
   -g hdbimg或imgbox 的gallery名，可省略，使用自动生成的名字   
   -d 指定info 或debug, 可省略，默认为info   
   -c HDBImg cookie 方式上传，可省略，默认关闭 (仅需要多次上传到同一gallery时使用, 修改imgup.py填写HDB_COOKIE)  


目前HDB/BHD的一般预览图会生成两个图摆一排的bbcode, 可以修改代码MakeBBCodeBHD/MakeBBCodeHDB   
max_preview_img_per_row=2改成想要的值  

对比图上传例子:  
E:\imgup>**python -m imgup -s hdb bhd pter ptp mtv np -t c -f -g test**  
HdbImg: 10415-Source.png 10415-Encode.png 11894-Source.png 11894-Encode.png 109685-Source.png 109685-Encode.png were uploaded successfully to gallery test  
ImgBox: 10415-Source.png was uploaded successfully to gallery test  
ImgBox: 10415-Encode.png was uploaded successfully to gallery test  
ImgBox: 11894-Source.png was uploaded successfully to gallery test  
ImgBox: 11894-Encode.png was uploaded successfully to gallery test  
ImgBox: 109685-Source.png was uploaded successfully to gallery test  
ImgBox: 109685-Encode.png was uploaded successfully to gallery test  
PTPImg: 10415-Source.png was uploaded successfully.  
PTPImg: 10415-Encode.png was uploaded successfully.  
PTPImg: 11894-Source.png was uploaded successfully.  
PTPImg: 11894-Encode.png was uploaded successfully.  
PTPImg: 109685-Source.png was uploaded successfully.  
PTPImg: 109685-Encode.png was uploaded successfully.  

HDB BBCODE:  
[center][size=4][b][color=Blue]Source Vs Encode[/color][/b][/size]  
[url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url] [url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url]  

[url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url] [url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url]  

[url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url] [url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url]  

[/center]  



BHD BBCODE:   
[comparison=Source,Encode]  
[img]https://images2.imgbox.com/86/da/XXXXX.png[/img]  
[img]https://images2.imgbox.com/ba/c8/XXXXX.png[/img]  
  
[img]https://images2.imgbox.com/44/95/XXXXX.png[/img]  
[img]https://images2.imgbox.com/39/67/XXXXX.png[/img]  

[img]https://images2.imgbox.com/80/a2/XXXXX.png[/img]    
[img]https://images2.imgbox.com/41/e2/XXXXX.png[/img]    

[/comparison]  



PTer BBCODE:  
[center][size=4][b][color=Blue]Source Vs Encode[/color][/b][/size]  
[url=https://images2.imgbox.com/86/da/XXXXX.png][img2]https://thumbs2.imgbox.com/86/da/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/ba/c8/XXXXX.png][img2]https://thumbs2.imgbox.com/ba/c8/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/44/95/XXXXX.png][img2]https://thumbs2.imgbox.com/44/95/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/39/67/XXXXX.png][img2]https://thumbs2.imgbox.com/39/67/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/80/a2/XXXXX.png][img2]https://thumbs2.imgbox.com/80/a2/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/41/e2/XXXXX.png][img2]https://thumbs2.imgbox.com/41/e2/XXXXX.png[/img][/url]  
[/center]  



PTP BBCODE:  
[comparison=Source,Encode]  
https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

[/comparison]  



MTV BBCODE:  
[comparison=Source,Encode]  
https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

https://ptpimg.me/XXXXX.png  
https://ptpimg.me/XXXXX.png  

[/comparison]  



NP BBCODE:    
[center][size=4][b][color=Blue]Source Vs Encode[/color][/b][/size]  
[url=https://images2.imgbox.com/86/da/XXXXX.png][img]https://thumbs2.imgbox.com/86/da/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/ba/c8/XXXXX.png][img]https://thumbs2.imgbox.com/ba/c8/XXXXX.png[/img][/url]  

[url=https://images2.imgbox.com/44/95/XXXXX.png][img]https://thumbs2.imgbox.com/44/95/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/39/67/XXXXX.png][img]https://thumbs2.imgbox.com/39/67/XXXXX.png[/img][/url]  

[url=https://images2.imgbox.com/80/a2/XXXXX.png][img]https://thumbs2.imgbox.com/80/a2/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/41/e2/XXXXX.png][img]https://thumbs2.imgbox.com/41/e2/XXXXX.png[/img][/url]  

[/center]  


一般预览图:     
E:\imgup>**python -m imgup -s hdb bhd pter ptp mtv np -f -g test**  
HdbImg: 12313-Preview.png 13729-Preview.png 140688-Preview.png were uploaded successfully to gallery test  
ImgBox: 12313-Preview.png was uploaded successfully to gallery test  
ImgBox: 13729-Preview.png was uploaded successfully to gallery test  
ImgBox: 140688-Preview.png was uploaded successfully to gallery test  
PTPImg: 12313-Preview.png was uploaded successfully.  
PTPImg: 13729-Preview.png was uploaded successfully.  
PTPImg: 140688-Preview.png was uploaded successfully.  
  
HDB BBCODE:  
[center][size=4][b][color=Blue]Preview[/color][/b][/size]  
[url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url] [url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url]  
[url=https://img.hdbits.org/XXXXX][img]https://t..hdbits.org/XXXXX.jpg[/img][/url]    
[/center]  



BHD BBCODE:  
[url=https://images2.imgbox.com/47/f0/XXXXX.png][img]https://thumbs2.imgbox.com/47/f0/XXXXX.png[/img][/url] [url=https://images2.imgbox.com/72/cc/XXXXX.png][img]https://thumbs2.imgbox.com/72/cc/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/96/96/XXXXX.png][img]https://thumbs2.imgbox.com/96/96/XXXXX.png[/img][/url]  



PTer BBCODE:  
[center][size=4][b][color=Blue]Preview[/color][/b][/size]  
[url=https://images2.imgbox.com/47/f0/XXXXX.png][img]https://thumbs2.imgbox.com/47/f0/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/72/cc/XXXXX.png][img]https://thumbs2.imgbox.com/72/cc/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/96/96/XXXXX.png][img]https://thumbs2.imgbox.com/96/96/XXXXX.png[/img][/url]    
[/center]  



PTP BBCODE:  
[img]https://ptpimg.me/XXXXX.png[/img]  
[img]https://ptpimg.me/XXXXX.png[/img]    
[img]https://ptpimg.me/XXXXX.png[/img]  



MTV BBCODE:  
[img]https://ptpimg.me/XXXXX.png[/img]  
[img]https://ptpimg.me/XXXXX.png[/img]  
[img]https://ptpimg.me/XXXXX.png[/img]  



NP BBCODE:  
[center][size=4][b][color=Blue]Preview[/color][/b][/size]  
[url=https://images2.imgbox.com/47/f0/XXXXX.png][img]https://thumbs2.imgbox.com/47/f0/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/72/cc/XXXXX.png][img]https://thumbs2.imgbox.com/72/cc/XXXXX.png[/img][/url]  
[url=https://images2.imgbox.com/96/96/XXXXX.png][img]https://thumbs2.imgbox.com/96/96/XXXXX.png[/img][/url]  
[/center]    

ptpimg, hdbimg cookie部分代码参考了梅西大佬的差速器https://github.com/LeiShi1313 (感谢)

