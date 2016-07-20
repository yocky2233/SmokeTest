#coding=UTF-8
from ftplib import FTP
import  sys,os,shutil,GetLog,sendMail,MailRecipients

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
    ftp.cwd("/work/Doc_For_OSTeam/Doc_For_OSTeam/simg2img/out_ota/w3_60_debug")
    
#     remotepath = ['boot.img','recovery.img','system.img']
    print ftp.getwelcome() #显示ftp服务器欢迎信息
    bufsize = 1024 #设置缓冲块大小

    print '下载文件'+versionsName
    localpath = os.path.join(file,versionsName)
    fp = open(localpath,'wb') #以写模式在本地打开文件
    ftp.retrbinary('RETR ' + versionsName,fp.write,bufsize) #接收服务器上文件并写入本地文件
    #ftp.set_debuglevel(0) #关闭调试
    fp.close()
    ftp.quit() #退出ftp服务器
    print '下载结束'

#上传报错日志文件到FTP
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
    
#上传ota日志文件到FTP
def uploadOtaFile():
    ftp = ftpconnect()
    ftp.cwd('otaLog')
    bufsize = 1024
    localpath = os.path.join(os.getcwd(),'test.txt') #设定上传文件位置
    fp = open(localpath,'rb')
    ftp.storbinary('STOR %s' % os.path.basename(localpath),fp,bufsize) #上传文件
    # ftp.set_debuglevel(0)
    fp.close() #关闭文件
    ftp.quit()
    
#删除ftp上文件
def deleteFile(fileName,dirname):
    ftp = ftpconnect()
    
    ftp.cwd(fileName)#要删除文件的ftp目录
    
    file = ftp.nlst()
    print file
    if file == []:
        print '无otaLog文件'
    else:
        print '有otaLog文件'
        ftp.delete(dirname) #删除远程目录


#判断是否有ota包
def ota():
    ftp = ftpconnect()
    ftp.cwd("/work/Doc_For_OSTeam/Doc_For_OSTeam/simg2img/out_ota/w3_60_debug")
    fileList = []
    
    time = GetLog.getTime('%Y%m%d')
    print '当前日期'+time
    
    getOta = 'false'
    time = time[2:]
    print time
    for i in ftp.nlst():
        if 'zip' in i and len(i)>18:
            fileList.append(i)
            otaName = i.split('.')
            if time in i:
                getOta = i
                break
    print 'ota包名'+getOta
    
    #没有ota包发送邮件
    if getOta == 'false':
        #发送邮件通知
        sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-无刷机版本","hi all:"+"\n"+"    "+time+"无刷机版本！请负责版本编译的开发同学关注。")
        sys.exit(0) #终止程序
    
    #下载ota包
    downloadfile(getOta)
    return getOta
    


if __name__ == "__main__":
    # a = os.path.join(os.getcwd(),'ErrorLog','abc','test.py')
    # a = 'd:/boot.img'
    # uploadfile(a)
    # test()
    ota()
