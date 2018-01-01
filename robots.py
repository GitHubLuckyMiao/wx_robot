# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#coding:utf8
import requests
from itchat.content import *
import itchat
import os
import re
import shutil
import time
import random
global gifKey
global run
run=True
gifKey=False
KEY = '8edce3ce905a4c1dbb965e6b35c3834d'
msg_dict = {}



def groupNameIsOK(name,msg):
    str=u'大家记得下午准时过去观看java部落软件设计大赛哟~'
    if re.search(r"\d\d(\-|\-|)\S*(\-|\-|)\S*",name)==None:
        msg.user.send(u'@%s\u2005%s' % (msg.actualNickName, str))

#ClearTimeOutMsg用于清理消息字典，把超时消息清理掉
#为减少资源占用，此函数只在有新消息动态时调用



def ClearTimeOutMsg():
    if msg_dict.__len__() > 0:
        for msgid in list(msg_dict): #由于字典在遍历过程中不能删除元素，故使用此方法
            if time.time() - msg_dict.get(msgid, None)["msg_time"] > 130.0: #超时两分钟
                item = msg_dict.pop(msgid)
                #print("超时的消息：", item['msg_content'])
                #可下载类消息，并删除相关文件
                if item['msg_type'] == "Picture" \
                        or item['msg_type'] == "Recording" \
                        or item['msg_type'] == "Video" \
                        or item['msg_type'] == "Attachment":
                    print("要删除的文件：", item['msg_content'])
                    os.remove(item['msg_content'])

#将接收到的消息存放在字典中，当接收到新消息时对字典中超时的消息进行清理
#没有注册note（通知类）消息，通知类消息一般为：红包 转账 消息撤回提醒等，不具有撤回功能
# @itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS])

def SaveMsg(msg):
    mytime = time.localtime()  # 这儿获取的是本地时间
    msg_time_touser = mytime.tm_year.__str__() \
                      + "/" + mytime.tm_mon.__str__() \
                      + "/" + mytime.tm_mday.__str__() \
                      + " " + mytime.tm_hour.__str__() \
                      + ":" + mytime.tm_min.__str__() \
                      + ":" + mytime.tm_sec.__str__()

    msg_id = msg['MsgId'] #消息ID
    msg_time = msg['CreateTime'] #消息时间
    if groupPeople(msg)!=None:
        msg_from=groupPeople(msg)
#        groupNameIsOK(msg_from,msg)
    else:
        try:
            msg_from = itchat.search_friends(userName=msg['FromUserName']).NickName# 消息发送人昵称
        except:
            msg_from=None
    #print msg_from
    msg_type = msg['Type'] #消息类型
    msg_content = None #根据消息类型不同，消息内容不同
    msg_url = None #分享类消息有url
    #图片 语音 附件 视频，可下载消息将内容下载暂存到当前目录
    if msg['Type'] == 'Text':
        msg_content = msg['Text']
    elif msg['Type'] == 'Picture':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
    elif msg['Type'] == 'Card':
        msg_content = msg['RecommendInfo']['NickName'] + r" 的名片"
    elif msg['Type'] == 'Map':
        x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1,
                                                                                                                    2,
                                                                                                                    3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()
        else:
            msg_content = r"" + location
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_url = msg['Url']
    elif msg['Type'] == 'Recording':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
    elif msg['Type'] == 'Attachment':
        msg_content = r"" + msg['FileName']
        msg['Text'](msg['FileName'])
    elif msg['Type'] == 'Video':
        msg_content = msg['FileName']
        msg['Text'](msg['FileName'])
    elif msg['Type'] == 'Friends':
        msg_content = msg['Text']

    #更新字典
    # {msg_id:(msg_from,msg_time,msg_time_touser,msg_type,msg_content,msg_url)}
    msg_dict.update(
        {msg_id: {"msg_from": msg_from, "msg_time": msg_time, "msg_time_touser": msg_time_touser, "msg_type": msg_type,
                  "msg_content": msg_content, "msg_url": msg_url}})
    #清理字典
    #print msg_dict
    ClearTimeOutMsg()
def groupPeople(msg):
    T=re.search("\@\@(.*?)",msg['FromUserName'])
    if T!=None:
        return msg['ActualNickName']
    else:
        return None

    #return str(source)
def Revoc(msg):

    #创建可下载消息内容的存放文件夹，并将暂存在当前目录的文件移动到该文件中
    if not os.path.exists(".\\SaveMsg\\"):
        os.mkdir(".\\SaveMsg\\")

    if re.search(r"\<replacemsg\>\<\!\[CDATA\[.*撤回了一条消息\]\]\>\<\/replacemsg\>", msg['Content']) != None:
        str=u"你不要无端端撤回哦，我能检测的到的喔~"
        msg.user.send(u'@%s\u2005%s' % (msg.actualNickName, str))
        old_msg_id = re.search(r"\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        old_msg = msg_dict.get(old_msg_id, {})
        #print old_msg
        msg_send = u"您的好友：" \
                   + old_msg['msg_from']\
                   + u"  在 [" + old_msg['msg_time_touser'] \
                   + u"], 撤回了一条 ["+old_msg['msg_type']+u"] 消息, 内容如下:" \
                   + old_msg['msg_content']

        if  old_msg['msg_type']== "Sharing":
            msg_send += u", 链接: " \
                        + old_msg.get('msg_url', None)
        elif old_msg['msg_type'] == 'Picture' \
                or old_msg['msg_type'] == 'Recording' \
                or old_msg['msg_type'] == 'Video' \
                or old_msg['msg_type'] == 'Attachment':
            msg_send += u", 存储在当前目录下SaveMsg文件夹中"
            shutil.move(old_msg['msg_content'], u".\\SaveMsg\\")
        itchat.send(msg_send, toUserName='filehelper') #将撤回消息的通知以及细节发送到文件助手

        msg_dict.pop(old_msg_id)
        ClearTimeOutMsg()

def get_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        #return r.get('text')
        code = r['code']
        if code == 100000:
            reply = r['text']
        elif code == 200000:
            reply = r['text'] + r['url']
        elif code == 302000:
            list = r['list']
            reply = r['text']
            for i in list:
                reply = reply + '  ,' + i['article'] + i['detailurl'] + '\n'
        return reply
    except:
        return

@itchat.msg_register([TEXT, MAP, CARD, SHARING])
def text_reply(msg):
    SaveMsg(msg)
    defaultReply = u'我不知道你在说啥，' + msg['Text']+u'是啥意思'
    # 如果图灵Key出现问题，那么reply将会是None
    reply = get_response(msg['Text'])
    # a or b的意思是，如果a有内容，那么返回a，否则返回b
    # 有内容一般就是指非空或者非None，你可以用`if a: print('True')`来测试
    return reply or defaultReply

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],isGroupChat=True,isFriendChat=True)
def download_files(msg):
    global gifKey
    SaveMsg(msg)
    msg.download("F:\wxrob\p\\"+msg.fileName)
    # print msg.fileName

    if gifKey==True or groupPeople(msg)==None:
        i=int(random.uniform(1,137))
        mess="F:\wxrob\p\\"+str(i)+".gif"
        if os.path.isfile(mess)!=True:
            mess="F:\wxrob\p\\"+str(i)+".png"
        if os.path.isfile(mess)!=True:
            mess="F:\wxrob\p\\"+str(i)+".jpg"
        print(mess)
        typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
        return '@%s@%s' % (typeSymbol, mess)
# @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
# def download_files(msg):
#     SaveMsg(msg)
#     msg.download(msg.fileName)
#     print msg.fileName
#     typeSymbol = {
#         PICTURE: 'img',
#         VIDEO: 'vid', }.get(msg.type, 'fil')
#     return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send(u'你好啊，我是机器人小锐')

@itchat.msg_register([TEXT, MAP, CARD, SHARING], isGroupChat=True)
def text_reply(msg):
    global gifKey
    global run
    SaveMsg(msg)
    if msg.isAt:
        try:
            alias=itchat.search_friends(userName=msg.actualUserName).Alias
        except:
            alias=None
        if alias=='347467045':
            if re.search(r"run",msg['Text'])!=None:
                run=True
                msg.user.send(u'%s' % (
                    u"你好，我醒了"))
                print('run')
            elif re.search(r"stop",msg['Text'])!=None:
                run=False
                msg.user.send(u'%s' % (
                         u"各位，先拜拜了"))
                print('stop')
            elif re.search(r"别斗了",msg['Text'])!=None:
                gifKey=False
            else:
                if run==True:
                    msg.user.send(u'@%s\u2005%s' % (
                        msg.actualNickName, get_response(msg['Text'])))
                else:
                    pass


        else:
            if re.search("斗图",msg['Text'])!=None:
                msg.user.send(u'@%s\u2005%s' % (
                    msg.actualNickName, u"斗图？我还没怕过谁！来吧！"))
                gifKey=True
                # print itchat.search_friends(name='Jachin')
                # print msg.actualNickName
                # print msg.actualUserName
                # print itchat.search_friends(name=msg.actualNickName)
                # print itchat.search_friends(userName=msg.actualUserName)
#           elseif re.search(r"(今天|日子)",msg['Text'])!=None:
#                msg.user.send(u'@%s\u2005%s' % (
#                    msg.actualNickName, u"今天是个好日子呀~"))

            elif u"你是" in msg['Text'] or u"你叫" in msg['Text'] or u"名字" in msg['Text']:
                msg.user.send(u'@%s\u2005%s' % (
                    msg.actualNickName, u"你好啊，我是机器人小锐~"))
            elif re.search(r"(你主人)",msg['Text'])!=None:
                msg.user.send(u'@%s\u2005%s' % (
                    msg.actualNickName, u"我主人是连小锐"))
            elif re.search(r"(帅)",msg['Text'])!=None:
                msg.user.send(u'@%s\u2005%s' % (
                    msg.actualNickName, u"谁都没我主人帅！！！"))
            elif re.search(r"(管理员)",msg['Text'][3:])!=None:
                msg.user.send(u'@%s\u2005%s' % (
                    msg.actualNickName, u"管理员这个字眼不要再提了，群里发生的事情我一直都看在眼里"))
            elif re.search(r"stop",msg['Text'])!=None:
                    msg.user.send(u'@%s\u2005%s' % (
                          msg.actualNickName,u"不要乱停止我哦，我会生气的"))
            else:
                if run==True:
                    msg.user.send(u'@%s\u2005%s' % (
                        msg.actualNickName, get_response(msg['Text'])))
                else:
                    pass
    # groups_json_list = itchat.get_chatrooms()
    # groupsName = [nm.get('UserName')
    #               for nm in groups_json_list]





#收到note类消息，判断是不是撤回并进行相应操作
@itchat.msg_register([NOTE])
def single(msg):
    Revoc(msg)
@itchat.msg_register([NOTE],isGroupChat=True)
def group(msg):
    Revoc(msg)


# 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
itchat.auto_login(hotReload=False)#
itchat.run()


