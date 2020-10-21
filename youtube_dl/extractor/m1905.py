# coding: utf-8

import base64
import time
import uuid
import hashlib

from .common import InfoExtractor
from ..compat import (
    compat_HTTPError,
    compat_str,
    compat_urllib_parse_urlencode,
)
from ..utils import (
    ExtractorError,
    int_or_none,
)


class M1905IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?1905\.com/video/play/(?P<id>\d+)\.shtml'
    IE_DESC = '电影频道'
    _GEO_COUNTRIES = ['CN']

    def _real_extract(self, url):
        video_id = self._match_id(url)
        try:
            params = {
                'nonce': '1603288973',
                'expiretime': '1603289573',
                'cid': '1485702',
                'uuid': '09699053-4b9c-40a9-9231-908ee8a1f5b2',
                'playerid': '897249252991526',
                'page': 'https://www.1905.com/video/play/1485702.shtml',
                'type': 'mp4'
            }
            params['signature'] = self._signature(params, 'dde3d61a0411511d')
            self.to_screen('params %s' % params)
            api_data = self._download_json(
                'https://profile.m1905.com/mvod/getVideoinfo.php', video_id, query=params)['data']
            self.to_screen('api_data %s' % api_data)
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 401:
                error = self._parse_json(e.cause.read().decode(), None)
                if error.get('code') == 40005:
                    self.raise_geo_restricted(countries=self._GEO_COUNTRIES)
                raise ExtractorError(error['msg'], expected=True)
            raise

    def _signature(self, p, appid):
        s = ''
        for k in sorted(p):
            if len(s) > 0:
                s += '&'
            s += (k + '=' + compat_str(p[k]))
        self.to_screen(s)
        return hashlib.sha1((s + '.' + appid).encode()).hexdigest()
