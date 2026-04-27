from etl.extract.extract_decfec import extract_decfec
from etl.transform.transform_distribution_indices import transform_distribution_indices
from etl.transform.transform_energy_losses import transform_energy_losses
from pathlib import Path
import pandas as pd

# path1 = Path('/app/tmp/uploads/07999e393a474891b50a8622f0175fe8/indicadores-continuidade-coletivos-2020-2029.csv') 
path1 = Path('/app/tmp/uploads/07999e393a474891b50a8622f0175fe8/Base de Dados das Perdas de Energia nos Processos Tarifários.xlsx') 
# path1 = Path('/app/tmp/uploads/07999e393a474891b50a8622f0175fe8/gdb_extracted') 
# path1 = Path('/app/tmp/uploads/07999e393a474891b50a8622f0175fe8/indicadores-continuidade-coletivos-limite.csv') 

raw = transform_energy_losses(path1)

df = pd.DataFrame(raw)
print(df.head)
# result = transform_distribution_indices(df)

# docs = result.get('docs', [])
# rejected = result.get('rejected', [])

# print('Docs:', len(docs))
# print('Rejected:', len(rejected))

# if docs:
#     print('Primeiro doc:', docs[0])
# else:
#     print('Nenhum documento válido gerado')