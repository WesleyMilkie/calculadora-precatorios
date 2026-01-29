# 📋 REGRA DE NEGÓCIO – ATUALIZAÇÃO DE PRECATÓRIOS
## Documento de Especificação Técnica e Jurídica

**Versão:** 1.0  
**Data:** 29 de janeiro de 2026  
**Fundamento Legal:** Constituição Federal, EC 114/2021, EC 136/2025  
**Órgão Normativo:** Conselho Nacional de Justiça (CNJ)

---

## 1. OBJETIVO

Estabelecer os critérios técnicos e jurídicos para cálculo de atualização monetária e juros de mora em precatórios, observando os regimes constitucionais vigentes e o período de graça orçamentário.

---

## 2. FUNDAMENTO CONSTITUCIONAL

### 2.1. Período de Graça Constitucional

O **período de graça** é o intervalo temporal concedido ao ente público para inclusão do precatório no orçamento e posterior pagamento, durante o qual **não há incidência de juros de mora**, mas **há incidência normal de correção monetária**.

### 2.2. Regimes Aplicáveis

A definição do período de graça depende **exclusivamente da data de expedição do ofício requisitório**:

| Regime | Data do Ofício Requisitório | Início do Período de Graça | Término do Período de Graça |
|--------|----------------------------|----------------------------|------------------------------|
| **CF** | Até 15/12/2021 | 1º de julho do ano da expedição | 31 de dezembro do ano seguinte |
| **EC 114/2021** | 16/12/2021 até 09/09/2025 | 1º de abril do ano da expedição | 31 de dezembro do ano seguinte |
| **EC 136/2025** | A partir de 10/09/2025 | 1º de fevereiro do ano da expedição | 31 de dezembro do ano seguinte |

---

## 3. ÍNDICES DE ATUALIZAÇÃO

### 3.1. Histórico de Índices (Referência Jurídica)

Embora o sistema judicial utilize índices distintos por período histórico, **para fins operacionais desta implementação**, são adotados **índices padronizados** conforme especificação técnica:

#### 📌 Índices Históricos (Referência Jurisprudencial)

| Período | Índice de Correção | Base Legal |
|---------|-------------------|------------|
| 10/12/2009 a 25/03/2015 | Taxa Referencial (TR) | Resolução CNJ |
| 26/03/2015 a 30/11/2021 | IPCA-E (IBGE) | Declaração STF de inconstitucionalidade da TR |
| A partir de 01/12/2021 | SELIC | Tese STF - Índice único (correção + mora) |

#### 📌 Índices Operacionais (Implementação Padrão)

Para fins de **cálculo simplificado e auditável**, esta implementação adota:

- **Correção monetária:** 1,0% ao ano (taxa simples)
- **Juros de mora:** 0,5% ao ano (taxa simples)

> ⚠️ **Nota Técnica:** A substituição dos índices oficiais por taxas fixas visa **facilitar a auditoria, transparência e validação dos cálculos**. Implementações futuras podem integrar índices oficiais (IPCA-E, SELIC) mediante consulta a APIs públicas (BACEN, IBGE).

---

## 4. REGRAS DE CÁLCULO

### 4.1. Linha do Tempo de Cálculo

O cálculo é realizado com base em **três datas fundamentais**:

1. **Data-base (homologação/trânsito em julgado):** Início da contagem
2. **Data de expedição do ofício requisitório:** Define o regime e período de graça
3. **Data final de cálculo:** Término da atualização

### 4.2. Divisão Temporal

A linha do tempo é dividida em **períodos distintos de aplicação**:

#### 📊 Período 1: ANTES do Período de Graça

- **Quando ocorre:** Entre a data-base e o início do período de graça
- **Aplicação:**
  - ✅ Correção monetária (1% a.a.)
  - ✅ Juros de mora (0,5% a.a.)
- **Taxa efetiva:** 1,5% ao ano

#### 📊 Período 2: DURANTE o Período de Graça

- **Quando ocorre:** Do início ao término do período de graça
- **Aplicação:**
  - ✅ Correção monetária (1% a.a.)
  - ❌ Juros de mora **SUSPENSOS**
- **Taxa efetiva:** 1,0% ao ano
- **Fundamento:** Não há mora durante prazo constitucional concedido ao ente público

#### 📊 Período 3: DEPOIS do Período de Graça

- **Quando ocorre:** Após o término do período de graça até a data final
- **Aplicação:**
  - ✅ Correção monetária (1% a.a.)
  - ✅ Juros de mora (0,5% a.a.) **RETOMADOS**
- **Taxa efetiva:** 1,5% ao ano

---

## 5. FÓRMULA DE CÁLCULO

### 5.1. Cálculo de Correção Monetária ou Juros de Mora

Para cada período:

```
Valor = Valor_Principal × (Taxa_Anual / 100) × (Dias_Corridos / 365)
```

Onde:
- **Valor_Principal:** Valor homologado do precatório
- **Taxa_Anual:** Taxa percentual ao ano (1,0% para correção ou 0,5% para mora)
- **Dias_Corridos:** Quantidade de dias entre data inicial e data final do período
- **365:** Base anual (ano civil)

### 5.2. Cálculo Total

```
Valor_Total = Valor_Principal + Correção_Total + Mora_Total
```

Onde:
- **Correção_Total:** Soma da correção de todos os períodos (inclusive período de graça)
- **Mora_Total:** Soma da mora apenas dos períodos FORA do período de graça

---

## 6. PRINCÍPIOS TÉCNICOS

### 6.1. Separação de Componentes

A atualização é composta de **dois componentes distintos e independentes**:

1. **Correção monetária:** Recomposição do poder aquisitivo da moeda
   - Aplicada **continuamente** em todos os períodos
   - **Não é suspensa** durante o período de graça

2. **Juros de mora:** Penalidade pela mora no cumprimento da obrigação
   - Aplicada **apenas fora do período de graça**
   - **Suspensa durante** o período de graça constitucional

### 6.2. Regime da SELIC (Referência Jurídica)

Quando aplicável o índice SELIC (a partir de 12/2021):

- A SELIC é **índice único** que engloba simultaneamente:
  - Correção monetária
  - Juros moratórios
- Durante o período de graça:
  - A SELIC continua sendo aplicada
  - Porém, **somente na parcela correspondente à correção monetária**
  - A parcela de mora fica suspensa

> 📌 **Nota Operacional:** Na implementação com taxas fixas (1% + 0,5%), essa distinção é explícita e automatizada.

---

## 7. EXEMPLOS PRÁTICOS

### 7.1. Exemplo 1 – Regime EC 114

**Dados do Precatório:**
- Valor homologado: R$ 100.000,00
- Data-base: 10/05/2021
- Data do ofício: 20/03/2022
- Data final: 31/12/2025

**Regime Identificado:** EC 114

**Período de Graça:**
- Início: 01/04/2022
- Término: 31/12/2023

**Divisão Temporal:**

| Período | Data Início | Data Fim | Tipo | Dias | Correção | Mora |
|---------|-------------|----------|------|------|----------|------|
| Antes da Graça | 10/05/2021 | 01/04/2022 | Completo | 326 | ✅ | ✅ |
| Durante a Graça | 01/04/2022 | 31/12/2023 | Sem Mora | 640 | ✅ | ❌ |
| Depois da Graça | 31/12/2023 | 31/12/2025 | Completo | 731 | ✅ | ✅ |

**Cálculo:**

1. **Correção Monetária Total:**
   - Período 1: 100.000 × 1% × (326/365) = R$ 893,15
   - Período 2: 100.000 × 1% × (640/365) = R$ 1.753,42
   - Período 3: 100.000 × 1% × (731/365) = R$ 2.002,74
   - **Total:** R$ 4.649,31

2. **Juros de Mora Total:**
   - Período 1: 100.000 × 0,5% × (326/365) = R$ 446,58
   - Período 2: **SUSPENSO** = R$ 0,00
   - Período 3: 100.000 × 0,5% × (731/365) = R$ 1.001,37
   - **Total:** R$ 1.447,95

3. **Valor Total:**
   - Principal: R$ 100.000,00
   - Correção: R$ 4.649,31
   - Mora: R$ 1.447,95
   - **Total: R$ 106.097,26**

---

## 8. CHECKLIST DE VALIDAÇÃO

### ✅ Checklist para Auditoria de Cálculo

- [ ] **1. Identificação do Regime**
  - [ ] Data do ofício foi corretamente identificada?
  - [ ] Regime constitucional aplicado corresponde à data do ofício?

- [ ] **2. Período de Graça**
  - [ ] Data de início do período de graça está correta?
  - [ ] Data de término do período de graça está correta?

- [ ] **3. Divisão Temporal**
  - [ ] Períodos antes, durante e depois da graça foram identificados?
  - [ ] Não há sobreposição de períodos?
  - [ ] Não há lacunas temporais entre períodos?

- [ ] **4. Aplicação de Correção Monetária**
  - [ ] Correção foi aplicada em TODOS os períodos?
  - [ ] Taxa de correção está correta (1% a.a.)?
  - [ ] Cálculo de dias está correto?

- [ ] **5. Aplicação de Juros de Mora**
  - [ ] Mora foi aplicada APENAS nos períodos fora do período de graça?
  - [ ] Mora foi SUSPENSA durante o período de graça?
  - [ ] Taxa de mora está correta (0,5% a.a.)?

- [ ] **6. Cálculo Final**
  - [ ] Soma das parcelas está correta?
  - [ ] Valores estão arredondados para 2 casas decimais?
  - [ ] Valor total = Principal + Correção + Mora?

- [ ] **7. Documentação**
  - [ ] Todos os períodos estão documentados?
  - [ ] Base de cálculo está explícita?
  - [ ] Taxas aplicadas estão informadas?

---

## 9. CASOS ESPECIAIS

### 9.1. Data-base dentro do período de graça

Se a data-base (homologação) ocorrer **durante o período de graça**:

- **Regra:** Aplica-se apenas correção monetária até o fim do período de graça
- **Mora:** Inicia-se somente após o término do período de graça

### 9.2. Data-base após o período de graça

Se a data-base ocorrer **após o término do período de graça**:

- **Regra:** Aplica-se correção + mora desde o início (data-base)
- **Período de graça:** Não afeta o cálculo

### 9.3. Data final dentro do período de graça

Se a data final de cálculo ocorrer **durante o período de graça**:

- **Regra:** Considera-se apenas correção monetária
- **Mora:** Não há período com mora

---

## 10. GLOSSÁRIO TÉCNICO

| Termo | Definição |
|-------|-----------|
| **Correção Monetária** | Recomposição do poder de compra da moeda, aplicada continuamente |
| **Juros de Mora** | Penalidade pelo atraso no cumprimento da obrigação pecuniária |
| **Período de Graça** | Intervalo constitucional sem incidência de mora |
| **Data-base** | Data da homologação ou trânsito em julgado da decisão |
| **Ofício Requisitório** | Documento oficial que requisita o pagamento do precatório |
| **Taxa Simples** | Cálculo proporcional linear (não composto) |
| **Regime Constitucional** | Conjunto de regras da CF ou EC aplicável ao precatório |

---

## 11. RESPONSABILIDADE TÉCNICA

Este documento especifica a regra de negócio implementada no sistema de cálculo de precatórios.

**Responsável Técnico:** Sistema de Cálculo de Precatórios  
**Linguagem:** Python 3.14  
**Arquivo de Implementação:** `app.py`

---

## 12. REFERÊNCIAS NORMATIVAS

1. Constituição Federal de 1988 – Art. 100
2. Emenda Constitucional nº 114/2021
3. Emenda Constitucional nº 136/2025
4. Resoluções do Conselho Nacional de Justiça (CNJ)
5. Jurisprudência do Supremo Tribunal Federal (STF)

---

## 13. CONTROLE DE VERSÕES

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 29/01/2026 | Versão inicial – Implementação com taxas fixas |

---

**Documento gerado automaticamente pelo Sistema de Cálculo de Precatórios**  
**Última atualização:** 29 de janeiro de 2026
