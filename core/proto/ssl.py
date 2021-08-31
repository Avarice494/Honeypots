# 这是一个示例 Python 脚本。
import asyncio
import binascii
import time
from .baseserver import BaseProtocol

##########################全局变量###########################
authfile = open('miguanlog.txt', 'a')
dic={
    "mssql_banner":"0401002b0000010000001a00060100200001020021000103002200000400220001ff0a3206510000020000",
    "mssql_response":"0401005600370100aa420018480000010e1b004c006f00670069006e0020006600610069006c0065006400200066006f00720020007500730065007200200027007300610027002e0000000000fd0200000000000000",

    "mysql_banner":""
}
############################mssql###########################
class mssql(BaseProtocol):
    def __init__(self, protocol='mssql', have_banner=True ,logfile = authfile):
        self.protocol = protocol
        self.have_banner = have_banner
        self.username = ''
        self.passhash = ''
        self.remote_addr = ''
        self.remote_port = 0
        self.dic={}
        self.begin_tds_login_packet=[]
        self.logfile_obj = logfile
        self.have_data=False

    def connection_made(self, transport):
        self.transport = transport
        self.remote_addr, self.remote_port = transport.get_extra_info('socket').getpeername()
        if self.have_banner:
            self.transport.write(self._get_banner())

    def data_received(self, data):
        if len(data)>3 : self.have_data = True
        self._parser_data(data)
        self.transport.write(self._get_response())
        if len(data)>150:
            self._parser_data(data)
            self._get_bytes_by_flag(data)
            self._get_username(self.dic["Usernameoffset"],self.dic["Usernamelength"])
            self._get_passwdhash(self.dic["Passwordoffset"], self.dic["Passwordlength"])
            self.transport.write(self._get_response())

    def _get_banner(self):
        a = dic["mssql_banner"]
        b = binascii.a2b_hex(a)
        return b

    def _get_response(self):
        a = dic["mssql_response"]
        b = binascii.a2b_hex(a)
        return b

    def connection_lost(self, exc):
        if self.have_data:self._save_pwd()

    def eof_received(self):
        pass

    def _get_username(self, of, len):
        sstr = ""
        for i in range(0, len):
            sstr += chr(self.begin_tds_login_packet[of + i * 2])
        self.username = sstr

    def _get_passwdhash(self, of, len):
        pws = ""
        mod = []
        for i in range(0, len):
            sstr = hex(self.begin_tds_login_packet[of + i * 2])
            sstr = str(sstr)
            sstr = sstr[2:4]
            for a in range(37, 127):
                mod.append(chr(a))
            for j in mod:
                passwd = (((ord(j) << 4) | (ord(j) >> 4)) ^ 0xA5)
                passwd = hex(passwd)
                passwd = str(passwd)
                passwd = passwd[3:5]
                # print(passwd)
                if passwd == sstr:
                    pws += j
                    break
        self.passhash = pws

    def _get_bytes_by_flag(self , data):
        begin = data
        self.begin_tds_login_packet = begin[8:]
        # 判,断版本TD7
        Type = begin[0]
        if (Type == 16):
            # tds包判断,长度
            TotalPacketLength = begin[2] * 16 * 16 + begin[3]
            # #,判断小版本
            # version
            LengthsAndoffset = begin[44:94]
            self.dic = {
                'ClientNameoffset': LengthsAndoffset[0],
                'ClientNamelength': LengthsAndoffset[2],
                'Usernameoffset': LengthsAndoffset[4],
                'Usernamelength': LengthsAndoffset[6],
                'Passwordoffset': LengthsAndoffset[8],
                'Passwordlength': LengthsAndoffset[10],
                'AppNameoffset': LengthsAndoffset[12],
                'AppNamelength': LengthsAndoffset[14],
                'ServerNameoffset': LengthsAndoffset[16],
                'ServerNamelength': LengthsAndoffset[18],
                'Unknown1offset': LengthsAndoffset[20],
                'Unknown1length': LengthsAndoffset[22],
                'LibraryNameoffset': LengthsAndoffset[24],
                'LibraryNamelength': LengthsAndoffset[26],
                'Localeoffset': LengthsAndoffset[28],
                'Localelength': LengthsAndoffset[30],
                'DatabaseNameoffset': LengthsAndoffset[32],
                'DatabaseNamelength': LengthsAndoffset[34]
            }
