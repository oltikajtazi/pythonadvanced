class Kurrizoret:
    def __init__(self, ka_kurriz=True):
        self.ka_kurriz = ka_kurriz


    def info(self):
        print("kafshet kurrizore lan shtyll kurrizore")



class Ujoret:
    def __init__(self, habitat="uji"):
        self.habitat = habitat

    def info(self):
        def info(self):
            print("kafshet ujore jetojn ne uje")


class Peshku (Kurrizoret,Ujoret):

    def __init__(self,lloji,ka_kurriz=True,habitat="uji"):
        super().__init__(ka_kurriz=ka_kurriz)

        self.habitat=habitat
        self.lloji=lloji

    def info(self):
        print(f"{self.lloji} eshte nje lloj peshk qe jeton ne{self.habitat}")



    def noton(self):
        print("peshku eshte duke notuar")


peshku = Peshku("peshku i arte")
print(peshku.ka_kurriz)
print(peshku.habitat)

peshku.info()



