# 🚀 Deploy do CSHub

## 📦 Arquivos Criados para Deploy

Os seguintes arquivos foram criados para facilitar o deploy:

1. **DEPLOY.md** - Guia completo e detalhado de deploy
2. **DEPLOY_RAPIDO.txt** - Guia resumido passo a passo
3. **Procfile** - Configuração para Render/Railway
4. **runtime.txt** - Versão do Python
5. **render.yaml** - Blueprint para deploy automático no Render
6. **.gitignore** - Arquivos a ignorar no Git
7. **GERAR_SECRET_KEY.bat** - Script para gerar SECRET_KEY

## 🎯 Opção Recomendada: Render.com

### Por que Render?
- ✅ **Gratuito** para começar
- ✅ PostgreSQL incluído
- ✅ HTTPS automático
- ✅ Deploy automático via GitHub
- ✅ Interface simples
- ✅ Suporte a Python/Django

### Limitações do Plano Gratuito:
- Serviço pode "dormir" após 15 minutos de inatividade
- Primeira requisição após dormir pode levar 30-60 segundos
- Para produção 24/7, considere o plano Starter ($7/mês)

## 📋 Checklist Rápido

1. [ ] Criar conta no GitHub
2. [ ] Enviar código para GitHub
3. [ ] Criar conta no Render.com
4. [ ] Criar banco PostgreSQL no Render
5. [ ] Criar Web Service no Render
6. [ ] Configurar variáveis de ambiente
7. [ ] Executar migrações
8. [ ] Testar acesso

## 🔧 Configurações Ajustadas

O arquivo `settings.py` foi atualizado para:
- ✅ Detectar ambiente (DEBUG via variável de ambiente)
- ✅ ALLOWED_HOSTS configurável via variável
- ✅ Cookies seguros automáticos em produção
- ✅ Suporte a variáveis de ambiente

## 📚 Próximos Passos

1. Leia o arquivo **DEPLOY_RAPIDO.txt** para um guia passo a passo
2. Ou leia **DEPLOY.md** para instruções detalhadas
3. Siga as instruções para colocar seu sistema no ar!

## 💡 Dicas Importantes

- **SECRET_KEY**: Use o script `GERAR_SECRET_KEY.bat` para gerar uma chave segura
- **ALLOWED_HOSTS**: Atualize com o domínio que o Render fornecer
- **Backup**: Configure backups do banco de dados
- **Monitoramento**: Acompanhe os logs no dashboard do Render

## 🆘 Precisa de Ajuda?

Consulte o arquivo **DEPLOY.md** que contém:
- Troubleshooting
- Soluções para problemas comuns
- Dicas de segurança
- Configurações avançadas

---

**Boa sorte com o deploy! 🎉**

