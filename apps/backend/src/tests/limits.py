from src.etl.transform.transform_limits import transform_limits
from pathlib import Path
import pandas as pd

path1 = Path('/app/tmp/uploads/1ae0dd2aa98c49f0a4d4ac4f76b84867/indicadores-continuidade-coletivos-limite.csv') 

df = pd.read_csv(path1, header=None, encoding="latin1", sep=";")

result = transform_limits(df)

docs = result.get("docs", [])
rejected = result.get("rejected", [])

print("Docs:", len(docs))
print("Rejected:", len(rejected))

if docs:
    print("Primeiro doc:", docs[0])
else:
    print("Nenhum documento válido gerado")