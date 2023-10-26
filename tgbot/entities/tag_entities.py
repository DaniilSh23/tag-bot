
class TagMsgEntity:
    """
    Дата класс, который хранит информацию о сообщении с тегом в определенном чате.
    """
    chat_id: int
    msg_id: int
    send_msg_timestamp: float
    last_tag_timestamp: float
    msg_text: str
    media_msg: bool

    def __init__(self, chat_id, msg_id, send_msg_timestamp, msg_text, media_msg=False):
        self.chat_id = chat_id
        self.msg_id = msg_id
        self.send_msg_timestamp = send_msg_timestamp
        self.last_tag_timestamp = send_msg_timestamp    # При создании класса это значение равно send_msg_timestamp
        self.msg_text = msg_text
        self.media_msg = media_msg
