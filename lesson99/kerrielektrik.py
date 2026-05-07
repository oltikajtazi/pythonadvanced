from kerri import Kerri


class Kerrielektrik(Kerri):
    def __init__(self,emri,viti,modeli,bateria):
        super().__init__(emri,viti,modeli)
        self.bateria=bateria






    def shpejciporritet(self):
        print("kerri elektrik eshte duke e rritur shpejcin")



    def mbushebaterin(self):
        print("mbushe baterin")
