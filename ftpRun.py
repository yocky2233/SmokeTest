#coding=UTF-8
from ftplib import FTP
import  sys,os,shutil,GetLog,sendMail

#连接FTP
def ftpconnect():
    ftp_server = '10.250.1.88'
    username = 'FTP_Talpa'
    password = 'talpaftp'
    ftp=FTP()
    #ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
    ftp.connect(ftp_server,21) #连接
    ftp.login(username,password) #登录，如果匿名登录则用空串代替即可
    return ftp

#从FTP下载文件
def downloadfile(versionsName):
    file = os.path.join(os.getcwd(),'versions')
    if not os.path.exists(file):
        print '新建文件'
        os.mkdir(file)
    else:
        shutil.rmtree(file)
        os.mkdir(file)

    ftp = ftpconnect()
    ftp.cwd("/work/Doc_For_OSTeam/Doc_For_OSTeam/RecoveryPackage/"+versionsName)
    remotepath = ['boot.img','recovery.img','system.img']
    print ftp.getwelcome() #显示ftp服务器欢迎信息
    bufsize = 1024 #设置缓冲块大小
    for i in remotepath:
        localpath = os.path.join(file,i)
        fp = open(localpath,'wb') #以写模式在本地打开文件
        ftp.retrbinary('RETR ' + i,fp.write,bufsize) #接收服务器上文件并写入本地文件
    #ftp.set_debuglevel(0) #关闭调试
    fp.close()
    ftp.quit() #退出ftp服务器
    print '下载结束'

#上传文件到FTP
def uploadfile(fileName,newLogName):
    make = True
    # remotepath = os.path.join('Log')
    # remotepath = 'Log'
    # print remotepath
    ftp = ftpconnect()

    ftp.cwd('Log')
    for i in ftp.nlst():
        print '文件名：'+i
        if fileName == i:
            make = False
            break
    if make:
        print 'Log/'+fileName
        ftp.mkd(fileName)

    ftp.cwd(fileName)
    bufsize = 1024
    localpath = os.path.join(os.getcwd(),'ErrorLog',fileName,newLogName+'.zip') #设定上传文件位置
    # localpath = fileName  #设定上传文件位置
    fp = open(localpath,'rb')
    ftp.storbinary('STOR %s' % os.path.basename(localpath),fp,bufsize) #上传文件
    # ftp.set_debuglevel(0)
    fp.close() #关闭文件
    ftp.quit()

#下载FTP文件
def downloadVersions():
    ftp = ftpconnect()
    ftp.cwd("/work/Doc_For_OSTeam/Doc_For_OSTeam/RecoveryPackage")
    fileList = []
    for i in ftp.nlst():
        if 'imgs' in i and len(i)>18:
            fileList.append(i)
    print fileList
    time = GetLog.getTime('%Y%m%d')
    print '当前日期'+time

    fileName = fileList[-1].split('-')
    fileTime = '20'+fileName[1]+fileName[2]+fileName[3]
    print fileName
    print fileTime

    if fileTime!=time:
        print '没有今天的版本'
        #发送邮件通知
        mailto_list = ['zhongfu.zheng@itel-mobile.com',
                       'jianhua.li@itel-mobile.com',
                       'lei.dai@itel-mobile.com',
                       'chongyi.pu@itel-mobile.com']
        sendMail.send(mailto_list,u"版本异常报告","hi all:"+"\n"+"    "+time+"无刷机版本！")
        sys.exit(0) #终止程序
    else:
        downloadfile(fileList[-1])
    return fileList[-1]


if __name__ == "__main__":
    # a = os.path.join(os.getcwd(),'ErrorLog','abc','test.py')
    # a = 'd:/boot.img'
    # uploadfile(a)
    # test()
    # downloadfile()
    downloadVersions()
