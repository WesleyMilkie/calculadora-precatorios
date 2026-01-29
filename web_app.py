from flask import Flask, render_template, request, jsonify
from datetime import date, datetime
from typing import Dict, Tuple

app = Flask(__name__)

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
        "inicio_periodo_graca": inicio_graca.isoformat(),
        "fim_periodo_graca": fim_graca.isoformat(),
        "valor_principal": valor_homologado,
        "correcao_monetaria": round(correcao_total, 2),
        "juros_mora": round(mora_total, 2),
        "valor_total_acrescimos": round(correcao_total + mora_total, 2),
        "valor_total": round(valor_total, 2),
        "detalhamento": {
            "periodos_com_mora": [(inicio.isoformat(), fim.isoformat()) for inicio, fim in periodos_completos],
            "periodos_sem_mora": [(inicio.isoformat(), fim.isoformat()) for inicio, fim in periodos_so_correcao],
            "taxa_correcao_aa": taxa_correcao_anual,
            "taxa_mora_aa": taxa_mora_anual
        }
    }


@app.route('/')
def index():
    """Página inicial com o formulário"""
    return render_template('index.html')


@app.route('/calcular', methods=['POST'])
def calcular():
    """Endpoint para calcular o precatório"""
    try:
        dados = request.get_json()
        
        # Validar e converter dados
        valor_homologado = float(dados['valor_homologado'])
        data_base = datetime.strptime(dados['data_base'], '%Y-%m-%d').date()
        data_oficio = datetime.strptime(dados['data_oficio'], '%Y-%m-%d').date()
        data_final = datetime.strptime(dados['data_final'], '%Y-%m-%d').date()
        taxa_correcao = float(dados.get('taxa_correcao', 1.0))
        taxa_mora = float(dados.get('taxa_mora', 0.5))
        
        # Validações
        if valor_homologado <= 0:
            return jsonify({'erro': 'Valor homologado deve ser maior que zero'}), 400
        
        if data_base > data_final:
            return jsonify({'erro': 'Data-base deve ser anterior à data final'}), 400
        
        if data_oficio < data_base:
            return jsonify({'erro': 'Data do ofício deve ser posterior à data-base'}), 400
        
        # Calcular
        resultado = calcular_precatorio(
            valor_homologado=valor_homologado,
            data_base=data_base,
            data_oficio=data_oficio,
            data_final=data_final,
            taxa_correcao_anual=taxa_correcao,
            taxa_mora_anual=taxa_mora
        )
        
        return jsonify(resultado)
    
    except ValueError as e:
        return jsonify({'erro': f'Dados inválidos: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'erro': f'Erro ao calcular: {str(e)}'}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Servidor Flask iniciado!")
    print("=" * 80)
    print("\n📌 Acesse a aplicação em: http://localhost:5000")
    print("\n⚠️  Pressione CTRL+C para encerrar o servidor\n")
    print("=" * 80)
    app.run(debug=True, host='0.0.0.0', port=5000)
