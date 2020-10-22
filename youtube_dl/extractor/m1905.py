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
    compat_urllib_parse_unquote_plus,
    compat_urllib_parse
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
                'nonce': int(time.time()),
                'expiretime': int(time.time())+600,
                'cid': video_id,
                'uuid': '09699053-4b9c-40a9-9231-908ee8a1f5b2',
                'playerid': '897249252991526',
                'page': url,
                'type': 'mp4'
            }
            params['signature'] = self._signature(params, 'dde3d61a0411511d')
            params['callback'] = 'fnCallback0'
            content, urlh = self._download_webpage_handle('https://profile.m1905.com/mvod/getVideoinfo.php', video_id, query=params)
            content = content[12:-1]
            api_data = self._parse_json(content, video_id)['data']
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 401:
                error = self._parse_json(e.cause.read().decode(), None)
                if error.get('code') == 40005:
                    self.raise_geo_restricted(countries=self._GEO_COUNTRIES)
                raise ExtractorError(error['msg'], expected=True)
            raise
        quality = ['sd', 'hd', 'uhd']
        formats = []
        for q in quality:
            formats.append({
                'format_id': compat_str(q),
                'url': api_data['quality'][q]['host']+api_data['sign'][q]['sign']+api_data['path'][q]['path'],
                'ext': 'mp4',
                'protocol': 'https',
                'http_headers': {
                    'Referer': url,
                }
            })
        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': api_data['title'],
            'formats': formats
        }


    def _signature(self, p, appid):
        s = ''
        for k in sorted(p):
            if len(s) > 0:
                s += '&'
            s += (k + '=' + compat_urllib_parse.quote_plus(compat_str(p[k])))
        return hashlib.sha1((s + '.' + appid).encode()).hexdigest()
