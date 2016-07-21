#coding=UTF-8
import ftpRun,os,sendMail,MailRecipients,sys,time,platform,GetLog,subprocess,startApp

if platform.system() == 'Windows':
    seek = 'findstr'
else:
    seek = 'grep'

def pushVersions():
    #下载OTA包
    OTA = ftpRun.ota()
    otaVersionsPath = 'ota包下载地址：ftp://FTP_Talpa:talpaftp@10.250.1.88/work/Doc_For_OSTeam/Doc_For_OSTeam/simg2img/out_ota/w3_60_debug/'+OTA
    #判断是否连接上设备
    run = wait_for_device(30)
    if run == 'false':
        print '刷机前手机连接超时，程序终止'
        #发邮件提示tester，未识别到手机，检查测试环境
        sendMail.send(MailRecipients.tester_list,u"升级异常","hi all:"+"\n"+"    "+"版本"+OTA+"在升级版本前未识别到手机，请检查手机是否已连接，或PC测试环境是否有问题！")
        sys.exit(0)
    else:
        print '手机已连接'
    
    #push包到手机内存
    print '正push文件'
    os.popen("adb push "+os.path.join(os.getcwd(),'versions',OTA)+" sdcard/")
    print "adb push "+os.path.join(os.getcwd(),'versions',OTA)+" sdcard/"
    print 'push结束'
    
    #判断手机中是否含有ota包
    cmd = os.popen('adb shell ls sdcard/').read()
    print cmd
    if OTA in cmd:
        print '手机中已有ota包'
        # # 本地调试路径;
        # os.system('adb install -r '+os.path.join(os.getcwd(),'app','OTAtest1.apk'))
        # os.system('adb install -r '+os.path.join(os.getcwd(),'app','OTAtest2.apk'))
        # 傻逼Linux服务器本地路径;
        os.system('adb install -r /home/zf/桌面/app/OTAtest1.apk')
        os.system('adb install -r /home/zf/桌面/app/OTAtest2.apk')
        os.system('adb shell am start -n tran.com.android.taplaota/.activity.OtaActivity')
        time.sleep(5)
        os.system('adb shell am instrument -w -r -e debug false -e class com.talpa.ota.ApplicationTest#otaTest com.talpa.ota.test/android.support.test.runner.AndroidJUnitRunner')
        time.sleep(30)

        #判断是否连接上设备
        run = wait_for_device(15)
        if run == 'false':
            print '手机连接超时，发送邮件通知并程序终止'
            #发送邮件通知手机无法进入系统
            sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机失败","hi all:"+"\n"+"    "+"版本"+OTA+"刷机后无法进入系统或无法识别设备！"+"\n"+"    "
                      +otaVersionsPath)
            sys.exit(0) #终止程序
        else:
            print '手机已连接'
            
         #判断是否进入Launcher
        launcher(OTA,otaVersionsPath)
        
        #判断屏幕是否锁屏
        for i in range(5):
            time.sleep(1)
            lockScreen = os.popen('adb shell dumpsys power | '+seek+' mWakefulness=').readline()
            if 'Asleep' in lockScreen:
                print '手机锁屏'
                os.popen('adb shell input keyevent POWER') #点亮屏幕
            else:
                break
            
        #测试启动所有应用
        #判断手机是否进入开机后的设置界面
        times = 0
        while True:
            cmd = os.popen('adb shell dumpsys activity top | '+seek+' ACTIVITY').readline()
            if 'com.android.settings' not in cmd:
                print '未进入到开机后的设置界面'
                os.popen('adb shell am start com.android.settings')
                time.sleep(15)
            else:
                print '手机进入系统界面'
                break
            if times == 40:
                print '系统长时间未进入开机后的设置界面'
                #发送邮件通知手机无法正常进入开机后界面
                sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机失败","hi all:"+"\n"+"    "+"版本"+OTA+"刷机后无法进入系统！"+"\n"+"    "
                          +otaVersionsPath)
                sys.exit(0)
            times += 1    
            
        #获取手机版本
        build = os.popen('adb shell getprop ro.build.display.id').readline()
        fileTime = GetLog.getTime('%Y%m%d') 
        fileName = build.strip()+'_'+fileTime  #FTP上的版本目录名称
        print '版本文件名：'+ fileName
        if  fileTime in build:
            print '已刷入当天版本'
            os.system('adb shell rm /sdcard/*.zip')
            time.sleep(2)
            os.system('adb shell input keyevent 4')
        else:
            print '刷机后不是当天版本'
            sendMail.send(MailRecipients.tester_list,u"版本刷机报告-刷机失败","hi all:"+"\n"+"    "+"版本"+OTA+"刷机后检测到版本号不是当天的版本！"+"\n"+"    "
                          +otaVersionsPath)
            sys.exit(0)
        
        #开启log抓取
        # child = subprocess.Popen('python '+os.path.join(os.getcwd(),'GetLog.py')+' -p '+ fileName,shell=True)
        child = subprocess.Popen('python /var/lib/jenkins/workspace/SmokeProject/GetLog.py -p '+ fileName,shell=True)
        print '开启抓log'    
        
        #运行启动程序
        startApp.test()
        
        #关闭log抓取
        subprocess.Popen("taskkill /F /T /PID %i"%child.pid , shell=True)
        print '关闭抓log'    
        
        
        #结束后发邮件
        if os.path.exists(os.path.join(os.getcwd(),'ErrorLog',fileName)):
            files = os.listdir(os.path.join(os.getcwd(),'ErrorLog',fileName))
            print files
            errorsFile = len(files)
            errorsNumber = 0
            if errorsFile == 0:
                print '没有报错文件'
                sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机成功","hi all:"+"\n"+"    "+"版本"+OTA+"刷机成功！所有应用启动正常。"+"\n"+"    "
                          +otaVersionsPath)
                if OTA != 'false':
                    createOtaFile(OTA)
                    ftpRun.uploadOtaFile()
            else:
                errorPath = ''
                for i in files:
                    if '.zip' in i:
                        errorsNumber += 1
                        packageName = i.split('_')[0]
                        if packageName == 'none':
                            errorPath += '应用报错' +'\n'+'ftp://FTP_Talpa:talpaftp@10.250.1.88/Log/'+fileName+'/'+i+'\n'
                        else:
                            errorPath += '应用'+packageName+'报错' +'\n'+'ftp://FTP_Talpa:talpaftp@10.250.1.88/Log/'+fileName+'/'+i+'\n'
                print '有报错文件'
                sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机成功","hi all:"+"\n"+"    "+"版本"+OTA+"刷机成功！启动所有应用过程共出现"+str(errorsNumber)+"次报错。"+"\n"+"    "
                          +otaVersionsPath+"\n"+"对应应用报错log地址如下："+"\n"+errorPath)

        else:
            print '没有报错文件'
            sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机成功","hi all:"+"\n"+"    "+"版本"+OTA+"刷机成功！所有应用启动正常。"+"\n"+"    "
                      +otaVersionsPath)
            if OTA != 'false':
                createOtaFile(OTA)
                ftpRun.uploadOtaFile()
        
    else:
        print '无ota包'
      
#创建ota日志文件
def createOtaFile(otaFileName):
    fileName = os.path.join(os.getcwd(),'test.txt')
    file = open(fileName, 'w')
    file.write(otaFileName)

def launcher(VersionsName,otaVersionsPath):
    #判断是否进入第二屏
    for i in range(30):
        cmd = os.popen('adb shell dumpsys activity top | '+seek+' ACTIVITY').readline()
        if cmd != None:
            print '手机进入第二屏'
            login = True
            break;
        else:
            login = False
            time.sleep(5)
    if not login:
        print '手机无法进入第二屏'
        #发送邮件通知手机无法正常开启
        sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机失败","hi all:"+"\n"+"    "+"版本"+VersionsName+"刷机后无法进入系统！"+"\n"+"    "
                      +otaVersionsPath)
        sys.exit(0)

    #判断是否运行launcher
    for i in range(30):
        cmd = os.popen('adb shell dumpsys activity top | '+seek+' ACTIVITY').readline()
        pid = cmd.strip().split(' ')[-1].strip()
        print pid
        if 'not running' in pid:
            lcRun = False
            time.sleep(5)
        else:
            print 'launcher已启动'
            lcRun = True
            time.sleep(10)
            break
    if not lcRun:
        print 'launcher未运行'
        #发送邮件通知手机无法正常运行launcher
        sendMail.send(MailRecipients.mailto_list,u"版本刷机报告-刷机失败","hi all:"+"\n"+"    "+"版本"+VersionsName+"刷机后无法进入系统！"+"\n"+"    "
                      +otaVersionsPath)
        sys.exit(0)
  
#升级ota包
def otaUpdate(): 
    #等待手机连接
    wait_for_device(30)
    #获取手机分辨率
    xy = os.popen('adb shell wm size').readline()
    xy = xy.split(':')[1].strip()
    x = xy.split('x')[0].strip()
    y = xy.split('x')[1].strip()
    print x
    print y
    

#等待连接设备
def wait_for_device(times): 
    for i in range(times):
        cmd = os.popen('adb get-state').readline()
        if cmd.strip() == 'device': 
            run = 'turn'
            break
        else:
            print '未识别'
            #os.popen('adb kill-server')
            time.sleep(60)
            #os.popen('adb start-server')
            run = 'false'
    return run

if __name__ == '__main__':
    pushVersions()