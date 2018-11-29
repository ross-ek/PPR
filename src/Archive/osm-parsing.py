import osmium as osm
import pandas as pd

class TimelineHandler(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.elemtimeline = []

    def node(self, n):
        self.elemtimeline.append(["node",
                                  n.id,
                                  n.version,
                                  n.visible,
                                  pd.Timestamp(n.timestamp),
                                  n.uid,
                                  n.changeset,
                                  len(n.tags)])

tlhandler = TimelineHandler()
tlhandler.apply_file("./data/input/ireland-and-northern-ireland.osm.pbf")
colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid', 'chgset', 'ntags']
elements = pd.DataFrame(tlhandler.elemtimeline, columns=colnames)
elements = elements.sort_values(by=['type', 'id', 'ts'])
print(elements.head(10))

# elements.to_csv("./data/output/ireland.csv", date_format='%Y-%m-%d %H:%M:%S')