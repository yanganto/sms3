import datetime
import logging
import re
import serial
from collections import namedtuple


pat = re.compile(r'\+CMGL: (?P<index>\d+),'
                 '"(?P<status>.+?)",'
                 '"(?P<number>.+?)",'
                 '("(?P<name>.+?)")?,'
                 '("(?P<date>.+?)")?\r\n'
                 )

logger = logging.getLogger('sms.modem')

MODE = namedtuple('MODE', ['PDU', 'TEXT'])(PDU=0, TEXT=1)


class ModemError(RuntimeError):
    pass


class ModeSettingError(ModemError):
    pass


class Message(object):
    """A received SMS message"""

    format = '%y/%m/%d,%H:%M:%S'

    def __init__(self, index, modem, number, date, text):
        self.index = index
        self.modem = modem
        self.number = number
        if date is not None:
            # modem incorrectly reports UTC time rather than local
            # time so ignore time zone info
            date = date[:-3]
            self.date = datetime.datetime.strptime(date, self.format)
        self.text = text

    def delete(self):
        response = self.modem._command('AT+CMGD=%d' % self.index)
        ok = False
        for line in response:
            if 'OK' in line:
                ok = True
        if not ok:
            raise ModemError('Delete of message %d seemed to fail' 
                             % self.index)


class Modem(object):
    """Provides access to a gsm modem"""
    
    def __init__(self, dev_id, mode=MODE.TEXT):
        self.conn = serial.Serial(dev_id, 9600, timeout=1, rtscts=1)
        # make sure modem is OK
        self._command('AT')
        self._mode = mode
        self.set_mode(mode)

    def send(self, number, message):
        """Send a SMS message

        number should start with 1
        message should be no more than 160 ASCII characters.
        """
        self._command('AT+CMGS="%s"' % number)
        self._command(message + '\x1A', flush=False)

    def messages(self):
        """Return received messages"""
        msgs = []
        text = None
        index = None
        date = None
        all_msgs = '"ALL"' if self._mode == MODE.TEXT else '4'
        for line in self._command('AT+CMGL=%s' % all_msgs)[:-1]:
            m = pat.match(line.decode('ascii'))
            logging.debug(m)
            if m is not None:
                if text is not None:
                    msgs.append(Message(index, self, number, date, text))
                status = m.group('status')
                index = int(m.group('index'))
                number = m.group('number')
                date = m.group('date')
                text = ''
            elif text is not None:
                if line == '\r\n':
                    text += '\n'
                else:
                    text += line.strip().decode('ascii')
        if text is not None:
            msgs.append(Message(index, self, number, date, text))
        return msgs
    
    def wait(self, timeout=None):
        """Blocking wait until a message is received or timeout (in secs)"""
        old_timeout = self.conn.timeout
        self.conn.timeout = timeout
        results = self.conn.read()
        logger.debug('wait read "%s"' % results)
        self.conn.timeout = old_timeout
        results = self.conn.readlines()
        logger.debug('after wait read "%s"' % results)
        
    def _command(self, at_command, flush=True):
        logger.debug('sending "%s"' % at_command)

        self.conn.write(at_command.encode('ascii'))
        if flush:
            self.conn.write('\r\n'.encode('ascii'))
            logger.debug('sending crnl')
        results = self.conn.readlines()
        logger.debug('received "%s"' % results)
        for line in results:
            if 'ERROR' in line.decode('ascii'):
                raise ModemError(results)
        return results

    def set_mode(self, mode):
        try:
            self._command("AT+CMGF=%d" % mode)
        except:
            raise ModeSettingError("Set Mode %d fail" % mode)

    @property
    def mode(self):
        for mode_name, value in MODE._asdict().items():
            print(mode_name, value)
            if self._mode == value:
                return mode_name
        else:
            return "UNKNOWN"

    def __del__(self):
        try:
            self.conn.close()
        except AttributeError:
            pass
