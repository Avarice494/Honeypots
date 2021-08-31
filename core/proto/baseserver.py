import asyncio
from config import authfile
from ..util.qqwry import get_ip_info
from ..util.getnowtime import get_now_str


## BaseProtocol ##
class BaseProtocol(asyncio.Protocol):
    def __init__(self, protocol='mysql', have_banner=False, logfile=authfile):
        self.protocol = protocol
        self.have_banner = have_banner
        self.username = ''
        self.password = ''
        self.remote_addr = ''
        self.remote_port = 0
        self.logfile_obj = logfile
        self.have_data = False


    def _save_pwd(self):
        queryip, country, area = get_ip_info(self.remote_addr)
        data = f'{self.protocol}::{get_now_str()}::{self.username}::{self.password}::{queryip}({country.strip()}_{area.strip()})\n'
        self.logfile_obj.write(data)
        self.logfile_obj.flush()

    def _get_banner(self):
        return b''

    def _parser_data(self, data):
        return b'', b''

    def _get_username(self, data, offset=0):
        return ''

    def _get_passwd(self, data, offset=0):
        return ''

    def _get_response(self):
        return b'this is response'

    def _get_bytes_by_flag(self, data, offset=0, endflag=0):
        ts = ''
        # print(data[offset:])
        for t in data[offset:]:
            if t == endflag:
                break
            else:
                # print(chr(t))
                ts = ts + chr(t)
        return ts.encode('ascii'), len(ts)

    def connection_made(self, transport):
        self.transport = transport
        self.remote_addr, self.remote_port = transport.get_extra_info('socket').getpeername()
        # print(f'connection_made ,remote_addr:{self.remote_addr},remote_port:{self.remote_port}')
        if self.have_banner:
            self.transport.write(self._get_banner())

    def data_received(self, data):
        if len(data) > 3: self.have_data = True
        self._parser_data(data)
        self.transport.write(self._get_response())

    def connection_lost(self, exc):
        if self.have_data:self._save_pwd()

    def eof_received(self):
        pass



