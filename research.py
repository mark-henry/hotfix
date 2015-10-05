import os

class Research():
    def __init__(self):
        self._file_locations = {}


    def _fetch_locations(self, servername):
        '''Returns dict of file => list of paths, suitable for memoization of locationsfor().'''
        paths_by_file = {}

        pathbase = r'\\{}\c$\rsi'.format(servername)
        def substitute_base(path):
            return 'C:\\RSI' + path[len(pathbase):]

        if not os.path.isdir(pathbase):
            raise IOError('Server "{}" does not exist or insufficient permissions'.format(servername))

        for root, directories, files in os.walk(pathbase):
            for file in files:
                path = substitute_base(root + '\\' + file)
                paths_by_file.setdefault(file.lower(), []).append(path)

        return paths_by_file


    def locationsfor(self, filename, servername):
        '''Traverses C:\RSI on server and returns locations of files matching the given filename.'''
        if servername not in self._file_locations:
            self._file_locations[servername] = self._fetch_locations(servername)

        return self._file_locations[servername].get(filename.lower(), [])