import binascii
from .baseserver import BaseProtocol

server_proto = {
    'telnet': {
        'info': {'port': 23, 'text': ''},
        'server1': 'fffb01fffb03fffd18fffd1f',
        'client1': 'fffd01',
        'client-putty': 'fffb1ffffb20fffb18fffb27fffd01fffb03fffd03fffa1f00500018fff0',
        'server2': '0d0a557365722041636365737320566572696669636174696f6e0d0a0d0a557365726e616d653a20',
        'client2': 'fffd03fffb18fffb1ffffa1f0078001efff0',
        'server3': 'fffa1801fff0',
        'client3': 'fffa1800414e5349fff0',
        'response-pass': '0d0a50617373776f72643a20',
        'errinfo-relogin': '0d0a0d0a252041757468656e7469636174696f6e206661696c65640d0a0d0a557365726e616d653a20',
        'timeout': '0d0a2520557365726e616d653a202074696d656f7574206578706972656421'
    }
}

## telnetProtocol ##
class telnetProtocol(BaseProtocol):
    def __init__(self, protocol='telnet', have_banner=True):
        super().__init__(protocol=protocol, have_banner=have_banner)
        self.renum = 0

    def _get_banner(self):
        data = binascii.a2b_hex(server_proto.get('telnet').get('server1'))
        return data

    def data_received(self, data):
        # 建立telnet连接
        if data == binascii.a2b_hex(server_proto.get('telnet').get('client1')):
            self.transport.write(binascii.a2b_hex(server_proto.get('telnet').get('server2')))
        elif data == binascii.a2b_hex(server_proto.get('telnet').get('client2')):
            self.transport.write(binascii.a2b_hex(server_proto.get('telnet').get('server3')))

        # putty 连接
        elif data == binascii.a2b_hex(server_proto.get('telnet').get('client-putty')):
            self.transport.write(binascii.a2b_hex(server_proto.get('telnet').get('server2')))

        # login: 用户名部分
        elif len(data) == 1 and data != b'\x08' and self.have_data is False:
            self.transport.write(data)
            self.username += data.decode()
        elif data == b'\x08' and self.have_data is False:
            self.username = self.username[:-1]
            self.transport.write(binascii.a2b_hex('082008'))

        # password: 密码部分
        elif data == b'\x0d\x0a' and self.have_data is False:
            self.have_data = True
            self.transport.write(binascii.a2b_hex(server_proto.get('telnet').get('response-pass')))
        elif len(data) == 1 and data != b'\x08' and self.have_data is True:
            self.password += data.decode()
        elif data == b'\x08' and self.have_data is True:
            self.password = self.password[:-1]

        # 再次尝试登录 3次后直接断开连接
        elif data == b'\x0d\x0a' and self.have_data is True:
            self._save_pwd()
            self.renum += 1
            if self.renum == 3:
                self.transport.close()
            self.transport.write(binascii.a2b_hex(server_proto.get('telnet').get('errinfo-relogin')))
            self.have_data = False
            self.username = ''
            self.password = ''

        # 超时
        elif data is None:
            pass

        else:
            pass
