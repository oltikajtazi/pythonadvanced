class Animal:
    def sound(self):
        print("sound of the animal")




class Dog(Animal):

    def sound(self):
        print("ham ham")


class Cat(Animal):
    def sound(self):
        print("mewwwwww  mewwww")


animal = Animal()
animal.sound()

animal2 = Dog()
animal2.sound()

animal3 = Cat()
animal3.sound()
