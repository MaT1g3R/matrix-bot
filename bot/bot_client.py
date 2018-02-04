import signal

from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError


class BotClient(MatrixClient):
    def __init__(self, base_url, logger, token=None, user_id=None, valid_cert_check=True):
        super().__init__(
            base_url,
            token=token,
            user_id=user_id,
            valid_cert_check=valid_cert_check
        )
        self.logger = logger
        signal.signal(signal.SIGINT, self.quit)

    def start(self, user, password, rooms=set()):
        self.logger.info('Logging in...')
        self.login_with_password(user, password)
        self.logger.info(f'Logged in as {user}!')

        for room in set(self.get_rooms()) | set(rooms):
            try:
                self.join_room(room).add_listener(self.on_message)
            except MatrixRequestError as e:
                self.logger.warning(str(e))
        self.start_listener_thread()
        print('Press Ctrl-C to quit.')
        signal.pause()

    def quit(self, sig, frame):
        self.logger.info("Stopping listener thread...")
        self.stop_listener_thread()
        self.logger.info("Logging out...")
        self.logout()
        exit(0)

    def on_message(self, room, event):
        if event['type'] != 'm.room.message':
            return
        if event['content']['msgtype'] != "m.text":
            return
        if self.user_id in event['sender']:
            return
        message = event['content']['body']
        if message.startswith('!'):
            payload = message.lstrip('!').split(' ')
            if payload[0] == 'echo':
                try:
                    to_echo = payload[1]
                except IndexError:
                    room.send_text('Please enter something for me to echo.')
                else:
                    room.send_text(to_echo)
