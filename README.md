# Calculadora de Precatórios

Sistema para cálculo de atualização de precatórios com correção monetária e juros de mora, conforme as regras do CNJ.

## 📋 Descrição

Esta aplicação calcula a atualização de precatórios considerando:
- **Correção Monetária**: Aplicada em todos os períodos (padrão: 1% a.a.)
- **Juros de Mora**: Aplicados apenas fora do período de graça (padrão: 0,5% a.a.)
- **Período de Graça**: Suspende a incidência de juros de mora, mantendo a correção monetária

## ⚖️ Regimes Constitucionais

O sistema identifica automaticamente o regime aplicável com base na data do ofício requisitório:

- **CF (Constituição Federal)**: Ofícios até 15/12/2021
  - Período de graça: 1º de julho do ano até 31 de dezembro do ano seguinte

- **EC 114/2021**: Ofícios de 16/12/2021 até 09/09/2025
  - Período de graça: 1º de abril do ano até 31 de dezembro do ano seguinte

- **EC 136/2025**: Ofícios a partir de 10/09/2025
  - Período de graça: 1º de fevereiro do ano até 31 de dezembro do ano seguinte

## 🚀 Como Usar

### Versão Web (Interface Gráfica)

```bash
python web_app.py
```

Acesse: http://localhost:5000

### Versão Console

```bash
python app.py
```

## 📦 Requisitos

```bash
pip install flask
```

## 🛠️ Estrutura do Projeto

```
├── app.py              # Versão console com relatório detalhado
├── web_app.py          # Aplicação web Flask
├── templates/
│   └── index.html      # Interface web
├── static/
│   ├── style.css       # Estilos
│   └── script.js       # Lógica JavaScript
└── REGRA_DE_NEGOCIO_CNJ.md  # Documentação das regras
```

## 📊 Funcionalidades

- ✅ Cálculo automático de períodos de graça
- ✅ Divisão temporal precisa (antes, durante e depois da graça)
- ✅ Correção monetária contínua
- ✅ Juros de mora suspensos durante o período de graça
- ✅ Relatório detalhado com valores por período
- ✅ Interface web responsiva

## 📄 Licença

Este projeto está sob a licença MIT.
