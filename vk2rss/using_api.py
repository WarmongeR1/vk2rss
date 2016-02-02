# -*- encoding: utf-8 -*-
import pickle
import re
import textwrap
from functools import lru_cache

import vk
from feedgen.feed import FeedGenerator


def _(text):
    return r"<![CDATA[{}]]>".format(text)


@lru_cache()
def get_author_name(api, author_id: int):
    if author_id < 0:
        info = api.groups.getById(group_ids=abs(author_id), fields=['name', ])
        assert len(info) == 1
        group_info = info[0]
        result = group_info.get('name', 'Аноним')
    else:
        info = api.users.get(user_ids=author_id, fields=['first_name', 'last_name'])
        assert len(info) == 1
        user_info = info[0]
        result = '{} {}'.format(user_info.get('first_name', 'Аноним'), user_info.get('last_name', 'Анонимов'))
    return result


def main():
    session = vk.Session()
    api = vk.API(session)

    group_id = '96469126'

    group_info = api.groups.getById(group_ids=group_id, fields=['description', 'site', 'name', 'photo', 'gid'])

    assert len(group_info) == 1
    group_info = group_info[0]

    url = 'http://vk.com/club{}'.format(group_info['gid'])
    # a = api.wall.get(owner_id=-1 * group_info['gid'])
    #
    # with open('out', 'wb') as fio:
    #     pickle.dump(a, fio)

    with open('out', 'rb') as fio:
        data = pickle.loads(fio.read())

    assert len(data) > 1

    fg = FeedGenerator()
    fg.id(url)
    fg.title(_(group_info['name']))
    fg.description(_(group_info['description']))
    fg.logo(group_info['photo'])
    site_url = group_info.get('site', url) if group_info.get('site', url) else url
    fg.link(href=_(site_url))
    fg.link(href=_(site_url), rel='self')
    fg.link(href=_(site_url), rel='alternate')
    fg.author({'name': 'Alexander Sapronov', 'email': 'a@sapronov.me'})
    fg.webMaster('a@sapronov.me (Alexander Sapronov)')

    pat = re.compile(r"#(\w+)")

    for x in data[1:]:
        post_link = "{}?w=wall-{}_{}".format(url, group_info['gid'], x['id'])
        e = fg.add_entry()
        # text = x.get('text', '').replace('<br>', '\n')
        text = x.get('text', '')

        e.description(_(text))
        e.author({'name': _(get_author_name(api, x.get('from_id')))})
        e.id(post_link)
        e.link(href=_(post_link))
        e.link(href=_(post_link), rel='alternate')

        tags = pat.findall(text)

        title = x.get('text', '')
        for tag in tags:
            e.category(term=_(tag))
            title = title.replace('#{}'.format(tag), '')

        title = re.sub('<[^<]+?>', ' ', title)
        title = textwrap.wrap(title, width=80)[0]
        e.title(_(title.strip()))

    fg.rss_file('rss.xml')


if __name__ == '__main__':
    main()
