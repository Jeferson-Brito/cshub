# Nexus - Sistema de Gestão de Reclamações

Sistema completo para gestão de reclamações desenvolvido em Django/Python com PostgreSQL.

## 🚀 Funcionalidades

- ✅ Dashboard com métricas em tempo real
- ✅ Gestão completa de reclamações
- ✅ Sistema de usuários (Gestores e Analistas)
- ✅ Filtros avançados e busca inteligente
- ✅ Importação de planilhas XLSX
- ✅ Exportação de dados (CSV/XLSX)
- ✅ Relatórios e estatísticas detalhadas
- ✅ Ações rápidas (mudança de status, atribuição de analista)
- ✅ Histórico completo de atividades
- ✅ Tema claro/escuro

## 📋 Requisitos

- Python 3.11+
- PostgreSQL
- Django 5.0+

## 🔧 Instalação Local

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados no `settings.py` ou use variáveis de ambiente

5. Execute as migrações:
   ```bash
   python manage.py migrate
   python manage.py create_admin_user
   ```

6. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

## 🌐 Deploy no Render

Consulte o arquivo `DEPLOY_RENDER.md` para instruções completas de deploy.


## 🛠️ Comandos Úteis

- Criar usuário admin: `python manage.py create_admin_user`
- Criar dados de exemplo: `python manage.py create_sample_data`
- Gerar SECRET_KEY: `python generate_secret_key.py`

## 📄 Licença

Uso interno.

