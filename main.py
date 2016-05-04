#coding=UTF-8
import ftpRun,os,time,sys,subprocess,GetLog,platform,startApp,sendMail

if platform.system() == 'Windows':
    seek = 'findstr'
else:
    seek = 'grep'

mailto_list = ['zhongfu.zheng@itel-mobile.com',
               'jianhua.li@itel-mobile.com',
               'lei.dai@itel-mobile.com',
               'chongyi.pu@itel-mobile.com']
tester_list = ['zhongfu.zheng@itel-mobile.com',
               'jianhua.li@itel-mobile.com',
               'lei.dai@itel-mobile.com']

def upgrade():
    #下载版本
    Versions = ftpRun.downloadVersions()

    #判断是否连接上设备
    run = wait_for_device()
    if run == 'false':
        print '刷机前手机连接超时，程序终止'
        #发邮件提示tester，未识别到手机，检查测试环境
        sendMail.send(tester_list,u"升级异常","hi all:"+"\n"+"    "+"版本"+Versions+"在升级版本前未识别到手机，请检查手机是否已连接，或PC测试环境是否有问题！")
        sys.exit(0)
    else:
        print '手机已连接'

    #刷版本
    os.popen('adb reboot bootloader')
    time.sleep(5)
    os.popen('fastboot flash boot '+os.path.join(os.getcwd(),'versions','boot.img'))
    os.popen('fastboot flash recovery  '+os.path.join(os.getcwd(),'versions','recovery .img'))
    os.popen('fastboot flash system '+os.path.join(os.getcwd(),'versions','system.img'))
    os.popen('fastboot reboot')
    print '升级完毕'

    #判断是否连接上设备
    run = wait_for_device()
    if run == 'false':
        print '手机连接超时，发送邮件通知并程序终止'
        #发送邮件通知手机无法进入系统
        sendMail.send(mailto_list,u"版本异常报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机后无法进入系统或无法识别设备！")
        sys.exit(0) #终止程序
    else:
        print '手机已连接'

    #判断是否进入Launcher
    launcher(Versions)

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
            time.sleep(5)
        else:
            print '手机进入系统界面'
            break
        if times == 40:
            print '系统长时间未进入开机后的设置界面'
            #发送邮件通知手机无法正常进入开机后界面
            sendMail.send(mailto_list,u"版本异常报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机后无法进入系统！")
            sys.exit(0)
        times += 1
    
        
    #获取手机版本
    build = os.popen('adb shell getprop ro.build.description').readline()
    fileTime = GetLog.getTime('%Y%m%d')
    fileName = build.strip()+'_'+fileTime  #FTP上的版本目录名称
    print '版本文件名：'+ fileName

    #开启log抓取
    #child = subprocess.Popen('python '+os.path.join(os.getcwd(),'GetLog.py')+' -p '+ fileName,shell=True)
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
            sendMail.send(mailto_list,u"版本刷机报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机成功！启动所有应用过程未出现报错。")
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
            sendMail.send(mailto_list,u"版本刷机报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机成功！启动所有应用过程共出现"+str(errorsNumber)+"次报错。"+"\n"+"对应应用报错log地址如下："+"\n"+errorPath)

    else:
        print '没有报错文件'
        sendMail.send(mailto_list,u"版本刷机报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机成功！启动所有应用过程未出现报错。")




def launcher(Versions):
    #判断是否进入第二屏
    for i in range(5):
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
        sendMail.send(mailto_list,u"版本异常报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机后无法进入系统！")
        sys.exit(0)

    #判断是否运行launcher
    for i in range(5):
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
        sendMail.send(mailto_list,u"版本异常报告","hi all:"+"\n"+"    "+"版本"+Versions+"刷机后无法进入系统！")
        sys.exit(0)


#等待连接设备
def wait_for_device():
    for i in range(20):
        cmd = os.popen('adb get-state').readline()
        if cmd.strip() == 'device': 
            run = 'turn'
            break
        else:
            print '未识别'
            #os.popen('adb kill-server')
            time.sleep(5)
            #os.popen('adb start-server')
            run = 'false'
    return run

if __name__ == '__main__':
    upgrade()