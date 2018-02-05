import signal
from threading import Thread

from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError


class BotClient(MatrixClient):
    def __init__(self, base_url, logger, prefix, commands,
                 token=None, user_id=None, valid_cert_check=True):
        super().__init__(
            base_url,
            token=token,
            user_id=user_id,
            valid_cert_check=valid_cert_check
        )
        self.logger = logger
        self.running = False
        self.commands = commands
        self.prefix = prefix
        signal.signal(signal.SIGINT, self.quit)

    def start(self, user, password, rooms=set()):
        self.logger.info('Logging in...')
        self.login_with_password(user, password)
        self.logger.info(f'Logged in as {user}!')

        for room in set(self.get_rooms()) | set(rooms):
            try:
                self.join_room(room).add_listener(self.on_event)
            except MatrixRequestError as e:
                self.logger.warning(str(e))
        self.start_listener_thread()
        self.running = True
        print('Press Ctrl-C to quit.')
        signal.pause()

    def quit(self, sig, frame):
        self.running = False
        self.logger.info("Stopping listener thread...")
        self.stop_listener_thread()
        self.logger.info("Logging out...")
        self.logout()
        exit(0)

    def _on_event(self, room, event):
        if event['type'] == 'm.room.message':
            message = event['content']['body']
            self.on_message(room, event, message)

    def on_event(self, room, event):
        if self.running:
            t = Thread(target=self._on_event, args=(room, event))
            t.daemon = True
            t.start()

    def on_message(self, room, event, message):
        if self.user_id in event['sender']:
            return
        if event['content']['msgtype'] != "m.text":
            return
        if message.startswith(self.prefix):
            payload = message.lstrip(self.prefix).split(' ')
            if payload:
                name = payload[0]
                try:
                    callback = self.commands[name]
                except KeyError:
                    pass
                else:
                    callback(room, event, payload[1:])
