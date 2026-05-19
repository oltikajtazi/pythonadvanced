class Personi:

    def __init__(self, emri, mosha, gjatesia, pesha):
        self.emri = emri
        self.mosha = int(mosha)
        self.gjatesia = float(gjatesia)
        self.pesha = float(pesha)


    @property


    def age(self):
        if self.mosha < 0:
         print("mosha nuk lejohet")
        else:
            print("mosha eshte e lejuar")




    def calculate_bmi(self):
        bmi = self.pesha / (self.gjatesia ** 2)
        return bmi

    def bmi_category(self):
        bmi = self.calculate_bmi()


        if self.mosha < 13:
            if bmi < 14:
                return "Underweight Child"
            elif bmi < 18:
                return "Normal weight Child"
            else:
                return "Overweight Child"

        elif self.mosha < 18:
            if bmi < 18:
                return "Underweight Teen"
            elif bmi < 25:
                return "Normal weight Teen"
            else:
                return "Overweight Teen"


        else:
            if bmi < 18.5:
                return "Underweight Adult"
            elif bmi < 24.9:
                return "Normal weight Adult"
            elif bmi < 29.9:
                return "Overweight Adult"
            else:
                return "Obese Adult"

    def prezantimi(self):
        print("Emri:", self.emri)
        print("Mosha:", self.mosha)
        print("BMI:", round(self.calculate_bmi(), 2))
        print("Category:", self.bmi_category())