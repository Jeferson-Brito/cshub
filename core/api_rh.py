"""
APIs para o Módulo de RH - Gestão de Colaboradores
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import json
import logging

from .models import (
    Colaborador, Cargo, Department, HistoricoProfissional, 
    PerformanceRH, User
)

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def api_colaboradores_list(request):
    """Retorna listagem de colaboradores com filtros básicos"""
    status_filter = request.GET.get('status', 'ativo')
    dept_filter = request.GET.get('department')
    
    colaboradores = Colaborador.objects.all()
    
    if status_filter != 'todos':
        colaboradores = colaboradores.filter(status=status_filter)
    
    if dept_filter:
        colaboradores = colaboradores.filter(department_id=dept_filter)
        
    data = []
    for c in colaboradores.select_related('cargo_atual', 'department'):
        data.append({
            'id': c.id,
            'nome': c.nome_completo,
            'cargo': c.cargo_atual.nome,
            'department': c.department.name,
            'status': c.status,
            'data_admissao': c.data_admissao.strftime('%d/%m/%Y'),
            'tempo_empresa': c.tempo_empresa,
            'foto_url': c.foto.url if c.foto else None
        })
        
    return JsonResponse({'success': True, 'colaboradores': data})


@login_required
@require_http_methods(["GET"])
def api_colaborador_detail(request, pk):
    """Retorna detalhes completos de um colaborador (Dossiê)"""
    colaborador = get_object_or_404(Colaborador.objects.select_related('cargo_atual', 'department', 'user'), pk=pk)
    
    # Histórico Profissional
    historico = []
    for h in colaborador.historico.all().select_related('cargo_anterior', 'cargo_novo'):
        historico.append({
            'id': h.id,
            'data': h.data_evento.strftime('%d/%m/%Y'),
            'tipo': h.get_tipo_evento_display(),
            'cargo_anterior': h.cargo_anterior.nome if h.cargo_anterior else None,
            'cargo_novo': h.cargo_novo.nome if h.cargo_novo else None,
            'salario_anterior': float(h.salario_anterior) if h.salario_anterior else None,
            'salario_novo': float(h.salario_novo) if h.salario_novo else None,
            'observacoes': h.observacoes
        })
        
    # Performance
    performance = []
    for p in colaborador.performance.all().select_related('avaliador'):
        performance.append({
            'id': p.id,
            'data': p.data_registro.strftime('%d/%m/%Y'),
            'tipo': p.get_tipo_display(),
            'titulo': p.titulo,
            'avaliador': p.avaliador.get_full_name() if p.avaliador else "Sistema",
            'comentarios': p.comentarios,
            'proximos_passos': p.proximos_passos,
            'nota': float(p.nota_quantitativa) if p.nota_quantitativa else None
        })
        
    return JsonResponse({
        'success': True,
        'colaborador': {
            'id': colaborador.id,
            'nome_completo': colaborador.nome_completo,
            'cpf': colaborador.cpf,
            'rg': colaborador.rg,
            'data_nascimento': colaborador.data_nascimento.strftime('%d/%m/%Y'),
            'endereco': colaborador.endereco,
            'telefone': colaborador.telefone,
            'email_pessoal': colaborador.email_pessoal,
            'data_admissao': colaborador.data_admissao.strftime('%d/%m/%Y'),
            'data_desligamento': colaborador.data_desligamento.strftime('%d/%m/%Y') if colaborador.data_desligamento else None,
            'cargo_atual': colaborador.cargo_atual.nome,
            'cargo_id': colaborador.cargo_atual.id,
            'department': colaborador.department.name,
            'department_id': colaborador.department.id,
            'salario_atual': float(colaborador.salario_atual),
            'tipo_contrato': colaborador.get_tipo_contrato_display(),
            'jornada': colaborador.jornada_trabalho,
            'status': colaborador.status,
            'tempo_empresa': colaborador.tempo_empresa,
            'foto_url': colaborador.foto.url if colaborador.foto else None,
            'historico': historico,
            'performance': performance
        }
    })


@login_required
@require_http_methods(["POST"])
def api_save_colaborador(request):
    """Cria ou atualiza um colaborador"""
    try:
        # Nota: multipart/form-data para fotos
        data = request.POST
        pk = data.get('id')
        
        with transaction.atomic():
            if pk:
                colaborador = get_object_or_404(Colaborador, pk=pk)
                created = False
            else:
                colaborador = Colaborador()
                created = True
                
            colaborador.nome_completo = data.get('nome_completo')
            colaborador.cpf = data.get('cpf')
            colaborador.rg = data.get('rg', '')
            colaborador.data_nascimento = data.get('data_nascimento')
            colaborador.data_admissao = data.get('data_admissao')
            colaborador.cargo_atual_id = data.get('cargo_id')
            colaborador.department_id = data.get('department_id')
            colaborador.salario_atual = data.get('salario_atual')
            colaborador.status = data.get('status', 'ativo')
            colaborador.tipo_contrato = data.get('tipo_contrato', 'clt')
            
            if 'foto' in request.FILES:
                colaborador.foto = request.FILES['foto']
                
            colaborador.save()
            
            # Se for novo, criar histórico de admissão
            if created:
                HistoricoProfissional.objects.create(
                    colaborador=colaborador,
                    tipo_evento='admissao',
                    cargo_novo_id=colaborador.cargo_atual_id,
                    salario_novo=colaborador.salario_atual,
                    observacoes="Registro inicial de admissão"
                )
                
            return JsonResponse({'success': True, 'id': colaborador.id, 'message': 'Dados salvos com sucesso'})
            
    except Exception as e:
        logger.error(f"Erro ao salvar colaborador: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_rh_auxiliar_data(request):
    """Dados auxiliares para formulários (Cargos, Departamentos, Opções)"""
    cargos = list(Cargo.objects.all().values('id', 'nome', 'department__name'))
    depts = list(Department.objects.all().values('id', 'name'))
    
    return JsonResponse({
        'success': True,
        'cargos': cargos,
        'departments': depts,
        'status_choices': dict(Colaborador.STATUS_CHOICES),
        'tipo_contrato_choices': dict(Colaborador.TIPO_CONTRATO_CHOICES),
        'tipo_evento_choices': dict(HistoricoProfissional.TIPO_EVENTO_CHOICES),
        'tipo_performance_choices': dict(PerformanceRH.TIPO_CHOICES)
    })
