/**
 * Utilidade para ler arquivos (CSV, XLSX, ZIP) e extrair suas colunas
 */
import * as XLSX from 'xlsx';
import JSZip from 'jszip';

/**
 * Detecta o separador do CSV (,  ou ;)
 */
const detectSeparator = (text) => {
  const firstLine = text.split('\n')[0];
  const commaCount = (firstLine.match(/,/g) || []).length;
  const semicolonCount = (firstLine.match(/;/g) || []).length;
  return semicolonCount > commaCount ? ';' : ',';
};

/**
 * Lê um arquivo CSV e retorna as colunas
 */
export const readCSVFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const separator = detectSeparator(text);
        const lines = text.split('\n').filter(line => line.trim());
        const headers = lines[0].split(separator).map(h => h.trim());
        
        console.group(`📄 ${file.name}`);
        console.log('Tipo: CSV');
        console.log('Separador detectado:', separator === ',' ? 'Vírgula (,)' : 'Ponto-e-vírgula (;)');
        console.log('Colunas:', headers);
        console.log('Total de colunas:', headers.length);
        console.log('Linhas:', lines.length - 1);
        console.groupEnd();
        
        resolve({
          file: file.name,
          type: 'CSV',
          separator: separator,
          columns: headers,
          rows: lines.length - 1
        });
      } catch (error) {
        console.error('❌ Erro ao processar CSV:', error);
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsText(file, 'utf-8');
  });
};

/**
 * Lê um arquivo XLSX e retorna as colunas de cada sheet
 */
export const readXLSXFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        
        console.group(`📊 ${file.name}`);
        console.log('Tipo: XLSX');
        console.log('Sheets:', workbook.SheetNames.length);
        
        const sheets = {};
        workbook.SheetNames.forEach((sheetName) => {
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          
          // Pega as colunas a partir das chaves do primeiro objeto
          const columns = jsonData.length > 0 ? Object.keys(jsonData[0]) : [];
          const rows = jsonData.length;
          
          console.log(`  Sheet '${sheetName}':`);
          console.log(`    Colunas: ${columns.length}`);
          console.log('    ', columns);
          console.log(`    Linhas: ${rows}`);
          
          sheets[sheetName] = {
            columns: columns,
            rows: rows
          };
        });
        console.groupEnd();
        
        resolve({
          file: file.name,
          type: 'XLSX',
          sheets: sheets
        });
      } catch (error) {
        console.error('❌ Erro ao processar XLSX:', error);
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
};

/**
 * Lê um arquivo ZIP e lista seu conteúdo
 */
export const readZIPFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const zip = new JSZip();
        const zipData = await zip.loadAsync(e.target.result);
        
        console.group(`🗂️  ${file.name}`);
        console.log('Tipo: ZIP');
        
        const fileList = [];
        zipData.forEach((relativePath, file) => {
          console.log(`  - ${relativePath}`);
          fileList.push(relativePath);
        });
        
        console.log('Total de arquivos:', fileList.length);
        console.groupEnd();
        
        resolve({
          file: file.name,
          type: 'ZIP',
          contents: fileList
        });
      } catch (error) {
        console.error('❌ Erro ao processar ZIP:', error);
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
};

/**
 * Processa um arquivo baseado em sua extensão
 */
export const processUploadFile = async (file) => {
  const extension = file.name.split('.').pop().toLowerCase();
  
  try {
    console.log('');
    console.log('🚀 Iniciando leitura do arquivo...');
    console.log('');
    
    if (extension === 'csv') {
      return await readCSVFile(file);
    } else if (extension === 'xlsx' || extension === 'xls') {
      return await readXLSXFile(file);
    } else if (extension === 'zip') {
      return await readZIPFile(file);
    } else {
      throw new Error(`Formato de arquivo não suportado: ${extension}`);
    }
  } catch (error) {
    console.error('❌ Erro ao processar arquivo:', error.message);
    throw error;
  }
};
