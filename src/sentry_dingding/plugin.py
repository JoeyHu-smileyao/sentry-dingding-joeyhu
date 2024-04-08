# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin
from collections import defaultdict
import sentry_dingding
from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'ansheng'
    author_url = 'https://github.com/JoeyHu-smileyao/sentry-dingding-joeyhu'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/JoeyHu-smileyao/sentry-dingding-joeyhu'),
        ('Bug Tracker', 'https://github.com/JoeyHu-smileyao/sentry-dingding-joeyhu/issues'),
        ('README', 'https://github.com/JoeyHu-smileyao/sentry-dingding-joeyhu/blob/master/README.md'),
    ]

    slug = 'DingDing'
    title = 'DingDing'
    conf_key = slug
    conf_title = title
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        send_url = DingTalk_API.format(token=access_token)
        title = u"New alert from {}".format(event.project.slug)
        #print(event.data.__dict__)
        #print(event.data.__str__)
        the_tags = defaultdict(lambda: '[NA]')
        the_tags.update({k:v for k, v in event.tags})
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": u"title: {tags[title]}  <br>serviceName: {tags[serviceName]}  <br>traceId: {tags[traceId]}  <br>url: <a href = {url}>{url}</a>  <br>errorCode: {tags[errorCode]}  <br>message: {message}".format(
                    title=title,
                    message=event.message,
                    tags=the_tags,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.id),
                )
            }
        }
        requests.post(
            url=send_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8")
        )
