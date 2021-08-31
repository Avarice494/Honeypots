import binascii
from .baseserver import BaseProtocol


server_proto = {
    'mongoDB': {
        'info': {'port': 27017, 'text': ''},
        'banner': '4a0000000a352e352e353300090000005b2956573337583700fff72102000f80150000000000000000000049486f76254f3f2f6b502f36006d7973716c5f6e61746976655f70617373776f726400',
        'response': '000002ff1504233238303030',
        'errinfo': "Access denied for user '{username}'@'{remote_addr}' (using password: YES)"
    },
}
## mysqlProtocol ##

class mysqlProtocol(BaseProtocol):
    def __init__(self, protocol='mysql', have_banner=False):
        super().__init__(protocol=protocol, have_banner=have_banner)

    def _parser_data(self, data):
        username, lenofstr = self._get_username(data, 36)
        pwdoffset = 36 + lenofstr + 2
        self._get_passwdhash(data, pwdoffset)

    def _get_username(self, data, offset=0):
        username, lenofstr = self._get_bytes_by_flag(data, 36)
        self.username = username.decode('utf-8')
        return username, lenofstr

    def _get_passwdhash(self, data, offset=0):
        password = binascii.b2a_hex(data[offset:offset+20])
        self.password = password.decode('utf-8')
        return password

    def _get_response(self):
        data = binascii.a2b_hex(server_proto.get('mysql').get('response'))
        error = server_proto.get('mysql').get('errinfo').format(username=self.username,remote_addr=self.remote_addr).encode()
        lenstr = binascii.a2b_hex(hex( len(data)+ len(error) - 3)[2:])
        return lenstr + data + error


