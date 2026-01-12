from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import IndicadorDesempenho, User, Department


@login_required
@require_http_methods(["GET"])
def api_kpis_list(request):
    """Lista KPIs - filtrado por analista se for um analista"""
    user = request.user
    
    # Obter departamento NRS Suporte
    try:
        nrs_dept = Department.objects.get(name='NRS Suporte')
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Departamento NRS Suporte não encontrado'}, status=404)
    
    # Filtrar analista específico (se solicitado)
    analista_id = request.GET.get('analista_id')
    
    if user.role == 'analista':
        # Analista só vê seus próprios KPIs
        kpis = IndicadorDesempenho.objects.filter(
            analista=user,
            department=nrs_dept
        ).order_by('ano', 'mes')
    elif analista_id:
        # Gestor/Admin filtrando por analista específico
        kpis = IndicadorDesempenho.objects.filter(
            analista_id=analista_id,
            department=nrs_dept
        ).order_by('ano', 'mes')
    else:
        # Gestor/Admin vê todos
        kpis = IndicadorDesempenho.objects.filter(
            department=nrs_dept
        ).order_by('ano', 'mes')
    
    data = [{
        'id': k.id,
        'analista_id': k.analista_id,
        'analista_nome': k.analista.get_full_name() or k.analista.username,
        'mes': k.mes,
        'ano': k.ano,
        'nps': float(k.nps) if k.nps else None,
        'tme': k.tme,
        'chats': k.chats,
    } for k in kpis]
    
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
def api_kpi_save(request):
    """Salvar ou atualizar KPI mensal"""
    user = request.user
    
    # Apenas gestor ou admin podem adicionar KPIs
    if user.role not in ['gestor', 'administrador']:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    analista_id = data.get('analista_id')
    mes = data.get('mes')
    ano = data.get('ano')
    nps = data.get('nps')
    tme = data.get('tme')
    chats = data.get('chats', 0)
    
    if not all([analista_id, mes, ano]):
        return JsonResponse({'error': 'Campos obrigatórios: analista_id, mes, ano'}, status=400)
    
    try:
        analista = User.objects.get(id=analista_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Analista não encontrado'}, status=404)
    
    # Obter departamento NRS Suporte
    try:
        nrs_dept = Department.objects.get(name='NRS Suporte')
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Departamento NRS Suporte não encontrado'}, status=404)
    
    # Criar ou atualizar
    kpi, created = IndicadorDesempenho.objects.update_or_create(
        analista=analista,
        mes=mes,
        ano=ano,
        department=nrs_dept,
        defaults={
            'nps': nps if nps is not None else None,
            'tme': tme if tme is not None else None,
            'chats': chats or 0,
        }
    )
    
    return JsonResponse({
        'id': kpi.id,
        'created': created,
        'message': 'KPI salvo com sucesso'
    })


@login_required
@require_http_methods(["DELETE"])
def api_kpi_delete(request, pk):
    """Excluir KPI"""
    user = request.user
    
    # Apenas gestor ou admin podem excluir KPIs
    if user.role not in ['gestor', 'administrador']:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    try:
        kpi = IndicadorDesempenho.objects.get(id=pk)
        kpi.delete()
        return JsonResponse({'message': 'KPI excluído com sucesso'})
    except IndicadorDesempenho.DoesNotExist:
        return JsonResponse({'error': 'KPI não encontrado'}, status=404)
