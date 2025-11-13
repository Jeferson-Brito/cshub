from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import timedelta
import csv
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
from .models import Complaint, Activity, AuditLog, User
from .forms import ComplaintForm


def login_view_custom(request):
    """View customizada de login que verifica se o usuário está ativo e aceita e-mail"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Buscar usuário por e-mail
            try:
                user = User.objects.get(email=email)
                # Autenticar usando o username do usuário encontrado
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    if user.ativo:
                        login(request, user)
                        messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                        next_url = request.GET.get('next', '/')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Sua conta está inativa. Entre em contato com o administrador.')
                else:
                    messages.error(request, 'E-mail ou senha incorretos. Tente novamente.')
            except User.DoesNotExist:
                messages.error(request, 'E-mail ou senha incorretos. Tente novamente.')
            except User.MultipleObjectsReturned:
                # Se houver múltiplos usuários com o mesmo e-mail, tentar autenticar com o primeiro
                user = User.objects.filter(email=email).first()
                user = authenticate(request, username=user.username, password=password)
                if user is not None and user.ativo:
                    login(request, user)
                    messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'E-mail ou senha incorretos. Tente novamente.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'core/login.html')


@login_required
def dashboard(request):
    total_complaints = Complaint.objects.count()
    pending = Complaint.objects.filter(status='pendente').count()
    in_progress = Complaint.objects.filter(status='em_andamento').count()
    resolved = Complaint.objects.filter(status='resolvido').count()
    awaiting = Complaint.objects.filter(status='aguardando_avaliacao').count()
    
    # Ranking de lojas com mais reclamações (top 5)
    top_stores_ranking = Complaint.objects.values('loja_cod').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Gráficos - simplificado para compatibilidade
    complaints_by_period = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=29-i)
        count = Complaint.objects.filter(created_at__date=date).count()
        complaints_by_period.append({'day': date.isoformat(), 'count': count})
    
    top_stores = Complaint.objects.values('loja_cod').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    satisfaction_by_store = Complaint.objects.filter(
        nota_satisfacao__isnull=False
    ).values('loja_cod').annotate(
        avg=Avg('nota_satisfacao')
    )
    
    complaints_by_status = Complaint.objects.values('status').annotate(
        count=Count('id')
    )
    
    recent_complaints = Complaint.objects.select_related('analista').order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'awaiting': awaiting,
        'recent_complaints': recent_complaints,
        'top_stores': list(top_stores),
        'top_stores_ranking': list(top_stores_ranking),
        'satisfaction_by_store': list(satisfaction_by_store),
        'complaints_by_status': list(complaints_by_status),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def complaint_list(request):
    complaints = Complaint.objects.select_related('analista').all()
    
    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    loja_filter = request.GET.get('loja', '')
    
    if search:
        # Remover formatação do CPF se houver (pontos e traços)
        search_clean = re.sub(r'[^\d\w\s@.-]', '', search)  # Remove apenas pontos e traços, mantém números e letras
        
        # Se parecer um CPF (11 dígitos), buscar apenas números
        numbers_only = re.sub(r'\D', '', search_clean)
        if len(numbers_only) == 11:
            # Buscar CPF sem formatação
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=numbers_only) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
        else:
            # Busca normal
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=search_clean) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if loja_filter:
        complaints = complaints.filter(loja_cod=loja_filter)
    
    complaints = complaints.order_by('-created_at')
    
    paginator = Paginator(complaints, 25)
    page = request.GET.get('page')
    complaints = paginator.get_page(page)
    
    return render(request, 'core/complaint_list.html', {'complaints': complaints})


@login_required
def store_list(request):
    """Lista todas as lojas com reclamações, com filtros e ordenação"""
    # Obter todas as lojas com contagem de reclamações
    stores = Complaint.objects.values('loja_cod').annotate(
        count=Count('id'),
        pendentes=Count('id', filter=Q(status='pendente')),
        em_andamento=Count('id', filter=Q(status='em_andamento')),
        resolvidas=Count('id', filter=Q(status='resolvido')),
        aguardando=Count('id', filter=Q(status='aguardando_avaliacao'))
    )
    
    # Filtros
    search = request.GET.get('search', '')
    min_occurrences = request.GET.get('min_occurrences', '')
    
    if search:
        stores = stores.filter(loja_cod__icontains=search)
    
    if min_occurrences:
        try:
            min_count = int(min_occurrences)
            stores = stores.filter(count__gte=min_count)
        except ValueError:
            pass
    
    # Ordenação
    order_by = request.GET.get('order_by', 'count')
    order_direction = request.GET.get('order_direction', 'desc')
    
    if order_by == 'loja':
        if order_direction == 'asc':
            stores = stores.order_by('loja_cod')
        else:
            stores = stores.order_by('-loja_cod')
    elif order_by == 'count':
        if order_direction == 'asc':
            stores = stores.order_by('count')
        else:
            stores = stores.order_by('-count')
    else:
        stores = stores.order_by('-count')
    
    # Contar total antes da paginação
    total_stores = stores.count()
    
    # Paginação - aplicar limit e offset manualmente
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    
    stores_list = list(stores[start:end])
    
    # Calcular informações de paginação
    total_pages = (total_stores + per_page - 1) // per_page
    
    context = {
        'stores': stores_list,
        'search': search,
        'min_occurrences': min_occurrences,
        'order_by': order_by,
        'order_direction': order_direction,
        'total_stores': total_stores,
        'page': page,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
    }
    
    return render(request, 'core/store_list.html', context)


@login_required
def store_complaints(request, loja_cod):
    """Lista todas as reclamações de uma loja específica"""
    complaints = Complaint.objects.filter(loja_cod=loja_cod).select_related('analista').order_by('-created_at')
    
    # Estatísticas da loja
    store_stats = Complaint.objects.filter(loja_cod=loja_cod).aggregate(
        total=Count('id'),
        pendentes=Count('id', filter=Q(status='pendente')),
        em_andamento=Count('id', filter=Q(status='em_andamento')),
        resolvidas=Count('id', filter=Q(status='resolvido')),
        aguardando=Count('id', filter=Q(status='aguardando_avaliacao'))
    )
    
    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        complaints = complaints.filter(
            Q(id_ra__icontains=search) |
            Q(cpf_cliente__icontains=search) |
            Q(nome_cliente__icontains=search) |
            Q(email_cliente__icontains=search)
        )
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    # Paginação
    paginator = Paginator(complaints, 25)
    page = request.GET.get('page')
    complaints_page = paginator.get_page(page)
    
    context = {
        'loja_cod': loja_cod,
        'complaints': complaints_page,
        'store_stats': store_stats,
        'search': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/store_complaints.html', context)


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    activities = complaint.activities.select_related('usuario').order_by('-created_at')
    return render(request, 'core/complaint_detail.html', {
        'complaint': complaint,
        'activities': activities
    })


@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            if request.user.is_analista():
                complaint.analista = request.user
            complaint.save()
            Activity.objects.create(
                complaint=complaint,
                usuario=request.user,
                comentario='Reclamação criada',
                tipo_interacao='criacao'
            )
            AuditLog.objects.create(
                usuario=request.user,
                action='create',
                target_type='Complaint',
                target_id=complaint.id
            )
            messages.success(request, 'Reclamação criada com sucesso!')
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm(user=request.user)
    return render(request, 'core/complaint_form.html', {'form': form})


@login_required
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint, user=request.user)
        if form.is_valid():
            # Capturar TODOS os valores antigos antes de salvar
            old_data = {
                'id_ra': complaint.id_ra,
                'cpf_cliente': complaint.cpf_cliente,
                'nome_cliente': complaint.nome_cliente,
                'sobrenome': complaint.sobrenome,
                'email_cliente': complaint.email_cliente,
                'telefone': complaint.telefone,
                'loja_cod': complaint.loja_cod,
                'origem_contato': complaint.origem_contato,
                'descricao': complaint.descricao,
                'status': complaint.status,
                'analista': complaint.analista,
                'data_reclamacao': complaint.data_reclamacao,
                'data_resposta': complaint.data_resposta,
                'nota_satisfacao': complaint.nota_satisfacao,
                'feedback_text': complaint.feedback_text,
            }
            
            # Salvar o formulário
            form.save()
            
            # Atualizar a instância do banco para comparar
            complaint.refresh_from_db()
            
            # Mapear nomes de campos para labels amigáveis
            field_labels = {
                'id_ra': 'ID RA',
                'cpf_cliente': 'CPF do Cliente',
                'nome_cliente': 'Nome do Cliente',
                'sobrenome': 'Sobrenome',
                'email_cliente': 'E-mail do Cliente',
                'telefone': 'Telefone',
                'loja_cod': 'Código da Loja',
                'origem_contato': 'Origem do Contato',
                'descricao': 'Descrição',
                'status': 'Status',
                'analista': 'Analista Responsável',
                'data_reclamacao': 'Data da Reclamação',
                'data_resposta': 'Data de Resposta',
                'nota_satisfacao': 'Nota de Satisfação',
                'feedback_text': 'Feedback do Cliente',
            }
            
            # Criar atividades para cada campo alterado
            changes = []
            
            for field_name, old_value in old_data.items():
                new_value = getattr(complaint, field_name)
                
                # Comparar valores, tratando None, strings vazias e ForeignKey
                # Para ForeignKey, comparar os IDs
                if field_name == 'analista':
                    old_id = old_value.id if old_value else None
                    new_id = new_value.id if new_value else None
                    if old_id != new_id:
                        field_label = field_labels.get(field_name, field_name)
                        old_name = old_value.username if old_value else "Não atribuído"
                        new_name = new_value.username if new_value else "Não atribuído"
                        Activity.objects.create(
                            complaint=complaint,
                            usuario=request.user,
                            comentario=f'Campo "{field_label}" alterado de "{old_name}" para "{new_name}"',
                            tipo_interacao='atualizacao'
                        )
                        changes.append(field_name)
                    continue
                
                # Para outros campos, normalizar None e strings vazias
                old_val = old_value if old_value not in (None, "") else ""
                new_val = new_value if new_value not in (None, "") else ""
                
                if str(old_val).strip() != str(new_val).strip():
                    field_label = field_labels.get(field_name, field_name)
                    
                    # Formatação especial para alguns campos
                    if field_name == 'status':
                        old_display = dict(Complaint.STATUS_CHOICES).get(old_value, str(old_value))
                        new_display = complaint.get_status_display()
                        Activity.objects.create(
                            complaint=complaint,
                            usuario=request.user,
                            comentario=f'Campo "{field_label}" alterado de "{old_display}" para "{new_display}"',
                            tipo_interacao='mudanca_status'
                        )
                    elif field_name == 'origem_contato':
                        old_display = dict(Complaint.ORIGEM_CHOICES).get(old_value, str(old_value))
                        new_display = complaint.get_origem_contato_display()
                        Activity.objects.create(
                            complaint=complaint,
                            usuario=request.user,
                            comentario=f'Campo "{field_label}" alterado de "{old_display}" para "{new_display}"',
                            tipo_interacao='atualizacao'
                        )
                    elif field_name in ['data_reclamacao', 'data_resposta']:
                        old_str = old_value.strftime('%d/%m/%Y') if old_value else "Não informada"
                        new_str = new_value.strftime('%d/%m/%Y') if new_value else "Não informada"
                        Activity.objects.create(
                            complaint=complaint,
                            usuario=request.user,
                            comentario=f'Campo "{field_label}" alterado de "{old_str}" para "{new_str}"',
                            tipo_interacao='atualizacao'
                        )
                    else:
                        # Para outros campos, mostrar valores antigo e novo
                        old_str = str(old_value) if old_value else "(vazio)"
                        new_str = str(new_value) if new_value else "(vazio)"
                        Activity.objects.create(
                            complaint=complaint,
                            usuario=request.user,
                            comentario=f'Campo "{field_label}" alterado de "{old_str}" para "{new_str}"',
                            tipo_interacao='atualizacao'
                        )
                    changes.append(field_name)
            
            # Se não houver mudanças, criar atividade genérica
            if not changes:
                Activity.objects.create(
                    complaint=complaint,
                    usuario=request.user,
                    comentario='Informações da reclamação foram atualizadas',
                    tipo_interacao='atualizacao'
                )
            
            messages.success(request, 'Reclamação atualizada com sucesso!')
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm(instance=complaint, user=request.user)
    return render(request, 'core/complaint_form.html', {'form': form, 'complaint': complaint})


@login_required
def complaint_delete(request, pk):
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para excluir reclamações.')
        return redirect('complaint_list')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if not password:
            messages.error(request, 'Por favor, informe sua senha para confirmar a exclusão.')
            return render(request, 'core/complaint_confirm_delete.html', {'complaint': complaint})
        
        # Verificar senha
        user = authenticate(request, username=request.user.username, password=password)
        if not user:
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return render(request, 'core/complaint_confirm_delete.html', {'complaint': complaint})
        
        # Criar atividade antes de excluir
        Activity.objects.create(
            complaint=complaint,
            usuario=request.user,
            comentario=f'Reclamação {complaint.id_ra} foi excluída pelo gestor {request.user.username}',
            tipo_interacao='atualizacao'
        )
        
        AuditLog.objects.create(
            usuario=request.user,
            action='delete',
            target_type='Complaint',
            target_id=complaint.id,
            detalhes_json={'id_ra': complaint.id_ra}
        )
        complaint.delete()
        messages.success(request, 'Reclamação excluída com sucesso!')
        return redirect('complaint_list')
    
    return render(request, 'core/complaint_confirm_delete.html', {'complaint': complaint})


@login_required
def complaint_bulk_delete(request):
    """Exclusão em massa de reclamações - apenas para gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para excluir reclamações.')
        return redirect('complaint_list')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        delete_all = request.POST.get('delete_all') == 'on'
        selected_ids = request.POST.getlist('selected_complaints')
        
        if not password:
            messages.error(request, 'Por favor, informe sua senha para confirmar a exclusão.')
            return redirect('complaint_list')
        
        # Verificar senha
        user = authenticate(request, username=request.user.username, password=password)
        if not user:
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return redirect('complaint_list')
        
        if delete_all:
            # Excluir todas as reclamações
            total = Complaint.objects.count()
            # Criar logs antes de excluir
            for complaint in Complaint.objects.all():
                AuditLog.objects.create(
                    usuario=request.user,
                    action='delete',
                    target_type='Complaint',
                    target_id=complaint.id,
                    detalhes_json={'id_ra': complaint.id_ra}
                )
            Complaint.objects.all().delete()
            messages.success(request, f'Todas as {total} reclamações foram excluídas com sucesso!')
        elif selected_ids:
            # Excluir selecionadas - pode vir como string separada por vírgula
            if isinstance(selected_ids, list) and len(selected_ids) > 0 and ',' in selected_ids[0]:
                selected_ids = selected_ids[0].split(',')
            # Converter para inteiros
            try:
                selected_ids = [int(id) for id in selected_ids if id]
            except (ValueError, TypeError):
                messages.error(request, 'IDs inválidos selecionados.')
                return redirect('complaint_list')
            
            complaints = Complaint.objects.filter(pk__in=selected_ids)
            count = complaints.count()
            for complaint in complaints:
                AuditLog.objects.create(
                    usuario=request.user,
                    action='delete',
                    target_type='Complaint',
                    target_id=complaint.id,
                    detalhes_json={'id_ra': complaint.id_ra}
                )
            complaints.delete()
            messages.success(request, f'{count} reclamação(ões) excluída(s) com sucesso!')
        else:
            messages.error(request, 'Nenhuma reclamação selecionada.')
        
        return redirect('complaint_list')
    
    return redirect('complaint_list')


def logout_view(request):
    """View customizada para logout que aceita GET"""
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('login')


@login_required
def user_list(request):
    """Lista de usuários - apenas para gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter == 'ativo':
        users = users.filter(ativo=True)
    elif status_filter == 'inativo':
        users = users.filter(ativo=False)
    
    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'core/user_list.html', {'users': users})


@login_required
def user_create(request):
    """Criar novo usuário - apenas para gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para criar usuários.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'analista')  # Default para analista
        ativo = request.POST.get('ativo') == 'on'
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já existe.')
            return render(request, 'core/user_form.html', {'form_type': 'create'})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'core/user_form.html', {'form_type': 'create'})
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            ativo=ativo,
            first_name=first_name,
            last_name=last_name
        )
        
        AuditLog.objects.create(
            usuario=request.user,
            action='create',
            target_type='User',
            target_id=user.id,
            detalhes_json={'username': username, 'role': role}
        )
        
        messages.success(request, f'Usuário {username} criado com sucesso!')
        return redirect('user_list')
    
    return render(request, 'core/user_form.html', {'form_type': 'create'})


@login_required
def user_edit(request, pk):
    """Editar usuário - apenas para gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para editar usuários.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.ativo = request.POST.get('ativo') == 'on'
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        
        AuditLog.objects.create(
            usuario=request.user,
            action='update',
            target_type='User',
            target_id=user.id,
            detalhes_json={'username': user.username, 'role': user.role}
        )
        
        messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
        return redirect('user_list')
    
    return render(request, 'core/user_form.html', {'user': user, 'form_type': 'edit'})


@login_required
def user_delete(request, pk):
    """Excluir usuário - apenas para gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para excluir usuários.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=pk)
    
    if user == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user.username
        AuditLog.objects.create(
            usuario=request.user,
            action='delete',
            target_type='User',
            target_id=user.id,
            detalhes_json={'username': username}
        )
        user.delete()
        messages.success(request, f'Usuário {username} excluído com sucesso!')
        return redirect('user_list')
    
    return render(request, 'core/user_confirm_delete.html', {'user': user})


@login_required
def settings_view(request):
    """Página de configurações do sistema"""
    return render(request, 'core/settings.html')


@login_required
def export_complaints_csv(request):
    """Exportar reclamações para CSV"""
    complaints = Complaint.objects.select_related('analista').all()
    
    # Aplicar filtros se existirem
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    loja_filter = request.GET.get('loja', '')
    
    if search:
        search_clean = re.sub(r'[^\d\w\s@.-]', '', search)
        numbers_only = re.sub(r'\D', '', search_clean)
        if len(numbers_only) == 11:
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=numbers_only) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
        else:
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=search_clean) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if loja_filter:
        complaints = complaints.filter(loja_cod=loja_filter)
    
    complaints = complaints.order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reclamacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID RA', 'CPF', 'Nome', 'Sobrenome', 'E-mail', 'Telefone',
        'Loja', 'Origem', 'Status', 'Analista', 'Data Reclamação',
        'Data Resposta', 'Nota Satisfação', 'Descrição'
    ])
    
    for complaint in complaints:
        writer.writerow([
            complaint.id_ra,
            complaint.cpf_cliente,
            complaint.nome_cliente,
            complaint.sobrenome or '',
            complaint.email_cliente,
            complaint.telefone or '',
            complaint.loja_cod,
            complaint.get_origem_contato_display(),
            complaint.get_status_display(),
            complaint.analista.username if complaint.analista else '',
            complaint.data_reclamacao.strftime('%d/%m/%Y') if complaint.data_reclamacao else '',
            complaint.data_resposta.strftime('%d/%m/%Y') if complaint.data_resposta else '',
            complaint.nota_satisfacao or '',
            complaint.descricao
        ])
    
    return response


@login_required
def export_complaints_xlsx(request):
    """Exportar reclamações para XLSX"""
    complaints = Complaint.objects.select_related('analista').all()
    
    # Aplicar filtros se existirem
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    loja_filter = request.GET.get('loja', '')
    
    if search:
        search_clean = re.sub(r'[^\d\w\s@.-]', '', search)
        numbers_only = re.sub(r'\D', '', search_clean)
        if len(numbers_only) == 11:
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=numbers_only) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
        else:
            complaints = complaints.filter(
                Q(id_ra__icontains=search) |
                Q(cpf_cliente__icontains=search_clean) |
                Q(nome_cliente__icontains=search) |
                Q(email_cliente__icontains=search)
            )
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if loja_filter:
        complaints = complaints.filter(loja_cod=loja_filter)
    
    complaints = complaints.order_by('-created_at')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Reclamações"
    
    # Cabeçalho
    headers = [
        'ID RA', 'CPF', 'Nome', 'Sobrenome', 'E-mail', 'Telefone',
        'Loja', 'Origem', 'Status', 'Analista', 'Data Reclamação',
        'Data Resposta', 'Nota Satisfação', 'Descrição'
    ]
    
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Dados
    for row_num, complaint in enumerate(complaints, 2):
        ws.cell(row=row_num, column=1, value=complaint.id_ra)
        ws.cell(row=row_num, column=2, value=complaint.cpf_cliente)
        ws.cell(row=row_num, column=3, value=complaint.nome_cliente)
        ws.cell(row=row_num, column=4, value=complaint.sobrenome or '')
        ws.cell(row=row_num, column=5, value=complaint.email_cliente)
        ws.cell(row=row_num, column=6, value=complaint.telefone or '')
        ws.cell(row=row_num, column=7, value=complaint.loja_cod)
        ws.cell(row=row_num, column=8, value=complaint.get_origem_contato_display())
        ws.cell(row=row_num, column=9, value=complaint.get_status_display())
        ws.cell(row=row_num, column=10, value=complaint.analista.username if complaint.analista else '')
        ws.cell(row=row_num, column=11, value=complaint.data_reclamacao.strftime('%d/%m/%Y') if complaint.data_reclamacao else '')
        ws.cell(row=row_num, column=12, value=complaint.data_resposta.strftime('%d/%m/%Y') if complaint.data_resposta else '')
        ws.cell(row=row_num, column=13, value=complaint.nota_satisfacao or '')
        ws.cell(row=row_num, column=14, value=complaint.descricao)
    
    # Ajustar largura das colunas
    column_widths = [12, 15, 20, 20, 25, 15, 10, 15, 15, 15, 15, 15, 10, 50]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = width
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reclamacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    wb.save(response)
    return response


@login_required
def export_stores_csv(request):
    """Exportar lojas para CSV"""
    stores = Complaint.objects.values('loja_cod').annotate(
        count=Count('id'),
        pendentes=Count('id', filter=Q(status='pendente')),
        em_andamento=Count('id', filter=Q(status='em_andamento')),
        resolvidas=Count('id', filter=Q(status='resolvido')),
        aguardando=Count('id', filter=Q(status='aguardando_avaliacao'))
    ).order_by('-count')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="lojas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Código da Loja', 'Total', 'Pendentes', 'Em Andamento', 'Aguardando Avaliação', 'Resolvidas'])
    
    for store in stores:
        writer.writerow([
            store['loja_cod'],
            store['count'],
            store['pendentes'],
            store['em_andamento'],
            store['aguardando'],
            store['resolvidas']
        ])
    
    return response


@login_required
def export_stores_xlsx(request):
    """Exportar lojas para XLSX"""
    stores = Complaint.objects.values('loja_cod').annotate(
        count=Count('id'),
        pendentes=Count('id', filter=Q(status='pendente')),
        em_andamento=Count('id', filter=Q(status='em_andamento')),
        resolvidas=Count('id', filter=Q(status='resolvido')),
        aguardando=Count('id', filter=Q(status='aguardando_avaliacao'))
    ).order_by('-count')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Lojas"
    
    headers = ['Código da Loja', 'Total', 'Pendentes', 'Em Andamento', 'Aguardando Avaliação', 'Resolvidas']
    
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    for row_num, store in enumerate(stores, 2):
        ws.cell(row=row_num, column=1, value=store['loja_cod'])
        ws.cell(row=row_num, column=2, value=store['count'])
        ws.cell(row=row_num, column=3, value=store['pendentes'])
        ws.cell(row=row_num, column=4, value=store['em_andamento'])
        ws.cell(row=row_num, column=5, value=store['aguardando'])
        ws.cell(row=row_num, column=6, value=store['resolvidas'])
    
    column_widths = [20, 10, 12, 15, 20, 12]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = width
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="lojas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    wb.save(response)
    return response


@login_required
def export_users_csv(request):
    """Exportar usuários para CSV - apenas gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para exportar usuários.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('username')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'E-mail', 'Nome', 'Sobrenome', 'Perfil', 'Ativo', 'Último Login', 'Data de Criação'])
    
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.first_name or '',
            user.last_name or '',
            user.get_role_display(),
            'Sim' if user.ativo else 'Não',
            user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else '',
            user.date_joined.strftime('%d/%m/%Y %H:%M') if user.date_joined else ''
        ])
    
    return response


@login_required
def export_users_xlsx(request):
    """Exportar usuários para XLSX - apenas gestores"""
    if not request.user.is_gestor():
        messages.error(request, 'Você não tem permissão para exportar usuários.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('username')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuários"
    
    headers = ['Username', 'E-mail', 'Nome', 'Sobrenome', 'Perfil', 'Ativo', 'Último Login', 'Data de Criação']
    
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    for row_num, user in enumerate(users, 2):
        ws.cell(row=row_num, column=1, value=user.username)
        ws.cell(row=row_num, column=2, value=user.email)
        ws.cell(row=row_num, column=3, value=user.first_name or '')
        ws.cell(row=row_num, column=4, value=user.last_name or '')
        ws.cell(row=row_num, column=5, value=user.get_role_display())
        ws.cell(row=row_num, column=6, value='Sim' if user.ativo else 'Não')
        ws.cell(row=row_num, column=7, value=user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else '')
        ws.cell(row=row_num, column=8, value=user.date_joined.strftime('%d/%m/%Y %H:%M') if user.date_joined else '')
    
    column_widths = [20, 30, 20, 20, 15, 10, 20, 20]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = width
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    wb.save(response)
    return response
