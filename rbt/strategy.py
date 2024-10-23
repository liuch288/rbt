class Strategy(object):
    def __init__(self) -> None:
        self.dmus = None
        self.peus = None
        self.md_engine = None

    def register_dmu(self, dmu):
        self.dmus.append(dmu)
    
    def register_peu(self, peu):
        self.peus.append(peu)

    def register_md_engine(self, md_engine):
        self.md_engine = md_engine

    def run(self):
        new_md = self.md_engine