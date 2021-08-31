import socket
import struct


## qqwry ##
class GetIpinfo:
    def __init__(self, db_file='./core/util/qqwry.dat'):
        self.f_db = open(db_file, "rb")
        bs = self.f_db.read(8)
        (self.first_index, self.last_index) = struct.unpack('II', bs)
        self.index_count = int((self.last_index - self.first_index) / 7 + 1)
        self.cur_start_ip = None
        self.cur_end_ip_offset = None
        self.cur_end_ip = None
        # print(self.get_version(), " 纪录总数: %d 条 "%(self.index_count))

    def _set_ip_range(self, index):
        offset = self.first_index + index * 7
        self.f_db.seek(offset)
        buf = self.f_db.read(7)
        # print(buf)
        (self.cur_start_ip, of1, of2) = struct.unpack("IHB", buf)
        # print((self.cur_start_ip, of1, of2))
        self.cur_end_ip_offset = of1 + (of2 << 16)
        self.f_db.seek(self.cur_end_ip_offset)
        buf = self.f_db.read(4)
        (self.cur_end_ip,) = struct.unpack("I", buf)

    def get_offset_string(self, offset=0):
        '''
        获取文件偏移处的字符串(以'\0'结尾)
        :param offset: 偏移
        :return: str
        '''
        if offset:
            self.f_db.seek(offset)
        bs = b''
        ch = self.f_db.read(1)
        (byte,) = struct.unpack('B', ch)
        while byte != 0:
            bs += ch
            ch = self.f_db.read(1)
            (byte,) = struct.unpack('B', ch)
        return bs.decode('gbk')

    def _get_area_addr(self, offset=0):
        if offset:
            self.f_db.seek(offset)
        bs = self.f_db.read(1)
        (byte,) = struct.unpack('B', bs)
        # print(byte)
        if byte == 0x01 or byte == 0x02:
            p = self.getLong3()
            # print(p)
            if p:
                return self.get_offset_string(p)
            else:
                return ""
        else:
            self.f_db.seek(-1, 1)
            return self.get_offset_string(offset)

    def _get_addr(self, offset):
        '''
        获取offset处记录区地址信息(包含国家和地区)
        如果是中国ip，则是 "xx省xx市 xxxxx地区" 这样的形式
        (比如:"福建省 电信", "澳大利亚 墨尔本Goldenit有限公司")
        :param offset:
        :return:str
        '''
        self.f_db.seek(offset + 4)
        bs = self.f_db.read(1)
        (byte,) = struct.unpack('B', bs)
        if byte == 0x01:    # 重定向模式1
            country_offset = self.getLong3()
            # print('ccc'+country_offset)
            self.f_db.seek(country_offset)
            bs = self.f_db.read(1)
            (b,) = struct.unpack('B', bs)
            # print(b)
            if b == 0x02:
                country_addr = self.get_offset_string(self.getLong3())
                self.f_db.seek(country_offset + 4)
            else:
                country_addr = self.get_offset_string(country_offset)
            area_addr = self._get_area_addr()
            # print("1-"+area_addr)
        elif byte == 0x02:  # 重定向模式2
            country_addr = self.get_offset_string(self.getLong3())
            area_addr = self._get_area_addr(offset + 8)
            # print("2-"+area_addr)
        else:   # 字符串模式
            country_addr = self.get_offset_string(offset + 4)
            area_addr = self._get_area_addr()
            # print("3-"+area_addr)
        return country_addr + " " + area_addr

    def get_addr_by_ip(self, ip):
        '''
        通过ip查找其地址
        :param ip: (int or str)
        :return: str
        '''
        srcip = ip
        if type(ip) == str:
            ip = self.str2ip(ip)
            # print(ip)
        L = 0
        # print(self.index_count)
        R = self.index_count - 1
        while L < R - 1:
            M = int((L + R) / 2)
            self._set_ip_range(M)
            if ip == self.cur_start_ip:
                L = M
                break
            if ip > self.cur_start_ip:
                L = M
            else:
                R = M
        self._set_ip_range(L)
        # version information, 255.255.255.X, urgy but useful
        # 0xffffff00 是255.255.255.0 ip & 0xffffff00 等同子网掩码255.255.255.0的网段起始ip
        if ip & 0xffffff00 == 0xffffff00:
            self._set_ip_range(R)
        if self.cur_start_ip <= ip <= self.cur_end_ip:
            # print(self.cur_end_ip_offset)
            address = self._get_addr(self.cur_end_ip_offset)
            # print(address)
        else:
            address = "未找到该IP的地址"
        country = address.split()[0]
        area = address.split()[1]
        return srcip, country, area

    def str2ip(self, s):
        '''
        IP字符串转换为整数IP
        读取的整数IP转换成翻转后的整数IP
        :param s:
        :return:
        '''
        (ip,) = struct.unpack('I', socket.inet_aton(s))
        return ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)

    def getLong3(self, offset=0):
        '''
        3字节的数值
        :param offset:
        :return:
        '''
        if offset:
            self.f_db.seek(offset)
        bs = self.f_db.read(3)
        (a, b) = struct.unpack('HB', bs)
        return (b << 16) + a

def get_ip_info(ip):
    gip = GetIpinfo()
    ip, country, area = gip.get_addr_by_ip(ip)
    return ip, country, area