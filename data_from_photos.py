import os
import pandas as pd


def custom_key(number):
    return int(number[1])


def data_maker():
    data = []
    dic = {}
    for i in os.listdir('input'):
        sp = []
        if i[:4] == 'Foto':
            k = i[5:]
            sp.append(int(k[:k.index('_')]))
            k = k[k.index('_') + 1:]
            sp.append(int(k[:k.index('_')]))
            k = k[k.index('_') + 1:]
            sp.append(int(k[:k.index('_')]))
            k = k[k.index('_') + 1:]
            sp.append(int(k[:k.index('_')]))
            k = k[k.index('_') + 1:]
            sp.append(int(k[:k.index('.')]) / 100)
            a = int(k[:k.index('.')]) / 100 - 1.05
            sp.append(((1.73205 * a) * 2) * ((0.70020 * a) * 2))
            try:
                dic[int(sp[0])].append(sp)
            except Exception:
                dic[int(sp[0])] = []
                dic[int(sp[0])].append(sp)
    dic = dict(sorted(dic.items(), key=lambda x: x[0]))
    for i in dic.keys():
        k = dic[i]
        k.sort(key=custom_key)
        for j in dic[i]:
            data.append(j)
    return pd.DataFrame(data,
                        columns=['Field_Number', 'Number_of_Photo_on_This_Field', 'X(м)', 'Y(м)',
                                 'Heigt(м)', 'Photo_Area(м^2)'])


print(data_maker())
