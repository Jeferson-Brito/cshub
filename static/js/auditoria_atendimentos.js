// ========================================
// AUDITORIA DE ATENDIMENTOS - JAVASCRIPT
// ========================================

document.addEventListener('DOMContentLoaded', function () {
    // Estado global
    const state = {
        analistas: [],
        currentPage: 1,
        totalPages: 1,
        filters: {},
        config: null
    };

    // Inicialização
    init();

    function init() {
        loadAnalistas();
        loadConfig();
        setupEventListeners();
        setupCriteriosHandlers();

        // Verificar se estamos na visão de analista
        if (document.querySelector('.card-dashboard')) {
            initAnalystView();
        }
    }

    // ========================================
    // EVENT LISTENERS
    // ========================================

    function setupEventListeners() {
        // Form de cadastro
        const formAuditoria = document.getElementById('formAuditoria');
        if (formAuditoria) {
            formAuditoria.addEventListener('submit', handleSubmitAuditoria);
        }

        // Botão limpar
        const btnLimpar = document.getElementById('btnLimpar');
        if (btnLimpar) {
            btnLimpar.addEventListener('click', resetForm);
        }

        // Filtros
        const btnFiltros = document.getElementById('btnFiltros');
        if (btnFiltros) {
            btnFiltros.addEventListener('click', toggleFiltros);
        }

        const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
        if (btnAplicarFiltros) {
            btnAplicarFiltros.addEventListener('click', applyFilters);
        }

        // Form de configurações
        const formConfig = document.getElementById('formConfig');
        if (formConfig) {
            formConfig.addEventListener('submit', handleSubmitConfig);
        }

        // Tabs - carregar dados ao trocar
        const tabs = document.querySelectorAll('#auditoriaTabs button[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', function (e) {
                const target = e.target.dataset.bsTarget;
                handleTabChange(target);
            });
        });
    }

    function setupCriteriosHandlers() {
        // Handlers para os switches de critérios
        const switches = document.querySelectorAll('.criterio-switch');
        switches.forEach(sw => {
            sw.addEventListener('change', function () {
                const erroField = this.dataset.erro;
                const erroContainer = document.getElementById(`${erroField}_container`);

                if (!this.checked) {
                    // Mostrar campo de erro
                    erroContainer.style.display = 'block';
                    document.getElementById(erroField).required = true;
                } else {
                    // Ocultar campo de erro
                    erroContainer.style.display = 'none';
                    document.getElementById(erroField).required = false;
                    document.getElementById(erroField).value = '';
                }

                // Atualizar preview em tempo real
                updatePreview();
            });
        });
    }

    // ========================================
    // CARREGAR DADOS INICIAIS
    // ========================================

    function loadAnalistas() {
        fetch('/api/auditoria/analistas/', {
            credentials: 'include'
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    state.analistas = data.analistas;
                    populateAnalistasSelect();
                } else {
                    console.error('API retornou success=false:', data);
                }
            })
            .catch(error => {
                console.error('Erro ao carregar analistas:', error);
            });
    }

    function populateAnalistasSelect() {
        const selects = [
            document.getElementById('analista_auditado_id'),
            document.getElementById('filtro_analista')
        ];

        selects.forEach(select => {
            if (!select) return;

            // Limpar opções anteriores (exceto a primeira)
            while (select.options.length > 1) {
                select.remove(1);
            }

            // Atualizar texto da primeira opção se for o select de cadastro
            if (select.id === 'analista_auditado_id' && select.options.length > 0) {
                select.options[0].text = 'Selecione...';
            }

            state.analistas.forEach(analista => {
                const option = document.createElement('option');
                option.value = analista.id;
                option.textContent = analista.nome_completo;
                select.appendChild(option);
            });
        });
    }

    function loadConfig() {
        fetch('/api/auditoria/config/', {
            credentials: 'include'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    state.config = data.configuracao;
                    const input = document.getElementById('percentual_minimo');
                    if (input) {
                        input.value = data.configuracao.percentual_minimo_aceitavel;
                    }
                }
            })
            .catch(error => console.error('Erro ao carregar config:', error));
    }

    // ========================================
    // PREVIEW EM TEMPO REAL
    // ========================================

    function updatePreview() {
        // Contar critérios marcados
        const switches = document.querySelectorAll('.criterio-switch');
        let pontuacao = 0;

        switches.forEach(sw => {
            if (sw.checked) pontuacao++;
        });

        // Calcular nota (0-10)
        const nota = ((pontuacao / 9) * 10).toFixed(1);

        // Calcular percentual
        const percentual = ((pontuacao / 9) * 100).toFixed(0);

        // Determinar classificação
        let classificacao = '';
        let badgeClass = '';
        let progressClass = '';

        if (pontuacao === 9) {
            classificacao = 'Excelente';
            badgeClass = 'badge-excelente';
            progressClass = 'bg-success';
        } else if (pontuacao >= 7) {
            classificacao = 'Bom';
            badgeClass = 'badge-bom';
            progressClass = 'bg-info';
        } else if (pontuacao >= 5) {
            classificacao = 'Regular';
            badgeClass = 'badge-regular';
            progressClass = 'bg-warning';
        } else {
            classificacao = 'Insatisfatório';
            badgeClass = 'badge-insatisfatorio';
            progressClass = 'bg-danger';
        }

        // Atualizar UI
        document.getElementById('pontuacao-display').textContent = pontuacao;
        document.getElementById('nota-display').textContent = nota.replace('.', ',');

        const progressBar = document.getElementById('progresso-bar');
        progressBar.style.width = percentual + '%';
        progressBar.textContent = percentual + '%';
        progressBar.className = 'progress-bar ' + progressClass;

        const badge = document.getElementById('classificacao-badge');
        badge.textContent = classificacao;
        badge.className = 'badge ' + badgeClass;
    }

    // ========================================
    // SUBMIT AUDITORIA
    // ========================================

    function handleSubmitAuditoria(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {};

        // Coletar dados básicos
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Tratar explicitamente os checkboxes (switches) para garantir booleanos
        document.querySelectorAll('.criterio-switch').forEach(switchInput => {
            data[switchInput.name] = switchInput.checked;
        });

        // Validar descrições de erro
        const switches = document.querySelectorAll('.criterio-switch:not(:checked)');
        let valid = true;

        switches.forEach(sw => {
            const erroField = sw.dataset.erro;
            const erroValue = document.getElementById(erroField).value.trim();
            if (!erroValue) {
                valid = false;
                document.getElementById(erroField).classList.add('is-invalid');
            }
        });

        if (!valid) {
            Swal.fire({
                icon: 'error',
                title: 'Erro de Validação',
                text: 'Por favor, descreva os erros para todos os critérios não atendidos.',
            });
            return;
        }

        // Enviar para API
        fetch('/api/auditoria/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Sucesso!',
                        text: `Auditoria salva com nota ${result.auditoria.nota.toFixed(1)} - ${result.auditoria.classificacao}`,
                        confirmButtonText: 'OK'
                    }).then(() => {
                        resetForm();
                        // Ir para aba de lista
                        const listaTab = document.querySelector('#lista-tab');
                        if (listaTab) {
                            const tab = new bootstrap.Tab(listaTab);
                            tab.show();
                        }
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: result.error || 'Erro ao salvar auditoria',
                    });
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Erro ao salvar auditoria. Tente novamente.',
                });
            });
    }

    function resetForm() {
        const form = document.getElementById('formAuditoria');
        form.reset();

        // Resetar switches para checked
        const switches = document.querySelectorAll('.criterio-switch');
        switches.forEach(sw => {
            sw.checked = true;
            const erroField = sw.dataset.erro;
            const erroContainer = document.getElementById(`${erroField}_container`);
            erroContainer.style.display = 'none';
            document.getElementById(erroField).value = '';
        });

        // Resetar data para hoje
        const dataInput = document.getElementById('data_atendimento');
        if (dataInput) {
            dataInput.value = new Date().toISOString().split('T')[0];
        }

        updatePreview();
    }

    // ========================================
    // LISTAGEM DE AUDITORIAS
    // ========================================

    function loadAuditorias(page = 1) {
        const tbody = document.getElementById('lista-auditorias');
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4"><div class="spinner-border text-primary"></div></td></tr>';

        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            ...state.filters
        });

        fetch(`/api/auditoria/list/?${params}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderAuditorias(data.auditorias);
                    renderPagination(data.page, data.total_pages);
                    state.currentPage = data.page;
                    state.totalPages = data.total_pages;
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger py-4">Erro ao carregar auditorias</td></tr>';
            });
    }

    function renderAuditorias(auditorias) {
        const tbody = document.getElementById('lista-auditorias');

        if (auditorias.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">Nenhuma auditoria encontrada</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        auditorias.forEach(aud => {
            const tr = document.createElement('tr');
            if (aud.requer_acao) {
                tr.classList.add('row-alert');
            }

            const badgeClass = `badge-${aud.classificacao}`;
            const dataFormatada = new Date(aud.data_atendimento).toLocaleDateString('pt-BR');

            tr.innerHTML = `
                <td>${dataFormatada}</td>
                <td>${aud.id_conversa}</td>
                <td><span class="badge bg-secondary">${aud.tipo_atendimento}</span></td>
                <td>${aud.analista_auditado.nome_completo}</td>
                <td>${aud.pontuacao}/9</td>
                <td class="fw-bold">${aud.nota.toFixed(1)}</td>
                <td>
                    <span class="badge ${badgeClass}">${aud.classificacao_display}</span>
                    ${aud.requer_acao ? '<i class="bi bi-exclamation-triangle icon-alert ms-2"></i>' : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewDetails(${aud.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });
    }

    function renderPagination(currentPage, totalPages) {
        const container = document.getElementById('paginacao');
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '<nav><ul class="pagination pagination-sm mb-0">';

        // Botão anterior
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadAuditorias(${currentPage - 1}); return false;">Anterior</a>
        </li>`;

        // Páginas
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="loadAuditorias(${i}); return false;">${i}</a>
                </li>`;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        // Botão próximo
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadAuditorias(${currentPage + 1}); return false;">Próximo</a>
        </li>`;

        html += '</ul></nav>';

        container.innerHTML = html;
    }

    // Tornar função global para uso inline
    window.loadAuditorias = loadAuditorias;

    // ========================================
    // DETALHES DA AUDITORIA
    // ========================================

    window.viewDetails = function (id) {
        fetch(`/api/auditoria/${id}/`, { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showDetailsModal(data.auditoria);
                }
            })
            .catch(error => console.error('Erro:', error));
    };

    function showDetailsModal(aud) {
        const content = document.getElementById('detalhes-content');

        const dataFormatada = new Date(aud.data_atendimento).toLocaleDateString('pt-BR');
        const badgeClass = `badge-${aud.classificacao}`;

        let criteriosHTML = '';
        const criterios = [
            { nome: '1. Apresentou-se corretamente?', value: aud.criterios.apresentou_corretamente, erro: aud.criterios.erro_apresentacao },
            { nome: '2. Analisou o histórico?', value: aud.criterios.analisou_historico, erro: aud.criterios.erro_historico },
            { nome: '3. Entendeu a solicitação?', value: aud.criterios.entendeu_solicitacao, erro: aud.criterios.erro_entendimento },
            { nome: '4. Informação clara?', value: aud.criterios.informacao_clara, erro: aud.criterios.erro_informacao },
            { nome: '5. Acordo de espera correto?', value: aud.criterios.acordo_espera, erro: aud.criterios.erro_acordo_espera },
            { nome: '6. Atendimento respeitoso?', value: aud.criterios.atendimento_respeitoso, erro: aud.criterios.erro_respeito },
            { nome: '7. Português correto?', value: aud.criterios.portugues_correto, erro: aud.criterios.erro_portugues },
            { nome: '8. Finalização correta?', value: aud.criterios.finalizacao_correta, erro: aud.criterios.erro_finalizacao },
            { nome: '9. Procedimento correto?', value: aud.criterios.procedimento_correto, erro: aud.criterios.erro_procedimento },
        ];

        criterios.forEach(crit => {
            const statusClass = crit.value ? 'success' : 'error';
            const statusIcon = crit.value ? '<i class="bi bi-check-circle text-success"></i>' : '<i class="bi bi-x-circle text-danger"></i>';

            criteriosHTML += `
                <div class="criterio-detail ${statusClass}">
                    <div class="d-flex align-items-start">
                        <div class="me-2">${statusIcon}</div>
                        <div class="flex-grow-1">
                            <strong>${crit.nome}</strong>
                            ${!crit.value && crit.erro ? `<p class="mb-0 mt-1 text-danger"><small><strong>Erro:</strong> ${crit.erro}</small></p>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });

        content.innerHTML = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <p><strong>Data:</strong> ${dataFormatada}</p>
                    <p><strong>ID Conversa:</strong> ${aud.id_conversa}</p>
                    <p><strong>Tipo:</strong> ${aud.tipo_atendimento}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Analista:</strong> ${aud.analista_auditado.nome_completo}</p>
                    <p><strong>Auditor:</strong> ${aud.auditor.nome_completo}</p>
                    <p><strong>Data Auditoria:</strong> ${new Date(aud.created_at).toLocaleDateString('pt-BR')}</p>
                </div>
            </div>
            
            <div class="alert alert-info mb-3">
                <div class="row text-center">
                    <div class="col-4">
                        <h6>Pontuação</h6>
                        <h4>${aud.pontuacao}/9</h4>
                    </div>
                    <div class="col-4">
                        <h6>Nota</h6>
                        <h4>${aud.nota.toFixed(1)}</h4>
                    </div>
                    <div class="col-4">
                        <h6>Classificação</h6>
                        <h4><span class="badge ${badgeClass}">${aud.classificacao_display}</span></h4>
                    </div>
                </div>
            </div>
            
            <h6 class="mb-3">Critérios Avaliados:</h6>
            ${criteriosHTML}
            
            ${aud.requer_acao ? '<div class="alert alert-danger mt-3"><i class="bi bi-exclamation-triangle me-2"></i><strong>Alerta:</strong> Esta auditoria requer discussão com o analista.</div>' : ''}
        `;

        const modal = new bootstrap.Modal(document.getElementById('modalDetalhes'));
        modal.show();
    }

    // ========================================
    // RANKING DE ANALISTAS
    // ========================================

    function loadRanking() {
        const container = document.getElementById('ranking-container');
        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';

        fetch('/api/auditoria/ranking/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderRanking(data.ranking);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                container.innerHTML = '<div class="alert alert-danger">Erro ao carregar ranking</div>';
            });
    }

    function renderRanking(ranking) {
        const container = document.getElementById('ranking-container');

        if (ranking.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Nenhuma auditoria registrada ainda</div>';
            return;
        }

        let html = '';

        ranking.forEach(item => {
            const rankClass = item.posicao <= 3 ? `top-${item.posicao}` : '';
            const badgeClass = item.posicao <= 3 ? `top-${item.posicao}` : '';

            html += `
                <div class="ranking-item ${rankClass}">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <div class="posicao-badge ${badgeClass}">${item.posicao}º</div>
                        </div>
                        <div class="col">
                            <h5 class="mb-1">${item.analista_nome}</h5>
                            <p class="text-muted mb-0">
                                ${item.total_auditorias} auditorias realizadas
                            </p>
                        </div>
                        <div class="col-auto text-center">
                            <h6 class="mb-1 text-muted">Nota Média</h6>
                            <h3 class="mb-0 text-primary fw-bold">${item.nota_media.toFixed(1)}</h3>
                        </div>
                        <div class="col-auto text-center">
                            <h6 class="mb-1 text-muted">Pontuação Média</h6>
                            <h4 class="mb-0">${item.pontuacao_media.toFixed(1)}/9</h4>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // ========================================
    // VISÃO POR ANALISTA
    // ========================================

    function loadAnalistasView() {
        const container = document.getElementById('analistas-container');
        container.innerHTML = '<div class="col-12 text-center py-4"><div class="spinner-border text-primary"></div></div>';

        // Carregar estatísticas de todos os analistas
        Promise.all(
            state.analistas.map(analista =>
                fetch(`/api/auditoria/analista/${analista.id}/`)
                    .then(r => r.json())
            )
        )
            .then(results => {
                renderAnalistasCards(results);
            })
            .catch(error => {
                console.error('Erro:', error);
                container.innerHTML = '<div class="col-12"><div class="alert alert-danger">Erro ao carregar dados dos analistas</div></div>';
            });
    }

    function renderAnalistasCards(results) {
        const container = document.getElementById('analistas-container');
        let html = '';

        results.forEach(data => {
            if (!data.success) return;

            const stats = data;
            const alertClass = stats.tem_alertas ? 'has-alert' : '';

            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="analista-card ${alertClass}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="mb-0">${stats.analista.nome_completo}</h5>
                            ${stats.tem_alertas ? '<span class="badge-alert"><i class="bi bi-exclamation-triangle"></i> Alerta</span>' : ''}
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-6 col-md-4">
                                <div class="stat-item">
                                    <div class="stat-value">${stats.total_auditorias}</div>
                                    <div class="stat-label">Auditorias</div>
                                </div>
                            </div>
                            <div class="col-6 col-md-4">
                                <div class="stat-item">
                                    <div class="stat-value">${stats.nota_media.toFixed(1)}</div>
                                    <div class="stat-label">Nota Média</div>
                                </div>
                            </div>
                            <div class="col-12 col-md-4 mt-2 mt-md-0">
                                ${stats.ultima_auditoria ? `
                                    <div class="stat-item">
                                        <div class="stat-value" style="font-size: 1rem;">${new Date(stats.ultima_auditoria.data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}</div>
                                        <div class="stat-label">Última Auditoria</div>
                                    </div>
                                ` : '<div class="stat-item"><div class="stat-label">Sem auditorias</div></div>'}
                            </div>
                        </div>
                        
                        ${stats.total_auditorias > 0 ? `
                            <div class="mt-3">
                                <h6 class="mb-2" style="font-size: 0.875rem;">Distribuição:</h6>
                                <div class="row g-1">
                                    <div class="col-6"><span class="badge badge-excelente w-100">Excelente: ${stats.distribuicao.excelente}</span></div>
                                    <div class="col-6"><span class="badge badge-bom w-100">Bom: ${stats.distribuicao.bom}</span></div>
                                    <div class="col-6"><span class="badge badge-regular w-100">Regular: ${stats.distribuicao.regular}</span></div>
                                    <div class="col-6"><span class="badge badge-insatisfatorio w-100">Insatisf.: ${stats.distribuicao.insatisfatorio}</span></div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        if (html === '') {
            html = '<div class="col-12"><div class="alert alert-info">Nenhum analista encontrado</div></div>';
        }

        container.innerHTML = html;
    }

    // ========================================
    // FILTROS
    // ========================================

    function toggleFiltros() {
        const panel = document.getElementById('filtrosPanel');
        const collapse = new bootstrap.Collapse(panel, {
            toggle: true
        });
    }

    function applyFilters() {
        const filters = {};

        const analistaId = document.getElementById('filtro_analista').value;
        if (analistaId) filters.analista_id = analistaId;

        const dataInicio = document.getElementById('filtro_data_inicio').value;
        if (dataInicio) filters.data_inicio = dataInicio;

        const dataFim = document.getElementById('filtro_data_fim').value;
        if (dataFim) filters.data_fim = dataFim;

        const tipo = document.getElementById('filtro_tipo').value;
        if (tipo) filters.tipo = tipo;

        const classificacao = document.getElementById('filtro_classificacao').value;
        if (classificacao) filters.classificacao = classificacao;

        const apenasAlertas = document.getElementById('filtro_apenas_alertas').checked;
        if (apenasAlertas) filters.apenas_alertas = 'true';

        state.filters = filters;
        loadAuditorias(1);
    }

    // ========================================
    // CONFIGURAÇÕES
    // ========================================

    function handleSubmitConfig(e) {
        e.preventDefault();

        const percentual = parseFloat(document.getElementById('percentual_minimo').value);

        fetch('/api/auditoria/config/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                percentual_minimo_aceitavel: percentual
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Configuração Salva!',
                        text: `Percentual mínimo atualizado para ${percentual}%`,
                        timer: 2000
                    });
                    state.config = data.configuracao;
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: data.error || 'Erro ao salvar configuração'
                    });
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Erro ao salvar configuração'
                });
            });
    }

    // ========================================
    // MUDANÇA DE TABS
    // ========================================

    function handleTabChange(target) {
        switch (target) {
            case '#lista':
                loadAuditorias(1);
                break;
            case '#ranking':
                loadRanking();
                break;
            case '#analistas':
                loadAnalistasView();
                break;
            case '#config':
                loadConfig();
                break;
        }
    }

    // ========================================
    // UTILITÁRIOS
    // ========================================

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ========================================
    // VISÃO DO ANALISTA (NOVO)
    // ========================================

    function initAnalystView() {
        // Carregar stats para os cards
        fetch('/api/auditoria/dashboard/', { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.distribuicao) {
                        document.getElementById('count-excelente').textContent = data.distribuicao.excelente || 0;
                        document.getElementById('count-bom').textContent = data.distribuicao.bom || 0;
                        document.getElementById('count-regular').textContent = data.distribuicao.regular || 0;
                        document.getElementById('count-insatisfatorio').textContent = data.distribuicao.insatisfatorio || 0;
                    }
                }
            })
            .catch(error => console.error('Erro ao carregar dashboard analista:', error));
    }

    window.filterAnalystList = function (classificacao) {
        // Atualizar label
        const map = {
            'excelente': 'Excelente',
            'bom': 'Bom',
            'regular': 'Regular',
            'insatisfatorio': 'Insatisfatório'
        };
        document.getElementById('current-filter-label').textContent = map[classificacao] || classificacao;

        // Mostrar container
        const container = document.getElementById('analyst-list-container');
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });

        // Carregar auditorias
        loadAnalystAudits(classificacao);
    };

    function loadAnalystAudits(classificacao) {
        const tbody = document.getElementById('lista-auditorias-analista');
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4"><div class="spinner-border text-primary"></div></td></tr>';

        // Usar API de lista com filtro
        const params = new URLSearchParams({
            classificacao: classificacao,
            per_page: 50 // Mostrar mais itens por ser uma lista focada
        });

        fetch(`/api/auditoria/list/?${params}`, { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderAnalystAudits(data.auditorias, tbody);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Erro ao carregar auditorias</td></tr>';
            });
    }

    function renderAnalystAudits(auditorias, tbody) {
        if (auditorias.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Nenhuma auditoria encontrada com esta classificação</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        auditorias.forEach(aud => {
            const tr = document.createElement('tr');
            if (aud.requer_acao) {
                tr.classList.add('row-alert');
            }

            const badgeClass = `badge-${aud.classificacao}`;
            const dataFormatada = new Date(aud.data_atendimento).toLocaleDateString('pt-BR');

            tr.innerHTML = `
                <td>${dataFormatada}</td>
                <td>${aud.id_conversa}</td>
                <td><span class="badge bg-secondary">${aud.tipo_atendimento}</span></td>
                <td>${aud.pontuacao}/9</td>
                <td class="fw-bold">${aud.nota.toFixed(1)}</td>
                <td>
                    <span class="badge ${badgeClass}">${aud.classificacao_display}</span>
                    ${aud.requer_acao ? '<i class="bi bi-exclamation-triangle icon-alert ms-2"></i>' : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewDetails(${aud.id})">
                        <i class="bi bi-eye"></i> Detalhes
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });
    }


    // Inicializar preview na carga
    updatePreview();

    // Definir data de hoje como padrão
    const dataInput = document.getElementById('data_atendimento');
    if (dataInput) {
        dataInput.value = new Date().toISOString().split('T')[0];
    }
});
