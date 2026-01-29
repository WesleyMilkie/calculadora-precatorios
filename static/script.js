document.getElementById('calculadoraForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Coletar dados do formulário
    const formData = {
        valor_homologado: parseFloat(document.getElementById('valor_homologado').value),
        data_base: document.getElementById('data_base').value,
        data_oficio: document.getElementById('data_oficio').value,
        data_final: document.getElementById('data_final').value,
        taxa_correcao: parseFloat(document.getElementById('taxa_correcao').value),
        taxa_mora: parseFloat(document.getElementById('taxa_mora').value)
    };
    
    // Mostrar loading
    const resultadoArea = document.getElementById('resultadoArea');
    resultadoArea.style.display = 'block';
    resultadoArea.innerHTML = '<div class="loading">⏳ Calculando...</div>';
    
    try {
        // Fazer requisição para o backend
        const response = await fetch('/calcular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            exibirResultado(data, formData);
        } else {
            resultadoArea.innerHTML = `<div class="card"><p style="color: red;">❌ Erro: ${data.erro}</p></div>`;
        }
    } catch (error) {
        resultadoArea.innerHTML = `<div class="card"><p style="color: red;">❌ Erro ao calcular: ${error.message}</p></div>`;
    }
});

function formatarData(dataStr) {
    const [ano, mes, dia] = dataStr.split('-');
    return `${dia}/${mes}/${ano}`;
}

function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function exibirResultado(resultado, entrada) {
    const resultadoArea = document.getElementById('resultadoArea');
    resultadoArea.style.display = 'block';
    
    // Dados de Entrada
    const dadosEntrada = `
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Valor Homologado:</span>
                <span class="info-value">${formatarMoeda(entrada.valor_homologado)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Data-base:</span>
                <span class="info-value">${formatarData(entrada.data_base)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Data do Ofício:</span>
                <span class="info-value">${formatarData(entrada.data_oficio)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Data Final:</span>
                <span class="info-value">${formatarData(entrada.data_final)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Taxa de Correção:</span>
                <span class="info-value">${entrada.taxa_correcao}% a.a.</span>
            </div>
            <div class="info-item">
                <span class="info-label">Taxa de Mora:</span>
                <span class="info-value">${entrada.taxa_mora}% a.a.</span>
            </div>
        </div>
    `;
    
    // Regime Constitucional
    const regimeInfo = `
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">Regime Aplicável:</span>
                <span class="info-value"><strong>${resultado.regime}</strong></span>
            </div>
            <div class="info-item">
                <span class="info-label">Início do Período de Graça:</span>
                <span class="info-value">${formatarData(resultado.inicio_periodo_graca)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Término do Período de Graça:</span>
                <span class="info-value">${formatarData(resultado.fim_periodo_graca)}</span>
            </div>
        </div>
    `;
    
    // Períodos de Cálculo
    let periodosHtml = '';
    
    // Períodos com mora
    const det = resultado.detalhamento;
    if (det.periodos_com_mora && det.periodos_com_mora.length > 0) {
        det.periodos_com_mora.forEach((periodo, idx) => {
            const inicio = periodo[0];
            const fim = periodo[1];
            const dias = calcularDias(inicio, fim);
            const tipo = new Date(inicio) < new Date(resultado.inicio_periodo_graca) ? 'ANTES' : 'DEPOIS';
            
            const correcao = entrada.valor_homologado * (entrada.taxa_correcao / 100) * (dias / 365);
            const mora = entrada.valor_homologado * (entrada.taxa_mora / 100) * (dias / 365);
            
            periodosHtml += `
                <div class="periodo">
                    <div class="periodo-header">🔹 Período ${tipo} do Período de Graça</div>
                    <div class="periodo-info">
                        <div class="periodo-linha">
                            <span>Data Início:</span>
                            <strong>${formatarData(inicio)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>Data Fim:</span>
                            <strong>${formatarData(fim)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>Dias corridos:</span>
                            <strong>${dias} dias</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>✅ Correção Monetária:</span>
                            <strong>${formatarMoeda(correcao)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>✅ Juros de Mora:</span>
                            <strong>${formatarMoeda(mora)}</strong>
                        </div>
                        <div class="periodo-linha" style="border-top: 1px solid #ddd; margin-top: 5px; padding-top: 8px;">
                            <span><strong>Subtotal:</strong></span>
                            <strong>${formatarMoeda(correcao + mora)}</strong>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    // Períodos sem mora
    if (det.periodos_sem_mora && det.periodos_sem_mora.length > 0) {
        det.periodos_sem_mora.forEach((periodo, idx) => {
            const inicio = periodo[0];
            const fim = periodo[1];
            const dias = calcularDias(inicio, fim);
            
            const correcao = entrada.valor_homologado * (entrada.taxa_correcao / 100) * (dias / 365);
            
            periodosHtml += `
                <div class="periodo sem-mora">
                    <div class="periodo-header">🔸 Período DURANTE o Período de Graça</div>
                    <div class="periodo-info">
                        <div class="periodo-linha">
                            <span>Data Início:</span>
                            <strong>${formatarData(inicio)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>Data Fim:</span>
                            <strong>${formatarData(fim)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>Dias corridos:</span>
                            <strong>${dias} dias</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>✅ Correção Monetária:</span>
                            <strong>${formatarMoeda(correcao)}</strong>
                        </div>
                        <div class="periodo-linha">
                            <span>❌ Juros de Mora:</span>
                            <strong>SUSPENSOS (R$ 0,00)</strong>
                        </div>
                        <div class="periodo-linha" style="border-top: 1px solid #ddd; margin-top: 5px; padding-top: 8px;">
                            <span><strong>Subtotal:</strong></span>
                            <strong>${formatarMoeda(correcao)}</strong>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    // Resultado Final
    const resultadoFinal = `
        <div class="totalizacao">
            <div class="total-linha">
                <span>Valor Principal:</span>
                <strong>${formatarMoeda(resultado.valor_principal)}</strong>
            </div>
            <div class="total-linha">
                <span>(+) Correção Monetária Total:</span>
                <strong>${formatarMoeda(resultado.correcao_monetaria)}</strong>
            </div>
            <div class="total-linha">
                <span>(+) Juros de Mora Total:</span>
                <strong>${formatarMoeda(resultado.juros_mora)}</strong>
            </div>
            <div class="total-linha">
                <span>(=) Total de Acréscimos:</span>
                <strong>${formatarMoeda(resultado.valor_total_acrescimos)}</strong>
            </div>
            <div class="total-linha destaque">
                <span>🎯 VALOR TOTAL DO PRECATÓRIO:</span>
                <strong>${formatarMoeda(resultado.valor_total)}</strong>
            </div>
        </div>
    `;
    
    // Montar o HTML completo
    resultadoArea.innerHTML = `
        <div class="card">
            <h2>📊 Dados Utilizados no Cálculo</h2>
            ${dadosEntrada}
        </div>
        
        <div class="card regime-card">
            <h2>⚖️ Regime Constitucional</h2>
            ${regimeInfo}
        </div>
        
        <div class="card">
            <h2>📅 Períodos de Cálculo</h2>
            ${periodosHtml}
        </div>
        
        <div class="card resultado-final">
            <h2>💰 Resultado Final</h2>
            ${resultadoFinal}
        </div>
    `;
}

function calcularDias(dataInicio, dataFim) {
    const d1 = new Date(dataInicio);
    const d2 = new Date(dataFim);
    const diffTime = Math.abs(d2 - d1);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}
