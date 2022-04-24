from tortoise import Model, fields

from ..bot import bot


class SubChannel(Model):
    channel_id = fields.IntField()
    channel_mention = fields.TextField()
    channel_button_text = fields.TextField()


class Film(Model):
    code = fields.IntField(unique=True)
    chat_id = fields.IntField()
    message_id = fields.IntField()


class BotUser(Model):
    user_id = fields.IntField(unique=True)
    username = fields.TextField(null=True)

    referral_data: fields.ReverseRelation["ReferralData"]

    @property
    def referral_url(self) -> str:
        return f"https://t.me/{bot._me.username}?start={self.user_id}"


class ReferralData(Model):
    bot_user: fields.ForeignKeyRelation[BotUser] = fields.ForeignKeyField(
        "models.BotUser", related_name="referral_data"
    )

    referrals_count = fields.IntField(default=0)
