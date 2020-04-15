import csv
import pandas as pd 

file_name_str = 'C:\\Users\\ww\\Desktop\\程序设计实践\\Japanese_word.csv'

df = pd.read_csv(file_name_str, encoding='utf-8')
print(df.info())
df = df.sort_values(by=["step1", "step2"])
df["example"] = df["example"].str.replace("<b>","")
df["example"] = df["example"].str.replace("</b>","")
result = pd.concat([df['kanji'], df['meaning'], df['property'],
         df['example'], df['example_meaning'], df['step1'], df['step2']], axis=1, ignore_index=True)
print(result)
result.to_csv("C:\\Users\\ww\\Desktop\\程序设计实践\\new.csv",index = 0, header=False)