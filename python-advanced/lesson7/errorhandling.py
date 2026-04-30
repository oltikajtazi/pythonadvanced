from logging import exception

numri = 10

numri1 = 0

try:
    rezultati = numri/numri1

except ZeroDivisionError:
    print("hejj nuk munesh me pjestu me 00")










numri = 10

numri2 = 2

try:
    rezultati = numri/numri2

except ZeroDivisionError:
    print("hejj nuk munesh me pjestu me 00")

else:
    print("pjestimi eshte i pranueshem")


print(rezultati)



mesazhi = "hello"
try:
    textToint = int(mesazhi)

except Exception as e:
    print("ka ndodh ndonje error")



def devide_number(a,b):
    try:
        result9 = a/b
        print("rezultati eshte :",result9)

    except ZeroDivisionError:
        print("hej ke tentu me pojestu me zero")

    except TypeError:
        print("invalide type of devision")

    except Exception as a:
        print("ka ndodhe nje error", a)


devide_number(10,5)
devide_number(12,6)
devide_number(45,2)



