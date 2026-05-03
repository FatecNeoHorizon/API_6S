from src.etl.extract.extract_decfec import extract_decfec
from src.etl.transform.transform_decfec import transform_decfec
from src.etl.transform.transform_energy_losses import transform_energy_losses
from pathlib import Path
import pandas as pd

path = Path('/app/tmp/uploads/1ae0dd2aa98c49f0a4d4ac4f76b84867/Base de Dados das Perdas de Energia nos Processos Tarifários.xlsx') 

df = pd.read_excel(path, header=2)

result = transform_energy_losses(df)

docs = result.get("docs", [])
rejected = result.get("rejected", [])

print("Docs:", len(docs))
print("Rejected:", len(rejected))

if docs:
    print("Primeiro doc:", docs[0])
else:
    print("Nenhum documento válido gerado")