class Personi:
    def __init__(self,emri,vitilindjes,gjinia):
        self.emri=emri
        self.vitiilindjes=vitilindjes
        self.gjinia = gjinia




    def prezantimi(self):
        print(f"unjam: { self.emri}, kam lindur ne vitin { self.vitiilindjes} dhe jam { self.gjinia}")


    def sayhi(self):
        print(f"pershendetje nga:{ self.emri}")