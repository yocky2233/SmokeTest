#coding=UTF-8
import os,time,platform,sendMail

if platform.system() == 'Windows':
    seek = 'findstr'
else:
    seek = 'grep'

def test():
    appPackage = ['com.android.settings',
                  'com.android.browser',
                  'com.android.calculator2',
                  'com.android.calendar',
                  'com.android.camera2',
                  'com.android.deskclock',
                  'com.android.contacts',
                  'com.android.email',
                  'com.sprd.fileexplorer',
                  'com.thunderst.radio',
                  'com.android.gallery3d',
                  'com.google.android.gm',
                  'com.google.android.gms',
                  'com.android.dialer',
                  'com.android.mms',
                  'com.android.music',
                  'com.sprd.note',
                  'com.android.dialer',
                  'com.android.vending',
                  'com.android.quicksearchbox',
                  'com.android.soundrecorder']
    
    for i in appPackage:
        os.popen('adb shell monkey -p '+i+' 1')
        # print 'adb shell monkey -p '+i+' 1'
        time.sleep(5)
        cmd = os.popen('adb shell dumpsys activity top | '+seek+' ACTIVITY').readline()
        if i not in cmd:
            str += i+'未启动成功，也可能是谷歌应用跳转到登陆界面'+'\n'
            print i+'未启动成功，也可能是谷歌应用跳转到登陆界面'
    
    mailto_list = ['471410616@qq.com']
    sendMail.send(mailto_list,"未启动的应用","hi all:"+"\n"+"    本次测试疑似未启动的应用有："+"\n"+str)


if __name__ == '__main__':
    test()
