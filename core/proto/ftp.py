import binascii
import asyncio
import time
##############################  文本模式写文件  ##############################
authfile = open(file='authfile.txt',mode='at',encoding='utf8',errors='ignore')
scanfile = open(file='scanfile.txt',mode='at',encoding='utf8',errors='ignore')
##############################  协议信息  ##############################
server_example={
    'ftp':{
        'info':{'port':21},
        'username':'123',
        'banner':{
            'version':'323230202876734654506420332e302e33290d0a',
            'encoding':'32303020416c7761797320696e2055544638206d6f64652e0d0a'
                  },
        'errorinfo':'353330205065726d697373696f6e2064656e6965642e0d0a',
        'byeinfo':'32323120476f6f646279652e0d0a',
        'passwdinfo':'33333120506c656173652073706563696679207468652070617373776f72642e0d0a',
        'passwderrorinfo':'353330204c6f67696e20696e636f72726563742e0d0a',
        'timeout':'3432312054696d656f75742e0d0a'
    },
    'telnet':{

    }
}
##############################  function  ##############################

class BaseProtocol(asyncio.Protocol):
    def __init__(self, protocol='mysql', have_banner=False, logfile=authfile):
        self.protocol = protocol
        self.have_banner = have_banner
        self.username = ''
        self.passhash = ''
        self.remote_addr = ''
        self.remote_port = 0
        self.logfile_obj = logfile
        self.have_data=False
    '''
    def _save_user(self):
        queryip, country, area = get_ip_info(self.remote_addr)
        data = f'{self.protocol}::{get_now_str()}::{self.username}::{self.passhash}::{queryip}({country.strip()}_{area.strip()})\n'
        self.logfile_obj.write(data)
        self.logfile_obj.flush()
    '''

    def _get_banner(self):
        return b''

    def _parser_data(self, data):
        return b'', b''

    def _get_username(self, data, offset=0):
        return ''

    def _get_passwdhash(self, data, offset=0):
        return ''

    def _get_response(self):
        return b'this is response'

    def _get_bytes_by_flag(self, data, offset=0, endflag=0):
        ts = ''
        for t in data[offset:]:
            if t == endflag:
                break
            else:
                ts = ts + chr(t)
        return ts.encode('ascii'), len(ts)

    '''
    连接建立时被调用,transport 参数是代表连接的传输。 此协议负责将引用保存至对应的传输。
    '''
    def connection_made(self, transport):
        self.transport = transport
        '''
        获取对端IP和端口
        transport.get_extra_info返回有关它使用的传输或底层资源的信息
        getpeername() 套接字连接到的远程地址
        '''
        self.remote_addr, self.remote_port = transport.get_extra_info('socket').getpeername()
        # print(f'connection_made ,remote_addr:{self.remote_addr},remote_port:{self.remote_port}')
        if self.have_banner:
            # 写入传输
            self.transport.write(self._get_banner())

    def data_received(self, data):
        # 判断数据大小
        if len(data) > 3: self.have_data = True
        if self.have_data:
            # 调用函数读取传入的数据
            self._parser_data(data)
        # 写入回复
        self.transport.write(self._get_response())

    def connection_lost(self, exc):
        if self.have_data:self._save_user()

    def eof_received(self):
        pass
class ftpProtocol(BaseProtocol):
    def __init__(self, protocol='ftp', have_banner=True, logfile=authfile):
        self.sign = ''
        super().__init__(protocol=protocol,have_banner=have_banner)
    def _get_banner(self):
        version=binascii.a2b_hex(server_example.get('ftp').get('banner').get('version'))
        encoding=binascii.a2b_hex(server_example.get('ftp').get('banner').get('encoding'))
        return version,encoding
    # 数据解析
    def _parser_data(self,data):
        # 通过标识判断输入数据类型
        if self.sign == '':
            data = self._save_user(data,10)
            # 判断是否是正确的用户名
            if data == server_example.get('ftp').get('username'):
                self.transport.write(binascii.a2b_hex(server_example.get('ftp').get('passwdinfo')))
                self.sign = 'pass'
                self.username = server_example.get('ftp').get('username')
                return 0
            else:
                # 写入日志
                ulog = self._save_log('U',data)
                # 写入回复
                self.transport.write(self._get_response())
        if self.sign == 'pass':
            # 提取数据
            passwd = self._save_user(data,10)
            # 写入日志
            plog = self._save_log('P',server_example.get('ftp').get('username'),passwd)
            # 写入回复
            self.transport.write(self._get_response())

    # 提取用户输入数据
    def _save_user(self, data,offset=0):
        data = binascii.b2a_hex(data)
        data = self._get_bytes_by_flag(data,offset)
        data = data.decode('utf-8')
        return data
    # 写入日志
    def _save_log(self,sign,user,passwd='<Null>'):
        log = sign + '::' + self.protocol + '::' + time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime()) + '::' +user+ '::' +passwd+ '::' + self.remote_addr + '\n'
        self.logfile_obj.write(log)
        self.logfile_obj.flush()
    def _get_bytes_by_flag(self, data, offset=0, endflag=0):
        ts = ''
        tts = ''
        for t in data[offset:]:
            if t == endflag:
                break
            else:
                ts = ts + chr(t)
        #转成byte，有’\r\n‘，去除
        ts = binascii.a2b_hex(ts)
        for t in ts[0:]:
            if t == endflag:
                break
            else:
                tts = tts + chr(t)
        #去除换行
        tts = tts.strip()
        return tts.encode('ascii')

    def _get_response(self):
        if self.sign == '':
            data = binascii.a2b_hex(server_example.get('ftp').get('errorinfo'))
        if self.sign == 'pass':
            data = binascii.a2b_hex(server_example.get('ftp').get('passwderrorinfo'))
        return data




    def connection_made(self, transport):
        self.transport = transport
        '''
        获取对端IP和端口
        transport.get_extra_info返回有关它使用的传输或底层资源的信息
        getpeername() 套接字连接到的远程地址
        '''
        self.remote_addr, self.remote_port = transport.get_extra_info('socket').getpeername()
        # print(f'connection_made ,remote_addr:{self.remote_addr},remote_port:{self.remote_port}')
        if self.have_banner:
            response_data=self._get_banner()
            for i in response_data:
                # 写入传输
                self.transport.write(i)
    '''
    当收到数据时被调用,data为包含入站数据的非空字节串对象
    '''
    def data_received(self, data):
        # 判断数据大小
        if len(data) > 3: self.have_data = True
        #判断是否是客户端的编码信息
        if data == b'OPTS UTF8 ON\r\n':
            self.have_data = False
        #判断是否是断连接信息
        if data == b'QUIT\r\n':
            self.have_data = False
            self.transport.write(binascii.a2b_hex(server_example.get('ftp').get('byeinfo')))
        # 用户数据输入
        if self.have_data:
            # 调用函数读取传入的数据
            self._parser_data(data)
            # # 写入回复
            # self.transport.write(self._get_response())

    def connection_lost(self, data):
        pass
    # def eof_received(self):
    #     self.transport.write(server_example.get('ftp').get('timeout'))
    #     self.transport.close()

##############################  启动  ##############################
async def main():
    # 开启一个异步环
    loop = asyncio.get_running_loop()
    #监听本地端口并开启一个传输对象
    async def run_service(protocol,port):
        '''
        创建TCP服务 (socket 类型 SOCK_STREAM ) 监听 host 地址的 port 端口
        loop.create_server(protocol_factory, host=None, port=None, *, family=socket.AF_UNSPEC, flags=socket.AI_PASSIVE,
        sock=None, backlog=100, ssl=None, reuse_address=None, reuse_port=None, ssl_handshake_timeout=None, start_serving=True)
        protocol_factory必须为一个返回协议实现的可调用对象。protocol_factory参数为接收到的链接创建协议对象，并用传输对象来表示。这些方法一般会返回(transport, protocol)元组
        '''
        server = await loop.create_server(protocol,'0.0.0.0',port)
        # 启用
        await server.serve_forever()

    # 创建一个队列
    allroco_tasks = []
    # 将执行的任务放入队列中
    allroco_tasks.append(run_service(ftpProtocol,21))
    #并发运行*allroco_tasks序列中的可等待对象
    await asyncio.gather(*allroco_tasks)
if __name__ == '__manin__':
    asyncio.run(main())