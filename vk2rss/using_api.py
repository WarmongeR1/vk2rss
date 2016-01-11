# -*- encoding: utf-8 -*-
import pickle
import re
import textwrap

import vk
from feedgen.feed import FeedGenerator


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
    fg.title(group_info['name'])
    fg.description(group_info['description'])
    fg.logo(group_info['photo'])
    fg.link(href=group_info.get('site', url) if group_info.get('site', url) else url)
    fg.link(href=group_info.get('site', url) if group_info.get('site', url) else url, rel='self')
    fg.link(href=group_info.get('site', url) if group_info.get('site', url) else url, rel='alternate')

    for x in data[1:]:
        e = fg.add_entry()
        title = x.get('text', '')
        title = re.sub('<[^<]+?>', ' ', title)
        title = textwrap.wrap(title, width=80)[0]

        text = x.get('text', '').replace('<br>', '\n')
        e.title(title)
        e.description(r"<![CDATA[ {} ]]>".format(text))
        e.id("{}?w=wall-{}_{}".format(url, group_info['gid'], x['id']))

    fg.rss_file('rss.xml')


if __name__ == '__main__':
    main()
