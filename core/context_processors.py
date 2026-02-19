from .models import Department

def departments(request):
    if not request.user.is_authenticated:
        return {}
        
    all_depts = Department.objects.all().order_by('name')
    selected_dept = None
    
    if request.user.is_administrador():
        # Para Admin, o departamento vem da sessão (contexto escolhido)
        selected_dept_id = request.session.get('selected_department_id')
        if selected_dept_id:
            selected_dept = next((d for d in all_depts if d.id == int(selected_dept_id)), None)
        
        # Se não houver depto na sessão, buscar o ID do 'NRS Suporte' como padrão
        if not selected_dept:
            nrs_dept = next((d for d in all_depts if d.name == 'NRS Suporte'), None)
            if nrs_dept:
                selected_dept = nrs_dept
                request.session['selected_department_id'] = nrs_dept.id
    else:
        # Para outros, o departamento é o fixo do usuário
        selected_dept = request.user.department
        # Restringir all_depts para o próprio depto para evitar vazamento em templates
        if selected_dept:
            all_depts = [selected_dept]
        else:
            all_depts = []

    return {
        'all_departments': all_depts,
        'current_department': selected_dept
    }
