# 💤 Por que o site "dorme" no Render Free?

## O que está acontecendo?

No **plano Free do Render**, os serviços web entram em "sleep mode" (modo de espera) após **15 minutos de inatividade**. Isso significa:

1. ⏰ Se ninguém acessar o site por 15 minutos, ele "dorme"
2. 🔄 Quando alguém acessa, o Render precisa "acordar" o serviço
3. ⏱️ Esse processo leva aproximadamente **10-30 segundos**
4. ✅ Depois disso, o site funciona normalmente

## Por que isso acontece?

O plano Free é uma cortesia do Render para projetos pessoais/testes. Para manter os custos baixos, eles colocam serviços inativos em modo de espera.

## Soluções

### Opção 1: Aceitar o delay (Gratuito)
- ✅ Gratuito
- ⏱️ Primeiro acesso após dormir leva ~15 segundos
- ✅ Funciona perfeitamente após "acordar"

### Opção 2: Usar um serviço de "ping" (Gratuito)
Configure um serviço externo para "acordar" seu site periodicamente:

**Serviços gratuitos:**
- **UptimeRobot**: https://uptimerobot.com
- **Cron-Job.org**: https://cron-job.org
- **EasyCron**: https://www.easycron.com

**Como configurar:**
1. Crie uma conta em um desses serviços
2. Configure para fazer uma requisição HTTP a cada 10-14 minutos
3. URL: `https://seu-app.onrender.com/`
4. Isso mantém o serviço "acordado"

### Opção 3: Upgrade para plano pago (Recomendado para produção)
- 💰 A partir de $7/mês
- ✅ Site sempre online (sem sleep)
- ✅ Melhor performance
- ✅ Suporte prioritário

## Sobre o erro de exportação

O erro que você viu nos logs é relacionado a:
1. **Worker timeout**: Operações longas (como exportar planilhas grandes) podem exceder 30 segundos
2. **Conexão SSL**: Problemas de reconexão após o site "acordar"

**Soluções aplicadas:**
- ✅ Configuração SSL corrigida
- ✅ Connection pooling melhorado
- ✅ Timeout de conexão ajustado

## Recomendações

Para uso em produção com equipe:
- 💡 Considere upgrade para plano pago ($7/mês)
- 💡 Ou use serviço de ping gratuito para manter ativo
- 💡 Para exportações grandes, considere processamento assíncrono (futuro)

