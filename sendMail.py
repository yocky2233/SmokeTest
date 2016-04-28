# -*- coding: UTF-8
import smtplib
from email.mime.text import MIMEText

mail_host="smtp.qiye.163.com"  #设置服务器
mail_user="zhongfu.zheng@itel-mobile.com"    #用户名
mail_pass="zheng@853"   #口令
mail_postfix="itel-mobile.com"  #发件箱的后缀

def mail(to_list,sub,content):  #to_list：收件人；sub：主题；content：邮件内容
    me="tester"+"<"+mail_user+"@"+mail_postfix+">"  #这里的tester可以任意设置，收到信后，将按照设置显示

    msg = MIMEText(content,_subtype='plain',_charset='utf-8')  #创建一个实例，这里设置为普通txt邮件，指定为utf-8编码
    msg['Subject'] = sub  #设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    msg["Accept-Language"]="zh-CN"  #这两个为邮件内容中文显示相关设置
    msg["Accept-Charset"]="ISO-8859-1,utf-8"

    try:
        server = smtplib.SMTP()
        server.connect(mail_host)  #连接smtp服务器
        server.login(mail_user,mail_pass)  #登陆服务器
        server.sendmail(me, to_list, msg.as_string())  #发送邮件
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

def send(mailto_list,title,content):
    if mail(mailto_list,title,content):
        print "邮件发送成功"
    else:
        print "邮件发送失败"

if __name__ == '__main__':
    # send("版本升级报告","hi all:"+"\n"+"    "+"版本升级正常")
    mailto_list=['471410616@qq.com']
    send(mailto_list,"版本异常报告","hi all:"+"\n"+"    "+"版本号"+" imgs-16-04-28-02-59 "+"刷机后无法进入系统！")

