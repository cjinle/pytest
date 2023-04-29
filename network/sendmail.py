#!/usr/bin/env python
# -*- coding: utf-8 -*-
# version $Id: sendmail.py 18418 2012-12-06 08:22:54Z luciferliu $

"""
    邮件发送工具
"""

import sys
import os
import re
import optparse
import glob
import socket
import urllib2
import smtplib
import mimetypes

try:
    from email import encoders
    from email.header import make_header,Header
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    #from email.message import Message
except ImportError:
    from email import Encoders as encoders
    from email.Header import make_header,Header
    from email.MIMEAudio import MIMEAudio
    from email.MIMEBase import MIMEBase
    from email.MIMEImage import MIMEImage
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    #from email.MIMEMessage import Message

try:
    from email.utils import COMMASPACE,formatdate,make_msgid
except ImportError:
    from email.Utils import COMMASPACE,formatdate,make_msgid

__version__     = "1.1.0"
__author__      = "luciferliu"
__description__ = "A module to send email in tencent"

SMTP_SERVER_NAME = 'smtp.163.com'
SMTP_SERVER_PORT = "25"
TIMEOUT= 30

class OptionParser(optparse.OptionParser, object):
    """
        命令行参数基类，用于添加命令行参数
    """
    def __init__(self, *args, **kwargs):
        super(OptionParser, self).__init__(*args, **kwargs)
        self.__addOptions()

    def __addOptions(self):
        self.__getAndAddOptions('Option', self.add_option)
        
    def __getAndAddOptions(self, suffix, addOption):
        for getOption in self.__methodsEndingWith(suffix):
            addOption(getOption(self))

    def __methodsEndingWith(self, suffix):
        return [method for name, method in vars(self.__class__).items() if
                name.endswith(suffix)]

class SendmMailOptionParser(OptionParser):
    """
        Sendmail命令行参数类
    """
    def __init__(self, *args, **kwargs):
        kwargs['usage'] = ("usage: %prog [-f Sender][-r Recipients][-l Cc]"
            "[-b Bcc][-s Subject][-c Content file path][-t Content file type]"
            "[-i Attachment file path][-u Auth user][-p Auth pass]"
            "[-n Content][-V Verbose][-e Silent][-o Output][-g debug]")
        kwargs['version'] = '%prog ' +  __version__
        super(SendmMailOptionParser, self).__init__(*args, **kwargs)

    def _comma_callback(self, option, opt, value, parser): 
        setattr(parser.values, option.dest, value.split(','))
        
    def fromOption(self):
        """
            发件人
        """
        return optparse.Option('-f', '--from',
            action="store",
            type="string",
            dest='fromaddr', 
            default='', 
            help="Mail Sender")
 
    def toOption(self):
        """
            收件人
        """
        return optparse.Option('-r', '--to',
            action="callback",
            dest='to', 
            type='string', 
            callback=self._comma_callback,
            default=[],
            help="Mail Recipients")

    def ccOption(self):
        """
            抄送
        """
        return optparse.Option('-l', '--cc', 
            action="callback",
            dest='cc', 
            type='string', 
            callback=self._comma_callback,
            default=[],
            help="Mail Cc Recipients")

    def bccOption(self):
        """
            密件抄送
        """
        return optparse.Option('-b', '--bcc', 
            action="callback",
            dest='bcc', 
            type='string', 
            callback=self._comma_callback,
            default=[],
            help="Mail Bcc Recipients")

    def subjectOption(self):
        """
            邮件主题
        """
        return optparse.Option('-s', '--subject', 
            action="store",
            type="string",
            dest='subject', 
            default='', 
            help="Mail Subject")

    def contentOption(self):
        """
            邮件正文内容
        """
        return optparse.Option('-n', '--content', 
            action="store",
            type="string",
            dest='content', 
            default='', 
            help="Mail Content file path")

    def contentPathOption(self):
        """
            邮件正文路径
        """
        return optparse.Option('-c', '--content_file', 
            action="store",
            type="string",
            dest='content_file', 
            default='', 
            help="Mail Content file path")

    def contentTypeOption(self):
        """
            邮件正文类型
        """
        return optparse.Option('-t', '--content_type', 
            action="store",
            type="string",
            dest='content_type', 
            default='', 
            help="Mail Content file type")

    def attachmentOption(self):
        """
            附件路径
        """
        return optparse.Option('-i', '--attachment', 
            action="callback",
            dest='attachment', 
            type='string', 
            callback=self._comma_callback,
            default="",
            help="Mail Attached file path, support asterisk wildcard")

    def authUserOption(self):
        """
            邮件服务器登录用户
        """
        return optparse.Option('-u', '--user', 
            action="store",
            dest='user', 
            type='string', 
            default='', 
            help="Auth user")

    def pathOption(self):
        """
            邮件服务器登录密码
        """
        return optparse.Option('-p', '--password', 
            action="store",
            dest='password', 
            type='string', 
            default='', 
            help="Auth pass")

    def verboseOption(self):
        """
            显示verbose
        """
        return optparse.Option('-V', '--verbose', 
            action="store_true",
            dest='verbose', 
            default=False, 
            help="Display verbose")

    def silentOption(self):
        """
            静默模式
        """
        return optparse.Option('-e', '--silent', 
            action="store_true",
            dest='silent', 
            default=False, 
            help="Not send mail")

    def outputOption(self):
        """
            保存邮件到文本
        """
        return optparse.Option('-o', '--output', 
            action="store",
            dest='output', 
            type='string',
            default='', 
            help="save email to file")

    def debugOption(self):
        """
            邮件调试开关
        """
        return optparse.Option('-g', '--debug', 
            action="store_true",
            dest='debug', 
            default=False, 
            help="debug switch")

    def format_help(self, formatter=None):
        result = super(SendmMailOptionParser, self).format_help()
        #python sendmail.py --from=angusguan --to=luciferliu --subject="你好"

        examples = """Examples:
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world"
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content="welcom to my email"
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="aaa"
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i '*.gif'
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i apache_pb.gif,apache_pb2.gif
    python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i pics

    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world"
    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world" --content="welcom to my email"
    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world" --content_file="aaa"
    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i '*.gif'
    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i apache_pb.gif,apache_pb2.gif
    python sendmail.py  --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html -i pics

    python sendmail.py --from="dsweb@tencent.com" --to="luciferliu@tencent.com" --subject="hello world"

    send text mail:
        python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=text
        python sendmail.py -f dsweb@tencent.com -r robincui@tencent.com,cyckercai@tencent.com -l angusguan@tencent.com -s mysubject -c ./aaa -t txt -i './*.gif'
    send html mail:
        python sendmail.py --from=dsweb@tencent.com --to=luciferliu@tencent.com --subject="hello world" --content_file="./notice.jacky.html" --content_type=html
        python sendmail.py -f dsweb@tencent.com -r luciferliu@tencent.com,fanlong@tencent.com -l larryxiong@tencent.com -s mysubject -c ./test.html -t html -i './*.gif'
        """
        result = result + os.linesep  + examples
        notes = """NOTES:
    Please use absolute path if you can not be sure in the correct path.
        """
        result = result + os.linesep  + notes
        return result


class Message(object):
    """
        邮件的属性信息
    """
    def __init__(self, fromaddr, to, subject, cc=[], bcc=[], 
             content=None, content_type="plain", content_file=None, attachments=None, charset='gb2312', init=True):
        """
        @fromaddr: 发件人
        @to: 收件人
        @cc: 抄送
        @bcc: 密件抄送
        @content: 邮件正文
        @content_type: 邮件正文类型
        @content_file: 邮件正文所在的文件
        @stream: 邮件输出流
        """
        #COMMASPACE = ', '
        super(Message, self).__init__()
        self._headers = {}
        self['Subject']         = Header(subject, charset)
        self['From']            = fromaddr
        self['To']              = to

        if not self['From'] or not self['To'] or not self['Subject']:
            raise "Error: From or to or subject should not be None"

        self['Cc']              = cc
        self['Bcc']             = bcc
        self['content']         = self.getContent(content, content_file)
        self['content_type']    = self.getContentType(content_type)
        self['content_file']    = content_file
        self['attachments']     = self.getAttachments(attachments)

        self['Date']            = formatdate(localtime = True)
        self['Message-ID']      = make_msgid()
        # encoding
        self['charset']         = charset
        # 处理cid
        self['imageId'] = 0
        self['images']  = {}
        self.reImage = re.compile(r"(<image\s+src\s*=\s*['\"])([^>]*)(['\"]\s*>)", re.IGNORECASE|re.DOTALL)

        if init:
            self.createMime()

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, val):
        name = name.lower()
        self._headers[name] = val

    def get(self, name, failobj=None):
        name = name.lower()
        for k, v in self._headers.items():
            if k.lower() == name:
                return v
        return failobj

    def createMime(self):
        """
            创建MIME
        """
        self.createRootMime()
        self.createBodyMime()
        self.createAttachmentMime()

    def createRootMime(self):
        """
        创建MIME，并添加信息头
        """
        #msgRoot = MIMEMultipart("mixed")
        msgRoot = MIMEMultipart()
        msgRoot['Subject']      = self['Subject']
        msgRoot['From']         = self['From']
        to = self['To']
        if to:
            msgRoot['To']       = COMMASPACE.join(to)
        cc = self['Cc']
        if cc:
            msgRoot['Cc']       = COMMASPACE.join(cc)
            to.extend(cc)
        bcc = self['Bcc']
        if bcc:
            msgRoot['Bcc']      = COMMASPACE.join(bcc)
            to.extend(bcc)
        msgRoot['Date']         = self['Date']
        msgRoot['Message-ID']   = self['Message-ID']
        self['rootMime'] = msgRoot

    def _handle_image(self, matchobj):
            """
                获得cid字符串
            """
            img=matchobj.group(2).strip()
            if not self['images'].has_key(img):
                self['imageId'] += 1
                self['images'][img]="inline-img%d" % self['imageId']
            return "%scid:%s%s" % (matchobj.group(1), self['images'][img], matchobj.group(3))
           
    def _parse_images(self):
            """
                使用cid字符串替换image src
            """
            self['content'] = self.reImage.sub(self._handle_image, self['content'])
            return self['images']

    def createBodyMime(self):
        """
            创建邮件正文MIME
        """
        if self['content']:
            body = self['content']
            if self['content_type'] == "plain":
                plainBody = MIMEText(body, _subtype='plain', _charset=self['charset'])
                self['rootMime'].attach(plainBody)
            elif self['content_type'] == "html":
                msgRelated = MIMEMultipart("related")
                # 支持html和plain并存
                msgAlternative = MIMEMultipart('alternative')
                msgRelated.attach(msgAlternative)
                self['rootMime'].attach(msgRelated)
                # 支持内嵌资源
                self._parse_images()
                body = self['content']
                # 支持plain
                plainBody = MIMEText(body, _subtype='plain', _charset=self['charset'])
                msgAlternative.attach(plainBody)
                # 支持html
                htmlBody = MIMEText(body, _subtype='html', _charset=self['charset'])
                msgAlternative.attach(htmlBody)

                # 如果存在内嵌资源，则创建内嵌资源MIME
                if self['images']:
                    for img in self['images'].keys():
                        cidImage = self._createAttachmentMime(img, cid=True)
                        if cidImage:
                            img_type, img_ext=cidImage["Content-Type"].split("/")
                            cidImage.replace_header('Content-Type', "%s/%s; name=\"%s.%s\"" % (img_type, img_ext, self['images'][img], img_ext))
                            cidImage.add_header("Content-ID", "<%s>" % self['images'][img])
                            cidImage.add_header("Content-Disposition", "inline; filename=\"%s.%s\"" % (self['images'][img], img_ext))
                            msgRelated.attach(cidImage)

    def getContent(self, content, content_file):
        """
            获得邮件正文
        """
        body = ""
        if content:
            body = content
        if not content and content_file:
            if os.path.isfile(content_file):
                body = open(content_file).read()
        return body

    def getContentType(self, content_type="plain"):
        """
            获得邮件正文类型
        """
        if not content_type or content_type == "text":
            content_type = "plain"
        return content_type

    def getAttachments(self, attachments):
        """
            获得邮件列表
        """
        result = []
        if attachments:
            for item in attachments:
                if os.path.isdir(item):
                    filelist = os.listdir(item)
                    filelist = [ os.path.join(item, filename) for filename in filelist ]
                else:
                    filelist = glob.glob(item)
                result.extend(filelist)
        return result

    def _createAttachmentMime(self, path, cid=False):
        """
            创建附件MIME
        """
        def _read_image(path):
            if path.startswith("http://"):
                #return urllib2.urlopen(path).read()
                return False
            else:
                return open(path, 'rb').read()
        
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(path)
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            cidContent = _read_image(path)
            if not cidContent:
                return None
            msg = MIMEImage(cidContent, _subtype=subtype)
        elif maintype == 'audio':
            fp = open(path, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        # Set the filename parameter
        if not cid:
            filename = os.path.split(path)[-1]
            if not os.path.splitext(filename)[-1]:
                filename = "./%s" % filename
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
        return msg

    def createAttachmentMime(self):
        attachments = self['attachments']
        for path in attachments:
            absolutePath = os.path.abspath(path)
            if not absolutePath and not os.path.isfile(absolutePath):
                continue
            self['rootMime'].attach(self._createAttachmentMime(absolutePath))

    def as_string(self):
        """
            格式化邮件
        """
        rootMime = self['rootMime'].as_string()
        return rootMime


class Mailer(object):
    def __init__(self, local_hostname=SMTP_SERVER_NAME,port=SMTP_SERVER_PORT, timeout=TIMEOUT, 
             user=None, password=None, silent=False, output=None, debug=False, verbose=False):
        """
        @local_hostname: 邮件服务器IP
        """
        super(Mailer, self).__init__()
        self.local_hostname = local_hostname
        self.port           = port
        self.timeout        = timeout
        self.silent         = silent
        self.output         = output
        self.debug          = debug
        self.verbose        = verbose
        self.user           = user
        self.password       = password
    
    def writeEmail(self, msgRoot):
        """
        重定向邮件内容
        """
        fp = open(self.output, 'w')
        fp.write(msgRoot)
        fp.close()

    def send(self, message):
        """
            发送邮件
        """
        msgRoot = message.as_string()
        if self.silent:
            if self.output:
                self.writeEmail(msgRoot)
            print msgRoot
        else:
            if self.output:
                self.writeEmail(msgRoot)
            try:
                # 设置连接延时
                import socket
                try:
                    timeout = int(self.timeout)
                    if timeout > 0:
                        socket.setdefaulttimeout(timeout)
                except:
                    pass
                # 创建SMTP object
                smtp = smtplib.SMTP(local_hostname=self.local_hostname)
                #smtp = smtplib.SMTP()
                # 调试开关
                smtp.set_debuglevel(self.debug)
                # 连接邮件服务器
                smtp.connect(self.local_hostname, self.port)
                # 登录
                if self.user and self.password:
                    smtp.login(self.user, self.password)
                # 发送邮件
                try:
                    # Python 3.2.1
                    smtp.send_message(message)
                #except AttributeError:
                except Exception, e:
                    # Python 2.7.2, Python2.4, Python2.5
                    smtp.sendmail(message['From'], message['To'], message.as_string())
                # 退出
                smtp.quit()
            except (socket.gaierror, socket.error, socket.herror, smtplib.SMTPException, smtplib.socket.error), e:
                sys.exit(1)

def sendmail(to, subject="", content="", cc=None, bcc=None, content_type=None, content_file=None, attachment=None):
    """
        发送邮件
        >>> from sendmail import sendmail
        >>> sendmail(['luciferliu@tencent.com'], subject="test", content="asdfasdfasdfasdf")
    """
    message = Message("IEODSAP@tencent.com", to, subject, cc, bcc, content, content_type, content_file, attachment)
    sender = Mailer(user="seeec@163.com", password='33135331.')
    sender.send(message)

if __name__ == '__main__':

    def main():
        sendmailParser = SendmMailOptionParser()
        (options, args) = sendmailParser.parse_args()
        if options.verbose:
            print '*' * 50
            print options
            print args
            print '*' * 50

        if not options.user:
            options.user = "seeec@163.com"
        if not options.password:
            options.password = '33135331.'
        options.fromaddr = "seeec@163.com"
	#tostr=[]
	#for tos in options.to:
	#	toarr=tos.split(';')
	#	for value in toarr: 
	#		tostr.append(value.split('@')[0]+"@tencent.com")
	#options.to=tostr		
	#ccstr=[]
	#for tos in options.cc:
    #    	toarr=tos.split(';')
    #    	for value in toarr:
    #            	ccstr.append(value.split('@')[0]+"@tencent.com")
	#options.cc=ccstr
        message = Message(options.fromaddr, options.to, options.subject, options.cc, options.bcc, options.content, options.content_type, options.content_file, options.attachment)
        sender = Mailer(SMTP_SERVER_NAME, SMTP_SERVER_PORT, TIMEOUT, options.user, options.password, options.silent, options.output, options.debug, options.verbose)
        sender.send(message)

    main()
