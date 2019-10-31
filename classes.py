class Bank:
    def __init__(self, name, root_url):
        self.name = name
        self.root_url = root_url
        self.snapshots = {
            '2010': [],
            '2011': [],
            '2012': [],
            '2013': [],
            '2014': [],
            '2015': [],
            '2016': [],
            '2017': [],
            '2018': []
        }


class Snapshot(dict):
    def __init__(self, timestamp=None, url=None):
        super(Snapshot, self).__init__()
        self['timestamp'] = timestamp
        self['url'] = url
        self['snapshot_url'] = 'http://web.archive.org/web/{timestamp}id_/{url}'.format(timestamp=timestamp, url=url)
