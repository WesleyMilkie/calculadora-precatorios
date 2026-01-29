from datetime import date
from typing import Dict, Tuple

def calcular_periodo_graca(data_oficio: date) -> Dict:
    """
    Determina o período de graça conforme o regime constitucional aplicável.
    
    Regimes:
    - CF: Ofícios até 15/12/2021 → Graça de julho do ano até dezembro do ano seguinte
    - EC 114: Ofícios de 16/12/2021 até 09/09/2025 → Graça de abril do ano até dezembro do ano seguinte
    - EC 136: Ofícios a partir de 10/09/2025 → Graça de fevereiro do ano até dezembro do ano seguinte
    """
    if data_oficio <= date(2021, 12, 15):
        # CF
        inicio = date(data_oficio.year, 7, 1)
        fim = date(data_oficio.year + 1, 12, 31)
        regime = "CF"
    elif date(2021, 12, 16) <= data_oficio <= date(2025, 9, 9):
        # EC 114
        inicio = date(data_oficio.year, 4, 1)
        fim = date(data_oficio.year + 1, 12, 31)
        regime = "EC 114"
    else:
        # EC 136
        inicio = date(data_oficio.year, 2, 1)
        fim = date(data_oficio.year + 1, 12, 31)
        regime = "EC 136"

    return {
        "regime": regime,
        "inicio_graca": inicio,
        "fim_graca": fim
    }


def calcular_correcao_simples(
    valor_base: float,
    data_inicio: date,
    data_fim: date,
    taxa_anual: float
) -> float:
    """
    Calcula correção monetária ou juros de mora usando taxa simples anual.
    
    Args:
        valor_base: Valor sobre o qual incide a taxa
        data_inicio: Data inicial do período
        data_fim: Data final do período
        taxa_anual: Taxa percentual ao ano (ex: 1.0 para 1% a.a.)
    
    Returns:
        Valor calculado com 2 casas decimais
    """
    if data_fim <= data_inicio:
        return 0.0
    
    dias = (data_fim - data_inicio).days
    valor = valor_base * (taxa_anual / 100) * (dias / 365)
    return round(valor, 2)


def calcular_periodos_aplicacao(
    data_base: date,
    data_final: date,
    inicio_graca: date,
    fim_graca: date
) -> Tuple[list, list]:
    """
    Divide a linha do tempo em períodos:
    - Períodos com correção + mora (fora do período de graça)
    - Períodos apenas com correção (durante o período de graça)
    
    Returns:
        Tuple com (periodos_completos, periodos_so_correcao)
        Cada período é uma tupla (data_inicio, data_fim)
    """
    periodos_completos = []  # Correção + Mora
    periodos_so_correcao = []  # Apenas Correção
    
    # Período 1: ANTES do período de graça (se existir)
    if data_base < inicio_graca:
        fim_periodo = min(inicio_graca, data_final)
        if fim_periodo > data_base:
            periodos_completos.append((data_base, fim_periodo))
    
    # Período 2: DURANTE o período de graça (apenas correção monetária)
    inicio_periodo_graca = max(data_base, inicio_graca)
    fim_periodo_graca = min(data_final, fim_graca)
    
    if fim_periodo_graca > inicio_periodo_graca:
        periodos_so_correcao.append((inicio_periodo_graca, fim_periodo_graca))
    
    # Período 3: DEPOIS do período de graça (se existir)
    if data_final > fim_graca:
        inicio_periodo = max(data_base, fim_graca)
        if data_final > inicio_periodo:
            periodos_completos.append((inicio_periodo, data_final))
    
    return periodos_completos, periodos_so_correcao


def calcular_precatorio(
    valor_homologado: float,
    data_base: date,
    data_oficio: date,
    data_final: date,
    taxa_correcao_anual: float = 1.0,
    taxa_mora_anual: float = 0.5
) -> Dict:
    """
    Calcula a atualização de precatório com correção monetária e juros de mora.
    
    Regra de cálculo:
    - Correção monetária: aplicada em TODOS os períodos
    - Juros de mora: aplicados APENAS fora do período de graça
    - Durante período de graça: SUSPENDE a mora, mantém a correção
    
    Args:
        valor_homologado: Valor principal do precatório
        data_base: Data da homologação/trânsito em julgado
        data_oficio: Data de expedição do ofício requisitório
        data_final: Data final para o cálculo
        taxa_correcao_anual: Taxa de correção monetária (padrão: 1% a.a.)
        taxa_mora_anual: Taxa de juros de mora (padrão: 0,5% a.a.)
    
    Returns:
        Dicionário com regime, períodos, valores detalhados
    """
    periodo = calcular_periodo_graca(data_oficio)
    
    inicio_graca = periodo["inicio_graca"]
    fim_graca = periodo["fim_graca"]
    
    # Dividir linha do tempo em períodos
    periodos_completos, periodos_so_correcao = calcular_periodos_aplicacao(
        data_base, data_final, inicio_graca, fim_graca
    )
    
    # Calcular correção monetária em TODOS os períodos
    correcao_total = 0.0
    
    # Correção nos períodos completos (fora do período de graça)
    for inicio, fim in periodos_completos:
        correcao_total += calcular_correcao_simples(
            valor_homologado, inicio, fim, taxa_correcao_anual
        )
    
    # Correção durante o período de graça
    for inicio, fim in periodos_so_correcao:
        correcao_total += calcular_correcao_simples(
            valor_homologado, inicio, fim, taxa_correcao_anual
        )
    
    # Calcular juros de mora APENAS fora do período de graça
    mora_total = 0.0
    
    for inicio, fim in periodos_completos:
        mora_total += calcular_correcao_simples(
            valor_homologado, inicio, fim, taxa_mora_anual
        )
    
    valor_total = valor_homologado + correcao_total + mora_total
    
    return {
        "regime": periodo["regime"],
        "inicio_periodo_graca": inicio_graca,
        "fim_periodo_graca": fim_graca,
        "valor_principal": valor_homologado,
        "correcao_monetaria": round(correcao_total, 2),
        "juros_mora": round(mora_total, 2),
        "valor_total_acrescimos": round(correcao_total + mora_total, 2),
        "valor_total": round(valor_total, 2),
        "detalhamento": {
            "periodos_com_mora": periodos_completos,
            "periodos_sem_mora": periodos_so_correcao,
            "taxa_correcao_aa": taxa_correcao_anual,
            "taxa_mora_aa": taxa_mora_anual
        }
    }


def imprimir_relatorio_detalhado(resultado: Dict, dados_entrada: Dict):
    """
    Imprime relatório detalhado do cálculo de precatório com logs separados.
    """
    print("=" * 80)
    print("📋 RELATÓRIO DE CÁLCULO DE PRECATÓRIO")
    print("=" * 80)
    
    # Dados de Entrada
    print("\n📌 DADOS DE ENTRADA:")
    print(f"   Valor Homologado: R$ {dados_entrada['valor_homologado']:,.2f}")
    print(f"   Data-base: {dados_entrada['data_base'].strftime('%d/%m/%Y')}")
    print(f"   Data do Ofício: {dados_entrada['data_oficio'].strftime('%d/%m/%Y')}")
    print(f"   Data Final: {dados_entrada['data_final'].strftime('%d/%m/%Y')}")
    
    # Regime Identificado
    print(f"\n⚖️  REGIME CONSTITUCIONAL: {resultado['regime']}")
    print(f"   Período de Graça: {resultado['inicio_periodo_graca'].strftime('%d/%m/%Y')} até {resultado['fim_periodo_graca'].strftime('%d/%m/%Y')}")
    
    # Taxas Aplicadas
    det = resultado['detalhamento']
    print(f"\n📊 TAXAS APLICADAS:")
    print(f"   Correção Monetária: {det['taxa_correcao_aa']}% a.a.")
    print(f"   Juros de Mora: {det['taxa_mora_aa']}% a.a.")
    
    # Divisão Temporal
    print("\n" + "=" * 80)
    print("📅 DIVISÃO TEMPORAL E CÁLCULOS POR PERÍODO")
    print("=" * 80)
    
    # Períodos COM mora (antes e depois da graça)
    if det['periodos_com_mora']:
        for idx, (inicio, fim) in enumerate(det['periodos_com_mora'], 1):
            dias = (fim - inicio).days
            periodo_tipo = "ANTES" if inicio < resultado['inicio_periodo_graca'] else "DEPOIS"
            
            correcao = dados_entrada['valor_homologado'] * (det['taxa_correcao_aa'] / 100) * (dias / 365)
            mora = dados_entrada['valor_homologado'] * (det['taxa_mora_aa'] / 100) * (dias / 365)
            
            print(f"\n🔹 Período {idx} - {periodo_tipo} DO PERÍODO DE GRAÇA")
            print(f"   Data Início: {inicio.strftime('%d/%m/%Y')}")
            print(f"   Data Fim: {fim.strftime('%d/%m/%Y')}")
            print(f"   Dias corridos: {dias}")
            print(f"   ✅ Correção Monetária: R$ {correcao:,.2f}")
            print(f"   ✅ Juros de Mora: R$ {mora:,.2f}")
            print(f"   Subtotal do período: R$ {correcao + mora:,.2f}")
    
    # Períodos SEM mora (durante a graça)
    if det['periodos_sem_mora']:
        for idx, (inicio, fim) in enumerate(det['periodos_sem_mora'], 1):
            dias = (fim - inicio).days
            correcao = dados_entrada['valor_homologado'] * (det['taxa_correcao_aa'] / 100) * (dias / 365)
            
            print(f"\n🔸 Período DURANTE O PERÍODO DE GRAÇA")
            print(f"   Data Início: {inicio.strftime('%d/%m/%Y')}")
            print(f"   Data Fim: {fim.strftime('%d/%m/%Y')}")
            print(f"   Dias corridos: {dias}")
            print(f"   ✅ Correção Monetária: R$ {correcao:,.2f}")
            print(f"   ❌ Juros de Mora: SUSPENSOS (R$ 0,00)")
            print(f"   Subtotal do período: R$ {correcao:,.2f}")
    
    # Totalizadores
    print("\n" + "=" * 80)
    print("💰 TOTALIZAÇÃO")
    print("=" * 80)
    print(f"   Valor Principal: R$ {resultado['valor_principal']:,.2f}")
    print(f"   (+) Correção Monetária Total: R$ {resultado['correcao_monetaria']:,.2f}")
    print(f"   (+) Juros de Mora Total: R$ {resultado['juros_mora']:,.2f}")
    print(f"   " + "-" * 60)
    print(f"   (=) Total de Acréscimos: R$ {resultado['valor_total_acrescimos']:,.2f}")
    print(f"   " + "=" * 60)
    print(f"   🎯 VALOR TOTAL DO PRECATÓRIO: R$ {resultado['valor_total']:,.2f}")
    print("=" * 80)
    print()


# Execução de teste com relatório detalhado
if __name__ == "__main__":
    dados = {
        'valor_homologado': 100000.00,
        'data_base': date(2021, 5, 10),
        'data_oficio': date(2022, 3, 20),
        'data_final': date(2026, 1, 29)
    }
    
    resultado = calcular_precatorio(**dados)
    
    imprimir_relatorio_detalhado(resultado, dados)
