import os

class Researcher():
    def __init__(self):
        self.file_locations = {}


    def fetch_locations(self, servername):
        '''Returns dict of file => list of paths, suitable for memoization of locationsfor().'''
        paths_by_file = {}

        pathbase = r"\\{}\c$\rsi".format(servername)
        def substitute_base(path):
            return "C:\\RSI" + path[len(pathbase):]

        for root, directories, files in os.walk(pathbase):
            for file in files:
                path = substitute_base(root + "\\" + file)
                paths_by_file.setdefault(file, []).append(path)

        return paths_by_file


    def locationsfor(self, filename, servername):
        '''Traverses C:\RSI on server and returns locations of files matching the given filename.'''
        if servername not in self.file_locations:
            self.file_locations[servername] = self.fetch_locations(servername)

        return self.file_locations[servername][filename]