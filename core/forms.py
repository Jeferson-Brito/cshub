from django import forms
import re
from .models import Complaint, User


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'id_ra', 'cpf_cliente', 'nome_cliente', 'sobrenome',
            'email_cliente', 'telefone', 'loja_cod',
            'origem_contato', 'tipo_reclamacao', 'descricao', 'status', 'analista',
            'data_reclamacao', 'data_resposta', 'nota_satisfacao',
            'volta_fazer_negocio', 'feedback_text'
        ]
        widgets = {
            'id_ra': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o ID da reclamação'
            }),
            'cpf_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'nome_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do cliente'
            }),
            'sobrenome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome do cliente'
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'cliente@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'loja_cod': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código da loja'
            }),
            'origem_contato': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva detalhadamente a reclamação do cliente...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'analista': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_reclamacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'data_resposta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tipo_reclamacao': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nota_satisfacao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'placeholder': '0 a 10'
            }),
            'volta_fazer_negocio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Feedback do cliente (opcional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar campo analista baseado no tipo de usuário
        analistas_queryset = User.objects.filter(role='analista', ativo=True).order_by('username')
        
        if user:
            if user.is_gestor():
                # Gestor pode ver e alterar analistas
                self.fields['analista'].queryset = analistas_queryset
                self.fields['analista'].required = False
                self.fields['analista'].empty_label = "Selecione um analista (opcional)"
                # Garantir que seja um Select visível e forçar atualização do queryset
                widget = forms.Select(attrs={'class': 'form-control'})
                self.fields['analista'].widget = widget
                # Forçar atualização das choices do widget
                self.fields['analista'].widget.choices = self.fields['analista'].widget.choices
            elif user.is_analista():
                # Analista não pode alterar, mas o campo deve estar presente (oculto)
                self.fields['analista'].queryset = analistas_queryset
                self.fields['analista'].initial = user
                self.fields['analista'].widget = forms.HiddenInput()
            else:
                # Outros usuários
                self.fields['analista'].queryset = analistas_queryset
                self.fields['analista'].required = False
                self.fields['analista'].empty_label = "Selecione um analista"
                widget = forms.Select(attrs={'class': 'form-control'})
                self.fields['analista'].widget = widget
        else:
            # Se não houver usuário, mostrar todos os analistas
            self.fields['analista'].queryset = analistas_queryset
            self.fields['analista'].empty_label = "Selecione um analista"
            widget = forms.Select(attrs={'class': 'form-control'})
            self.fields['analista'].widget = widget
    
    def clean_cpf_cliente(self):
        """Remove formatação do CPF antes de salvar (apenas números)"""
        cpf = self.cleaned_data.get('cpf_cliente')
        if cpf:
            # Remove tudo que não é número
            cpf_clean = re.sub(r'\D', '', cpf)
            
            # Validar que tem exatamente 11 dígitos
            if len(cpf_clean) != 11:
                raise forms.ValidationError('CPF deve conter exatamente 11 dígitos.')
            
            return cpf_clean
        return cpf
    
    def clean_nota_satisfacao(self):
        """Validar que a nota está entre 0 e 10"""
        nota = self.cleaned_data.get('nota_satisfacao')
        if nota is not None:
            if nota < 0 or nota > 10:
                raise forms.ValidationError('A nota de satisfação deve estar entre 0 e 10.')
        return nota
    
    def clean_data_reclamacao(self):
        """Preservar data da reclamação se não for fornecida na edição"""
        data = self.cleaned_data.get('data_reclamacao')
        # Se estiver editando e a data não foi fornecida, manter a data existente
        if self.instance and self.instance.pk and not data:
            return self.instance.data_reclamacao
        return data


