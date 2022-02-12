import os


def area_finder():
    dic = {}
    for i in os.listdir('input'):
        if i[:5] == 'Field':
            with open('input\\' + i, mode='r') as file:
                p = 0
                h = 0
                text = file.read()
                k = text[1:len(text) - 1].replace(', (', '*(').split('*')
                sp = []
                for j in k:
                    f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                    sp.append(f)
                for j in range(len(sp) - 1):
                    p += sp[j][0] * sp[j + 1][1]
                    h += sp[j + 1][0] * sp[j][1]
                p += sp[-1][0] * sp[0][1]
                h += sp[0][0] * sp[-1][1]
                dic[int(i[5:i.index('.')])] = abs(p - h) * 0.5
    dic = dict(sorted(dic.items(), key=lambda x: x[0]))
    return dic