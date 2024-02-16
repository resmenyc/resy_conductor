import time
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook, DiscordEmbed
from utils import Utils
import os
from random import randint
import sys

utils = Utils()


class Discord:
    def __init__(self):
        self.webhook_url = ""
        self.logs_webhook_url = ""
        self.cancels_webhook_url = ""

        if not os.getenv("WEBHOOK_URL"):
            utils.thread_warn("Not sending discord webhooks, please set .env")
        else:
            self.webhook_url = os.getenv("WEBHOOK_URL")

        if not os.getenv("LOGS_WEBHOOK_URL"):
            utils.thread_error("No logs webhook found")
        else:
            self.logs_webhook_url = os.getenv("LOGS_WEBHOOK_URL")

        if not os.getenv("CANCELS_WEBHOOK_URL"):
            utils.thread_error("No cancels webhook found")
        else:
            self.cancels_webhook_url = os.getenv("CANCELS_WEBHOOK_URL")

    def cancels_wh(self, message):
        if self.cancels_webhook_url is not None:
            webhook = DiscordWebhook(url=self.cancels_webhook_url)

            embed = DiscordEmbed(
                title="ResMe Conductor Robot",
                description="New Cancelled Reservation",
                color="ff2647",
            )

            embed.set_footer(text=f"Sent @ {datetime.now()}")

            embed.add_embed_field(name="Message", value=message)

            webhook.add_embed(embed)

            webhook.execute()

    def logs_wh(self, message):
        if self.logs_webhook_url is not None:
            webhook = DiscordWebhook(url=self.logs_webhook_url)

            embed = DiscordEmbed(
                title="ResMe System Robot",
                description="New ResMe System Notification",
                color="00f2ff",
            )

            embed.set_footer(text=f"Sent @ {datetime.now()}")

            embed.add_embed_field(name="Message", value=message)

            webhook.add_embed(embed)

            webhook.execute()
