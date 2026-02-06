from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import AuditoriaAtendimento, ConfiguracaoAuditoria, User, Department


# ========================================
# DECORADORES DE PERMISSÃO
# ========================================

def gestor_or_admin_required(view_func):
    """Decorator para permitir apenas gestores e administradores"""
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_gestor() or request.user.is_administrador()):
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator para permitir apenas administradores"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_administrador():
            return JsonResponse({'error': 'Acesso negado. Apenas administradores.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# ========================================
# CRUD DE AUDITORIAS
# ========================================

@login_required
@gestor_or_admin_required
@require_POST
def api_auditoria_create(request):
    """Cria nova auditoria de atendimento"""
    try:
        data = json.loads(request.body)
        
        # Obter departamento
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        # Validar campos obrigatórios
        required_fields = ['data_atendimento', 'id_conversa', 'tipo_atendimento', 'analista_auditado_id']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Campo obrigatório: {field}'}, status=400)
        
        # Validar analista
        try:
            analista = User.objects.get(id=data['analista_auditado_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'Analista não encontrado'}, status=404)
        
        # Validar descrições de erro quando critério = False
        criterios_erros = {
            'apresentou_corretamente': 'erro_apresentacao',
            'analisou_historico': 'erro_historico',
            'entendeu_solicitacao': 'erro_entendimento',
            'informacao_clara': 'erro_informacao',
            'acordo_espera': 'erro_acordo_espera',
            'atendimento_respeitoso': 'erro_respeito',
            'portugues_correto': 'erro_portugues',
            'finalizacao_correta': 'erro_finalizacao',
            'procedimento_correto': 'erro_procedimento',
        }
        
        for criterio, campo_erro in criterios_erros.items():
            if not data.get(criterio, True) and not data.get(campo_erro, '').strip():
                return JsonResponse({
                    'error': f'Descrição do erro é obrigatória quando o critério "{criterio}" não é atendido'
                }, status=400)
        
        # Criar auditoria
        auditoria = AuditoriaAtendimento(
            data_atendimento=data['data_atendimento'],
            id_conversa=data['id_conversa'],
            tipo_atendimento=data['tipo_atendimento'],
            analista_auditado=analista,
            auditor=request.user,
            department=department,
            # Critérios
            apresentou_corretamente=data.get('apresentou_corretamente', True),
            erro_apresentacao=data.get('erro_apresentacao', ''),
            analisou_historico=data.get('analisou_historico', True),
            erro_historico=data.get('erro_historico', ''),
            entendeu_solicitacao=data.get('entendeu_solicitacao', True),
            erro_entendimento=data.get('erro_entendimento', ''),
            informacao_clara=data.get('informacao_clara', True),
            erro_informacao=data.get('erro_informacao', ''),
            acordo_espera=data.get('acordo_espera', True),
            erro_acordo_espera=data.get('erro_acordo_espera', ''),
            atendimento_respeitoso=data.get('atendimento_respeitoso', True),
            erro_respeito=data.get('erro_respeito', ''),
            portugues_correto=data.get('portugues_correto', True),
            erro_portugues=data.get('erro_portugues', ''),
            finalizacao_correta=data.get('finalizacao_correta', True),
            erro_finalizacao=data.get('erro_finalizacao', ''),
            procedimento_correto=data.get('procedimento_correto', True),
            erro_procedimento=data.get('erro_procedimento', ''),
        )
        
        # Save já calcula automaticamente pontuação, nota e classificação
        auditoria.save()
        
        return JsonResponse({
            'success': True,
            'auditoria': {
                'id': auditoria.id,
                'pontuacao': auditoria.pontuacao,
                'nota': float(auditoria.nota),
                'classificacao': auditoria.classificacao,
                'requer_acao': auditoria.requer_acao,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@gestor_or_admin_required
@require_GET
def api_auditoria_list(request):
    """Lista auditorias com filtros opcionais"""
    try:
        # Obter departamento
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        # Base queryset
        queryset = AuditoriaAtendimento.objects.filter(department=department)
        
        # Filtros
        analista_id = request.GET.get('analista_id')
        if analista_id:
            queryset = queryset.filter(analista_auditado_id=analista_id)
        
        data_inicio = request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_atendimento__gte=data_inicio)
        
        data_fim = request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_atendimento__lte=data_fim)
        
        tipo = request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_atendimento=tipo)
        
        classificacao = request.GET.get('classificacao')
        if classificacao:
            queryset = queryset.filter(classificacao=classificacao)
        
        apenas_alertas = request.GET.get('apenas_alertas')
        if apenas_alertas == 'true':
            queryset = queryset.filter(requer_acao=True)
        
        # Paginação
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        
        total = queryset.count()
        auditorias = queryset[start:end]
        
        data = []
        for aud in auditorias:
            data.append({
                'id': aud.id,
                'data_atendimento': aud.data_atendimento.isoformat(),
                'id_conversa': aud.id_conversa,
                'tipo_atendimento': aud.get_tipo_atendimento_display(),
                'analista_auditado': {
                    'id': aud.analista_auditado.id,
                    'username': aud.analista_auditado.username,
                    'nome_completo': aud.analista_auditado.get_full_name() or aud.analista_auditado.username,
                },
                'auditor': {
                    'id': aud.auditor.id,
                    'username': aud.auditor.username,
                },
                'pontuacao': aud.pontuacao,
                'nota': float(aud.nota),
                'classificacao': aud.classificacao,
                'classificacao_display': aud.get_classificacao_display(),
                'requer_acao': aud.requer_acao,
                'created_at': aud.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'auditorias': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@gestor_or_admin_required
@require_GET
def api_auditoria_detail(request, pk):
    """Detalhes de uma auditoria específica"""
    try:
        auditoria = AuditoriaAtendimento.objects.get(id=pk)
        
        # Verificar permissão de department
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        if auditoria.department != department:
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        data = {
            'id': auditoria.id,
            'data_atendimento': auditoria.data_atendimento.isoformat(),
            'id_conversa': auditoria.id_conversa,
            'tipo_atendimento': auditoria.get_tipo_atendimento_display(),
            'analista_auditado': {
                'id': auditoria.analista_auditado.id,
                'username': auditoria.analista_auditado.username,
                'nome_completo': auditoria.analista_auditado.get_full_name() or auditoria.analista_auditado.username,
            },
            'auditor': {
                'id': auditoria.auditor.id,
                'username': auditoria.auditor.username,
                'nome_completo': auditoria.auditor.get_full_name() or auditoria.auditor.username,
            },
            'criterios': {
                'apresentou_corretamente': auditoria.apresentou_corretamente,
                'erro_apresentacao': auditoria.erro_apresentacao,
                'analisou_historico': auditoria.analisou_historico,
                'erro_historico': auditoria.erro_historico,
                'entendeu_solicitacao': auditoria.entendeu_solicitacao,
                'erro_entendimento': auditoria.erro_entendimento,
                'informacao_clara': auditoria.informacao_clara,
                'erro_informacao': auditoria.erro_informacao,
                'acordo_espera': auditoria.acordo_espera,
                'erro_acordo_espera': auditoria.erro_acordo_espera,
                'atendimento_respeitoso': auditoria.atendimento_respeitoso,
                'erro_respeito': auditoria.erro_respeito,
                'portugues_correto': auditoria.portugues_correto,
                'erro_portugues': auditoria.erro_portugues,
                'finalizacao_correta': auditoria.finalizacao_correta,
                'erro_finalizacao': auditoria.erro_finalizacao,
                'procedimento_correto': auditoria.procedimento_correto,
                'erro_procedimento': auditoria.erro_procedimento,
            },
            'pontuacao': auditoria.pontuacao,
            'nota': float(auditoria.nota),
            'classificacao': auditoria.classificacao,
            'classificacao_display': auditoria.get_classificacao_display(),
            'requer_acao': auditoria.requer_acao,
            'created_at': auditoria.created_at.isoformat(),
            'updated_at': auditoria.updated_at.isoformat(),
        }
        
        return JsonResponse({'success': True, 'auditoria': data})
        
    except AuditoriaAtendimento.DoesNotExist:
        return JsonResponse({'error': 'Auditoria não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@admin_required
@require_POST
def api_auditoria_update(request, pk):
    """Atualiza uma auditoria (apenas admin)"""
    try:
        auditoria = AuditoriaAtendimento.objects.get(id=pk)
        data = json.loads(request.body)
        
        # Atualizar campos editáveis
        if 'data_atendimento' in data:
            auditoria.data_atendimento = data['data_atendimento']
        if 'id_conversa' in data:
            auditoria.id_conversa = data['id_conversa']
        if 'tipo_atendimento' in data:
            auditoria.tipo_atendimento = data['tipo_atendimento']
        
        # Atualizar critérios
        criterios = [
            'apresentou_corretamente', 'analisou_historico', 'entendeu_solicitacao',
            'informacao_clara', 'acordo_espera', 'atendimento_respeitoso',
            'portugues_correto', 'finalizacao_correta', 'procedimento_correto'
        ]
        
        erros = [
            'erro_apresentacao', 'erro_historico', 'erro_entendimento',
            'erro_informacao', 'erro_acordo_espera', 'erro_respeito',
            'erro_portugues', 'erro_finalizacao', 'erro_procedimento'
        ]
        
        for criterio in criterios:
            if criterio in data:
                setattr(auditoria, criterio, data[criterio])
        
        for erro in erros:
            if erro in data:
                setattr(auditoria, erro, data[erro])
        
        # Save recalcula automaticamente
        auditoria.save()
        
        return JsonResponse({
            'success': True,
            'auditoria': {
                'id': auditoria.id,
                'pontuacao': auditoria.pontuacao,
                'nota': float(auditoria.nota),
                'classificacao': auditoria.classificacao,
                'requer_acao': auditoria.requer_acao,
            }
        })
        
    except AuditoriaAtendimento.DoesNotExist:
        return JsonResponse({'error': 'Auditoria não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@admin_required
@require_POST
def api_auditoria_delete(request, pk):
    """Exclui uma auditoria (apenas admin)"""
    try:
        auditoria = AuditoriaAtendimento.objects.get(id=pk)
        auditoria.delete()
        return JsonResponse({'success': True})
    except AuditoriaAtendimento.DoesNotExist:
        return JsonResponse({'error': 'Auditoria não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ========================================
# ESTATÍSTICAS E RANKING
# ========================================

@login_required
@gestor_or_admin_required
@require_GET
def api_ranking_analistas(request):
    """Ranking de analistas por nota média"""
    try:
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        # Período opcional
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        
        queryset = AuditoriaAtendimento.objects.filter(department=department)
        
        if data_inicio:
            queryset = queryset.filter(data_atendimento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_atendimento__lte=data_fim)
        
        # Agrupar por analista e calcular médias
        ranking = queryset.values(
            'analista_auditado__id',
            'analista_auditado__username',
            'analista_auditado__first_name',
            'analista_auditado__last_name'
        ).annotate(
            total_auditorias=Count('id'),
            nota_media=Avg('nota'),
            pontuacao_media=Avg('pontuacao')
        ).order_by('-nota_media')
        
        # Formatar resposta com posição
        data = []
        for idx, item in enumerate(ranking, 1):
            # Determinar classificação predominante
            auditorias_analista = queryset.filter(analista_auditado_id=item['analista_auditado__id'])
            classificacao_predominante = auditorias_analista.values('classificacao').annotate(
                count=Count('id')
            ).order_by('-count').first()
            
            nome_completo = f"{item['analista_auditado__first_name']} {item['analista_auditado__last_name']}".strip()
            if not nome_completo:
                nome_completo = item['analista_auditado__username']
            
            data.append({
                'posicao': idx,
                'analista_id': item['analista_auditado__id'],
                'analista_username': item['analista_auditado__username'],
                'analista_nome': nome_completo,
                'total_auditorias': item['total_auditorias'],
                'nota_media': round(float(item['nota_media']), 2),
                'pontuacao_media': round(float(item['pontuacao_media']), 1),
                'classificacao_predominante': classificacao_predominante['classificacao'] if classificacao_predominante else 'N/A',
            })
        
        return JsonResponse({'success': True, 'ranking': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@gestor_or_admin_required
@require_GET
def api_estatisticas_analista(request, analista_id):
    """Estatísticas detalhadas de um analista específico"""
    try:
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        analista = User.objects.get(id=analista_id)
        
        auditorias = AuditoriaAtendimento.objects.filter(
            department=department,
            analista_auditado=analista
        )
        
        total_auditorias = auditorias.count()
        
        if total_auditorias == 0:
            return JsonResponse({
                'success': True,
                'analista': {
                    'id': analista.id,
                    'username': analista.username,
                    'nome_completo': analista.get_full_name() or analista.username,
                },
                'total_auditorias': 0,
                'nota_media': 0,
                'distribuicao': {},
                'ultima_auditoria': None,
                'tem_alertas': False,
            })
        
        # Calcular estatísticas
        nota_media = auditorias.aggregate(Avg('nota'))['nota__avg']
        
        # Distribuição por classificação
        distribuicao = {}
        for classificacao in ['excelente', 'bom', 'regular', 'insatisfatorio']:
            count = auditorias.filter(classificacao=classificacao).count()
            distribuicao[classificacao] = count
        
        # Última auditoria
        ultima = auditorias.order_by('-created_at').first()
        
        # Verificar alertas ativos
        tem_alertas = auditorias.filter(requer_acao=True).exists()
        
        return JsonResponse({
            'success': True,
            'analista': {
                'id': analista.id,
                'username': analista.username,
                'nome_completo': analista.get_full_name() or analista.username,
            },
            'total_auditorias': total_auditorias,
            'nota_media': round(float(nota_media), 2),
            'distribuicao': distribuicao,
            'ultima_auditoria': {
                'id': ultima.id,
                'data': ultima.data_atendimento.isoformat(),
                'nota': float(ultima.nota),
                'classificacao': ultima.get_classificacao_display(),
            } if ultima else None,
            'tem_alertas': tem_alertas,
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'Analista não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@gestor_or_admin_required
@require_GET
def api_dashboard_auditoria(request):
    """Dashboard geral de auditorias"""
    try:
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        # Período opcional (padrão: último mês)
        data_fim = timezone.now().date()
        data_inicio = data_fim - timedelta(days=30)
        
        if request.GET.get('data_inicio'):
            data_inicio = datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d').date()
        if request.GET.get('data_fim'):
            data_fim = datetime.strptime(request.GET.get('data_fim'), '%Y-%m-%d').date()
        
        auditorias = AuditoriaAtendimento.objects.filter(
            department=department,
            data_atendimento__gte=data_inicio,
            data_atendimento__lte=data_fim
        )
        
        total = auditorias.count()
        nota_media_geral = auditorias.aggregate(Avg('nota'))['nota__avg'] or 0
        
        # Distribuição por classificação
        distribuicao = {
            'excelente': auditorias.filter(classificacao='excelente').count(),
            'bom': auditorias.filter(classificacao='bom').count(),
            'regular': auditorias.filter(classificacao='regular').count(),
            'insatisfatorio': auditorias.filter(classificacao='insatisfatorio').count(),
        }
        
        # Analistas com alertas
        analistas_com_alertas = auditorias.filter(requer_acao=True).values(
            'analista_auditado__id',
            'analista_auditado__username'
        ).distinct()
        
        # Top 3 analistas
        top_3 = auditorias.values(
            'analista_auditado__id',
            'analista_auditado__username',
            'analista_auditado__first_name',
            'analista_auditado__last_name'
        ).annotate(
            nota_media=Avg('nota')
        ).order_by('-nota_media')[:3]
        
        return JsonResponse({
            'success': True,
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat(),
            },
            'total_auditorias': total,
            'nota_media_geral': round(float(nota_media_geral), 2),
            'distribuicao': distribuicao,
            'total_alertas': auditorias.filter(requer_acao=True).count(),
            'analistas_com_alertas': list(analistas_com_alertas),
            'top_3': [
                {
                    'id': item['analista_auditado__id'],
                    'username': item['analista_auditado__username'],
                    'nome': f"{item['analista_auditado__first_name']} {item['analista_auditado__last_name']}".strip() or item['analista_auditado__username'],
                    'nota_media': round(float(item['nota_media']), 2),
                }
                for item in top_3
            ],
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ========================================
# CONFIGURAÇÕES
# ========================================

@login_required
@gestor_or_admin_required
@require_GET
def api_configuracao_get(request):
    """Obter configuração atual de auditoria"""
    try:
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        config, created = ConfiguracaoAuditoria.objects.get_or_create(
            department=department,
            defaults={'percentual_minimo_aceitavel': 77.78, 'ativo': True}
        )
        
        return JsonResponse({
            'success': True,
            'configuracao': {
                'id': config.id,
                'percentual_minimo_aceitavel': float(config.percentual_minimo_aceitavel),
                'ativo': config.ativo,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@admin_required
@require_POST
def api_configuracao_update(request):
    """Atualizar configuração (apenas admin)"""
    try:
        data = json.loads(request.body)
        
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        config, created = ConfiguracaoAuditoria.objects.get_or_create(department=department)
        
        if 'percentual_minimo_aceitavel' in data:
            percentual = float(data['percentual_minimo_aceitavel'])
            if percentual < 0 or percentual > 100:
                return JsonResponse({'error': 'Percentual deve estar entre 0 e 100'}, status=400)
            config.percentual_minimo_aceitavel = percentual
        
        if 'ativo' in data:
            config.ativo = bool(data['ativo'])
        
        config.save()
        
        return JsonResponse({
            'success': True,
            'configuracao': {
                'id': config.id,
                'percentual_minimo_aceitavel': float(config.percentual_minimo_aceitavel),
                'ativo': config.ativo,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ========================================
# HELPER - LISTA DE ANALISTAS
# ========================================

@login_required
@gestor_or_admin_required
@require_GET
def api_analistas_list(request):
    """Lista de analistas do departamento para seleção"""
    try:
        department = request.session.get('current_department_obj') or request.user.department
        if isinstance(department, dict):
            department = Department.objects.get(id=department['id'])
        
        analistas = User.objects.filter(
            department=department,
            ativo=True
        ).order_by('first_name', 'last_name', 'username')
        
        data = []
        for analista in analistas:
            nome_completo = analista.get_full_name() or analista.username
            data.append({
                'id': analista.id,
                'username': analista.username,
                'nome_completo': nome_completo,
                'role': analista.get_role_display(),
            })
        
        return JsonResponse({'success': True, 'analistas': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
