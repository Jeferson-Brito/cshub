// Script para aplicar ícones aos critérios restantes (4-9)
// Esse script será executado no navegador para adicionar ícones

const criteriaIcons = {
    'informacao_clara': { icon: 'bi-lightbulb', color: 'text-warning' },
    'acordo_espera': { icon: 'bi-hourglass-split', color: 'text-info' },
    'atendimento_respeitoso': { icon: 'bi-heart', color: 'text-danger' },
    'portugues_correto': { icon: 'bi-spellcheck', color: 'text-success' },
    'finalizacao_correta': { icon: 'bi-check2-circle', color: 'text-success' },
    'procedimento_correto': { icon: 'bi-journal-check', color: 'text-primary' }
};

// Aplicar melhorias em cada critério
Object.keys(criteriaIcons).forEach(criterioId => {
    const criterioItem = document.getElementById(criterioId)?.closest('.criterio-item');
    if (criterioItem) {
        criterioItem.classList.add('checked');
        criterioItem.setAttribute('data-criterio', criterioId);
    }
});
