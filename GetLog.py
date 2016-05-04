#coding=UTF-8
import subprocess,os,time,ftpRun,Unzip,thread
from optparse import OptionParser

anrFile = None
fileName = None
# package = ''
def getLog(fileName):
    # global package
    name = ''
    package = ''
    crashPackage = ''
    pullANR = False
    popen = subprocess.Popen("adb logcat -v time", stdout = subprocess.PIPE,shell=True)
    returncode = popen.poll()

    versionsLog = os.path.join(os.getcwd(),'ErrorLog',fileName)
    if os.path.exists(versionsLog) != True:
        os.makedirs(versionsLog)

    i = 200
    while returncode  is None:
        log = popen.stdout.readline()
        a = "FATAL EXCEPTION" in log
        b = "ANR in" in log
        if a or b:
            if a:
                name = 'Crash'
                print name
            else:
                name = 'ANR'
                print name
                pullANR = True
                #获取ANR报错包名
                print '获取包名'
                # logSplit = log.split('ANR in')
                # get = logSplit[-1].strip().split(' ')
                # package = get[0].strip()
                # print package
                try:
                    logSplit = log.split('ANR in')
                    get = logSplit[-1].strip().split(' ')
                    package = get[0].strip()+'_'
                    print '包名：'+package
                except:
                    package = 'none_'


            time = getTime('%Y%m%d-%H%M%S')
            print "报错"
            i = 0
            print '报错类型'+name
            logName = name+time
            errorFile = os.path.join(versionsLog,logName)
            if os.path.exists(errorFile) != True:
                os.mkdir(errorFile)
            writeLog = open(os.path.join(errorFile,'logcat.log'),'a')
        #获取crash报错包名
        # print a
        if name == 'Crash'and i==1:
            print '获取包名'
            if 'Process:' in log:
                logSplit = log.split('Process:')
                get = logSplit[-1].strip().split(',')
                crashPackage = get[0].strip()+'_'
                print '包名：'+crashPackage
            else:
                crashPackage = 'none_'
                print '包名：'+crashPackage

            # try:
            #     logSplit = log.split('Process:')
            #     get = logSplit[-1].strip().split(',')
            #     package = get[0].strip()
            # except:
            #     package = 'none'

        if i<200:
            writeLog.write(log)
            writeLog.flush()     
            i+=1
            if i == 200 and pullANR:
                print "anr"
                anrFile = os.path.join(errorFile,'ANR')
                if os.path.exists(anrFile) != True:
                    os.mkdir(anrFile)
                newlogName = package+logName
                thread.start_new_thread(pullAnrLog,(anrFile,fileName,logName,newlogName)) #运行导出anr日志并上传log

                pullANR = False
            elif i == 200:
                # package
                # print "package:"+package
                print "crash"
                newlogName = crashPackage+logName
                thread.start_new_thread(pullLog,(fileName,logName,newlogName)) #上传log
        returncode = popen.poll()

def getTime(timeFormat):
    timestamp = time.strftime(timeFormat,time.localtime(time.time()))
    return timestamp

#导出ANR日志并上传log
def pullAnrLog(anrFile,fileName,logName,newLogName):
    print '上传log'
    os.popen('adb pull '+'data/anr '+anrFile)
    Unzip.zip_dir(fileName,logName,newLogName) #压缩日志
    ftpRun.uploadfile(fileName,newLogName) #上传日志
    thread.exit_thread()

#上传log
def pullLog(fileName,logName,newLogName):
    print '上传log'
    Unzip.zip_dir(fileName,logName,newLogName) #压缩日志
    ftpRun.uploadfile(fileName,newLogName) #上传日志
    thread.exit_thread()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', dest='fileName')
    (options, args) = parser.parse_args()
    fileName = options.fileName.strip()#手机版本和日期的文件名
    print fileName
    # fileName = 'sp7731geaplus_dt-D-v0.04.66_20160427'
    getLog(fileName)
