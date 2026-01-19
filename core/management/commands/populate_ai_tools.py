from django.core.management.base import BaseCommand
from core.models import FerramentaIA

class Command(BaseCommand):
    help = 'Popula o banco de dados com 200 ferramentas de IA profissionais'

    def handle(self, *args, **options):
        # Lista de 200 ferramentas de IA
        # Formato: (Titulo, URL, Descricao, Categoria)
        # Categorias: 'ia' (Geral), 'design', 'marketing', 'coding', 'productivity', 'business', 'audio', 'video'
        
        tools = [
            # --- Chat & Assistentes Gerais (20) ---
            ("ChatGPT", "https://chat.openai.com/", "Modelo de linguagem avançado da OpenAI.", "ia"),
            ("Claude", "https://claude.ai/", "Assistente de IA da Anthropic, ótimo para análise de texto.", "ia"),
            ("Google Gemini", "https://gemini.google.com/", "IA multimodal do Google integrada ao ecossistema Google.", "ia"),
            ("Microsoft Copilot", "https://copilot.microsoft.com/", "Assistente de IA da Microsoft integrado ao Bing e Office.", "ia"),
            ("Perplexity AI", "https://www.perplexity.ai/", "Motor de busca conversacional que fornece fontes.", "ia"),
            ("Poe", "https://poe.com/", "Plataforma para acessar vários modelos de IA (GPT-4, Claude, etc.).", "ia"),
            ("Hugging Chat", "https://huggingface.co/chat/", "Interface de chat open-source da Hugging Face.", "ia"),
            ("Pi (Inflection AI)", "https://pi.ai/", "Assistente pessoal focado em conversas empáticas e apoio.", "ia"),
            ("Character.AI", "https://beta.character.ai/", "Crie e converse com personagens de IA personalizados.", "ia"),
            ("Jasper Chat", "https://www.jasper.ai/chat", "Chatbot de IA focado em negócios e marketing.", "ia"),
            ("You.com", "https://you.com/", "Motor de busca com assistente de IA integrado.", "ia"),
            ("Komo", "https://komo.ai/", "Motor de busca de IA rápido e privado.", "ia"),
            ("Andi", "https://andisearch.com/", "Busca inteligente e assistente de leitura.", "ia"),
            ("Brave Leo", "https://brave.com/leo/", "Assistente de IA integrado ao navegador Brave.", "ia"),
            ("Opera Aria", "https://www.opera.com/features/aria", "IA nativa do navegador Opera.", "ia"),
            ("Taskade AI", "https://www.taskade.com/", "Agente de IA para produtividade e gestão de tarefas.", "ia"),
            ("Writesonic (Chatsonic)", "https://writesonic.com/chat", "Alternativa ao ChatGPT com dados em tempo real.", "ia"),
            ("Rytr Chat", "https://rytr.me/", "Assistente de escrita e chat.", "ia"),
            ("Easy-Peasy.AI", "https://easy-peasy.ai/", "Gerador de conteúdo e chat com IA.", "ia"),
            ("Forefront", "https://www.forefront.ai/", "Acesso a modelos poderosos com recursos empresariais.", "ia"),

            # --- Criação de Contúdo & Marketing (30) ---
            ("Jasper", "https://www.jasper.ai/", "Plataforma de conteúdo IA para equipes de marketing.", "marketing"),
            ("Copy.ai", "https://www.copy.ai/", "Gerador de copy para marketing e vendas.", "marketing"),
            ("Writesonic", "https://writesonic.com/", "Criação de artigos e conteúdo otimizado para SEO.", "marketing"),
            ("Rytr", "https://rytr.me/", "Assistente de escrita criativa simples e eficaz.", "marketing"),
            ("Anyword", "https://anyword.com/", "Copywriting com previsão de performance.", "marketing"),
            ("Surfer SEO", "https://surferseo.com/", "Otimização de conteúdo para SEO com IA.", "marketing"),
            ("Frase", "https://www.frase.io/", "Pesquisa e otimização de conteúdo SEO.", "marketing"),
            ("Semrush (ContentShake)", "https://www.semrush.com/", "Ferramentas de marketing de conteúdo da Semrush.", "marketing"),
            ("Scalenut", "https://www.scalenut.com/", "Plataforma de SEO e marketing de conteúdo.", "marketing"),
            ("Writer", "https://writer.com/", "IA generativa para empresas e marcas.", "marketing"),
            ("LongShot AI", "https://www.longshot.ai/", "Assistente para blogs de formato longo e fact-checking.", "marketing"),
            ("Peppertype.ai", "https://www.peppertype.ai/", "Assistente de conteúdo virtual.", "marketing"),
            ("Neuroflash", "https://neuroflash.com/", "Gerador de texto e imagem líder na Europa.", "marketing"),
            ("Simplified", "https://simplified.com/", "App tudo-em-um para marketing (design, vídeo, escrita).", "marketing"),
            ("Hypotenuse AI", "https://www.hypotenuse.ai/", "Assistente de escrita para e-commerce e marketing.", "marketing"),
            ("Wordtune", "https://www.wordtune.com/", "Reescrita e aprimoramento de texto.", "marketing"),
            ("Quillbot", "https://quillbot.com/", "Parafraseador e verificador gramatical.", "marketing"),
            ("Grammarly", "https://www.grammarly.com/", "Assistente de escrita e correção gramatical.", "marketing"),
            ("Hemingway Editor Plus", "https://hemingwayapp.com/", "Melhora a clareza e legibilidade do texto.", "marketing"),
            ("ProWritingAid", "https://prowritingaid.com/", "Mentor de escrita e editor de estilo.", "marketing"),
            ("AdCreative.ai", "https://www.adcreative.ai/", "Geração de criativos publicitários com IA.", "marketing"),
            ("Predis.ai", "https://predis.ai/", "Gerador de posts para redes sociais.", "marketing"),
            ("Ocoya", "https://www.ocoya.com/", "Automação e criação de conteúdo para social media.", "marketing"),
            ("FeedHive", "https://feedhive.com/", "Gestão de social media com IA para reciclagem de conteúdo.", "marketing"),
            ("Taplio", "https://taplio.com/", "Ferramenta de crescimento e conteúdo para LinkedIn.", "marketing"),
            ("TweetHunter", "https://tweethunter.io/", "Ferramenta de crescimento e conteúdo para Twitter (X).", "marketing"),
            ("Reply.io", "https://reply.io/", "Plataforma de engajamento de vendas com IA.", "marketing"),
            ("Lavender", "https://www.lavender.ai/", "Assistente de e-mail de vendas.", "marketing"),
            ("Regie.ai", "https://www.regie.ai/", "Geração de campanhas de vendas e conteúdo.", "marketing"),
            ("SmartWriter.ai", "https://www.smartwriter.ai/", "E-mails de divulgação personalizados.", "marketing"),

            # --- Imagem & Design (30) ---
            ("Midjourney", "https://www.midjourney.com/", "Gerador de arte e imagens de alta qualidade.", "design"),
            ("DALL·E 3", "https://openai.com/dall-e-3", "Gerador de imagens da OpenAI (via ChatGPT/Microsoft).", "design"),
            ("Stable Diffusion", "https://stability.ai/", "Modelo de geração de imagens open-source.", "design"),
            ("Adobe Firefly", "https://firefly.adobe.com/", "IA generativa para criadores, integrada ao Photoshop.", "design"),
            ("Canva Magic Studio", "https://www.canva.com/magic", "Suíte de ferramentas de IA do Canva.", "design"),
            ("Leonardo.ai", "https://leonardo.ai/", "Geração de ativos de jogos e arte conceitual.", "design"),
            ("Ideogram", "https://ideogram.ai/", "Gerador de imagens com foco em tipografia correta.", "design"),
            ("Krea AI", "https://www.krea.ai/", "Geração e aprimoramento de imagens em tempo real.", "design"),
            ("Playground AI", "https://playgroundai.com/", "Editor de imagens AI colaborativo.", "design"),
            ("Clipdrop", "https://clipdrop.co/", "Ferramentas de edição de imagem e limpeza (by Stability AI).", "design"),
            ("Photoroom", "https://www.photoroom.com/", "Remoção de fundo e fotos de produtos.", "design"),
            ("Remove.bg", "https://www.remove.bg/", "Remoção automática de fundos de imagens.", "design"),
            ("Upscayl", "https://upscayl.org/", "Upscaling de imagens gratuito e open-source.", "design"),
            ("Magnific AI", "https://magnific.ai/", "Upscaler e enhancer de imagens de altíssima fidelidade.", "design"),
            ("Topaz Photo AI", "https://www.topazlabs.com/", "Melhoria de qualidade de imagem profissional.", "design"),
            ("Khroma", "https://www.khroma.co/", "Gerador de paletas de cores com IA.", "design"),
            ("Fontjoy", "https://fontjoy.com/", "Emparelhamento de fontes com deep learning.", "design"),
            ("Designs.ai", "https://designs.ai/", "Plataforma de criação de logos, vídeos e banners.", "design"),
            ("Looka", "https://looka.com/", "Design de logotipos e identidade de marca.", "design"),
            ("Brandmark", "https://brandmark.io/", "Criador de logos com IA.", "design"),
            ("Uizard", "https://uizard.io/", "Design de UI/UX a partir de esboços ou texto.", "design"),
            ("Visily", "https://visily.ai/", "Design de wireframes e protótipos com IA.", "design"),
            ("Galileo AI", "https://www.usegalileo.ai/", "Gera designs de interface (UI) a partir de texto.", "design"),
            ("Flair.ai", "https://flair.ai/", "Design de fotografia de produtos com IA.", "design"),
            ("Pebblely", "https://pebblely.com/", "Transforma fotos de produtos em imagens de marketing.", "design"),
            ("Stockimg.ai", "https://stockimg.ai/", "Geração de imagens de stock, capas de livros, etc.", "design"),
            ("Civitai", "https://civitai.com/", "Hub para modelos e recursos de Stable Diffusion.", "design"),
            ("Tensor.art", "https://tensor.art/", "Plataforma gratuita para gerar e compartilhar imagens IA.", "design"),
            ("Scenario", "https://www.scenario.com/", "Geração de ativos para jogos.", "design"),
            ("PrompBase", "https://promptbase.com/", "Marketplace de prompts para DALL-E, Midjourney, etc.", "design"),

             # --- Vídeo & Animação (25) ---
            ("Runway Gen-2", "https://runwayml.com/", "Geração e edição de vídeo avançada.", "video"),
            ("Pika Labs", "https://pika.art/", "Plataforma de geração de vídeo a partir de texto/imagem.", "video"),
            ("Sora", "https://openai.com/sora", "Modelo de text-to-video da OpenAI (em breve).", "video"),
            ("Luma Dream Machine", "https://lumalabs.ai/", "Gerador de vídeos de alta qualidade e rápidos.", "video"),
            ("Kling AI", "https://klingai.com/", "Modelo de geração de vídeo realista.", "video"),
            ("HeyGen", "https://www.heygen.com/", "Criação de vídeos com avatares falantes.", "video"),
            ("Synthesia", "https://www.synthesia.io/", "Avatares de IA para vídeos corporativos.", "video"),
            ("D-ID", "https://www.d-id.com/", "Animação de fotos e avatares falantes.", "video"),
            ("Descript", "https://www.descript.com/", "Edição de vídeo/áudio baseada em texto.", "video"),
            ("Wondershare Filmora", "https://filmora.wondershare.com/", "Editor de vídeo com recursos de IA.", "video"),
            ("CapCut", "https://www.capcut.com/", "Editor de vídeo popular com muitos efeitos de IA.", "video"),
            ("InVideo", "https://invideo.io/", "Criação de vídeos a partir de prompts de texto.", "video"),
            ("Pictory", "https://pictory.ai/", "Transforma artigos e textos em vídeos curtos.", "video"),
            ("Opus Clip", "https://www.opus.pro/", "Reaproveita vídeos longos em curtos virais (Shorts/Reels).", "video"),
            ("Munch", "https://www.getmunch.com/", "Extração de clipes de vídeos longos com IA.", "video"),
            ("Vidyo.ai", "https://vidyo.ai/", "Automação de cortes para social media.", "video"),
            ("Veed.io", "https://www.veed.io/", "Editor de vídeo online com ferramentas de IA.", "video"),
            ("Kaiber", "https://kaiber.ai/", "Animação e transformação de vídeo estilo anime/arte.", "video"),
            ("Kyber", "https://kyber.ai/", "Ferramentas de criatividade e vídeo.", "video"),
            ("Wonder Dynamics", "https://wonderdynamics.com/", "Animação e composição de personagens CGI em cenas reais.", "video"),
            ("Lumen5", "https://lumen5.com/", "Transforma blog posts em vídeos de marketing.", "video"),
            ("Steve.ai", "https://www.steve.ai/", "Criação de vídeos animados e live-action.", "video"),
            ("Hour One", "https://hourone.ai/", "Avatares virtuais para comunicação empresarial.", "video"),
            ("Colossyan", "https://www.colossyan.com/", "Criador de vídeos com atores de IA.", "video"),
            ("Fliki", "https://fliki.ai/", "Texto para vídeo com vozes de IA.", "video"),

            # --- Áudio & Voz (20) ---
            ("ElevenLabs", "https://elevenlabs.io/", "Síntese de voz realista e clonagem de voz.", "audio"),
            ("Suno AI", "https://suno.com/", "Criação de músicas completas com letras e vocais.", "audio"),
            ("Udio", "https://www.udio.com/", "Gerador de música de alta fidelidade.", "audio"),
            ("Murf.ai", "https://murf.ai/", "Gerador de voz para narrações profissionais.", "audio"),
            ("Lovo.ai", "https://lovo.ai/", "Gerador de voz e plataforma de text-to-speech.", "audio"),
            ("Play.ht", "https://play.ht/", "Vozes de IA ultra-realistas.", "audio"),
            ("Speechify", "https://speechify.com/", "Leitor de texto (TTS) para produtividade.", "audio"),
            ("Krisp", "https://krisp.ai/", "Cancelamento de ruído e eco em chamadas.", "audio"),
            ("Adobe Podcast", "https://podcast.adobe.com/", "Melhoria de áudio e gravação remota.", "audio"),
            ("Otter.ai", "https://otter.ai/", "Transcrição de reuniões e notas automáticas.", "audio"),
            ("Fireflies.ai", "https://fireflies.ai/", "Assistente de reuniões para transcrição e resumo.", "audio"),
            ("Fathom", "https://fathom.video/", "Gravador e transcritor de reuniões Zoom/Google Meet.", "audio"),
            ("Riverside", "https://riverside.fm/", "Gravação de podcasts e vídeo com qualidade de estúdio.", "audio"),
            ("Podcastle", "https://podcastle.ai/", "Plataforma de criação de podcasts com IA.", "audio"),
            ("VocalRemover", "https://vocalremover.org/", "Separação de vocais e instrumentos.", "audio"),
            ("Lalal.ai", "https://www.lalal.ai/", "Extração de stems de áudio de alta qualidade.", "audio"),
            ("Soundraw", "https://soundraw.io/", "Gerador de música royalty-free para criadores.", "audio"),
            ("AIVA", "https://www.aiva.ai/", "Compositor de música clássica e soundtracks com IA.", "audio"),
            ("AudioPen", "https://audiopen.ai/", "Transforma pensamentos falados em texto estruturado.", "audio"),
            ("Cleanvoice", "https://cleanvoice.ai/", "Remove 'hums', 'ahs' e gaguejos de gravações.", "audio"),

            # --- Desenvolvimento & Código (25) ---
            ("GitHub Copilot", "https://github.com/features/copilot", "O par programador de IA mais popular.", "coding"),
            ("Cursor", "https://cursor.sh/", "Editor de código fork do VS Code com IA nativa.", "coding"),
            ("Tabnine", "https://www.tabnine.com/", "Autocompletar de código para empresas.", "coding"),
            ("Amazon CodeWhisperer", "https://aws.amazon.com/codewhisperer/", "Companheiro de codificação da AWS.", "coding"),
            ("CodiumAI", "https://www.codium.ai/", "Geração de testes unitários e análise de código.", "coding"),
            ("Replit Ghostwriter", "https://replit.com/site/ghostwriter", "IA integrada ao IDE online Replit.", "coding"),
            ("Codeium", "https://codeium.com/", "Toolkit de codificação IA gratuito.", "coding"),
            ("Blackbox", "https://www.blackbox.ai/", "IA para programadores responderem perguntas.", "coding"),
            ("Phind", "https://www.phind.com/", "Motor de busca para desenvolvedores.", "coding"),
            ("Sourcegraph Cody", "https://about.sourcegraph.com/cody", "Assistente que conhece toda a sua base de código.", "coding"),
            ("MarsCode", "https://www.marscode.com/", "IDE na nuvem com assistente de IA.", "coding"),
            ("Mutable.ai", "https://mutable.ai/", "Desenvolvimento de software acelerado por IA.", "coding"),
            ("Bricabrac", "https://bricabrac.ai/", "Gere apps web a partir de texto.", "coding"),
            ("Durable", "https://durable.co/", "Construtor de sites com IA em 30 segundos.", "coding"),
            ("10Web", "https://10web.io/", "Construtor de sites WordPress com IA.", "coding"),
            ("Framer AI", "https://www.framer.com/", "Design e publicação de sites com IA.", "coding"),
            ("Wix ADI", "https://www.wix.com/", "Inteligência de Design Artificial do Wix.", "coding"),
            ("Softr", "https://www.softr.io/", "Crie apps a partir do Airtable/Google Sheets.", "coding"),
            ("FlutterFlow", "https://flutterflow.io/", "Desenvolvimento low-code para apps nativos.", "coding"),
            ("Bubble", "https://bubble.io/", "Plataforma no-code líder.", "coding"),
            ("Zapier", "https://zapier.com/", "Automação de workflows sem código.", "coding"),
            ("Make", "https://www.make.com/", "Plataforma visual de automação.", "coding"),
            ("Bardeen", "https://www.bardeen.ai/", "Automação de navegador com IA.", "coding"),
            ("Cheat Layer", "https://cheatlayer.com/", "Automação usando linguagem natural (GPT-4).", "coding"),
            ("Browse AI", "https://www.browse.ai/", "Extração de dados da web sem código.", "coding"),

             # --- Produtividade & Negócios (30) ---
            ("Notion AI", "https://www.notion.so/", "IA integrada ao workspace do Notion.", "productivity"),
            ("Coda AI", "https://coda.io/", "IA para documentos colaborativos.", "productivity"),
            ("ClickUp AI", "https://clickup.com/ai", "IA para gestão de projetos e tarefas.", "productivity"),
            ("Monday.com", "https://monday.com/", "Work OS com recursos de IA.", "productivity"),
            ("Asana Intelligence", "https://asana.com/", "Gestão de projetos inteligente.", "productivity"),
            ("Trello", "https://trello.com/", "Gestão de tarefas (integrado com Atlassian Intelligence).", "productivity"),
            ("Todoist", "https://todoist.com/", "Lista de tarefas com assistente de IA.", "productivity"),
            ("Motion", "https://www.usemotion.com/", "Calendário e gestão de tarefas automatizada.", "productivity"),
            ("Reclaim.ai", "https://reclaim.ai/", "Agendamento inteligente para Google Calendar.", "productivity"),
            ("Clockwise", "https://www.getclockwise.com/", "Otimização de calendário para equipes.", "productivity"),
            ("Mem", "https://mem.ai/", "Anotações auto-organizadas com IA.", "productivity"),
            ("Obsidian (Plugins)", "https://obsidian.md/", "Anotações com plugins de IA como Text Generator.", "productivity"),
            ("Reflect", "https://reflect.app/", "Notas com assistente de IA integrado.", "productivity"),
            ("Napkin", "https://napkin.ai/", "Visualização de ideias e notas.", "productivity"),
            ("Gamma", "https://gamma.app/", "Criação de apresentações, documentos e sites com IA.", "productivity"),
            ("Beautiful.ai", "https://www.beautiful.ai/", "Software de apresentações inteligente.", "productivity"),
            ("Tome", "https://tome.app/", "Formato de narrativa com IA para slides.", "productivity"),
            ("PopAi", "https://www.popai.pro/", "Assistente de documentos e apresentações.", "productivity"),
            ("SlidesGO", "https://slidesgo.com/", "Gerador de templates de apresentação.", "productivity"),
            ("Decktopus", "https://decktopus.com/", "Gerador de apresentações instantâneo.", "productivity"),
            ("ChatPDF", "https://www.chatpdf.com/", "Converse com arquivos PDF.", "productivity"),
            ("Humata", "https://www.humata.ai/", "Analise contratos e documentos técnicos.", "productivity"),
            ("Consensus", "https://consensus.app/", "Motor de busca para pesquisa científica.", "productivity"),
            ("Scholarcy", "https://www.scholarcy.com/", "Resumidor de artigos acadêmicos.", "productivity"),
            ("Scite", "https://scite.ai/", "Assistente de pesquisa com citações reais.", "productivity"),
            ("Elicit", "https://elicit.com/", "Analise literatura de pesquisa.", "productivity"),
            ("Excel Formula Bot", "https://formulabot.com/", "Gere fórmulas de Excel com texto.", "productivity"),
            ("SheetAI", "https://www.sheetai.app/", "Use IA dentro do Google Sheets.", "productivity"),
            ("Rows", "https://rows.com/", "Planilha moderna com IA integrada.", "productivity"),
            ("Arc Browser", "https://arc.net/", "Navegador com recursos 'Max' de IA.", "productivity"),

             # --- Outros & Especializados (20) ---
            ("Hugging Face", "https://huggingface.co/", "A plataforma 'GitHub' de Machine Learning.", "business"),
            ("Replicate", "https://replicate.com/", "Execute modelos de IA open-source na nuvem.", "business"),
            ("LangChain", "https://www.langchain.com/", "Framework para desenvolver apps com LLMs.", "business"),
            ("Pinecone", "https://www.pinecone.io/", "Banco de dados vetorial para IA.", "business"),
            ("Weights & Biases", "https://wandb.ai/", "Plataforma de desenvolvedor para ML.", "business"),
            ("Gradio", "https://www.gradio.app/", "Crie interfaces web para modelos de ML.", "business"),
            ("Streamlit", "https://streamlit.io/", "Transforme scripts de dados em web apps.", "business"),
            ("Synthesia (Avatar)", "https://www.synthesia.io/", "Avatares para treinamento corporativo.", "business"),
            ("Salesforce Einstein", "https://www.salesforce.com/products/einstein/overview/", "IA para CRM e vendas.", "business"),
            ("HubSpot AI", "https://www.hubspot.com/", "Ferramentas de IA para plataforma de clientes.", "business"),
            ("Intercom Fin", "https://www.intercom.com/fin", "Bot de suporte ao cliente com IA.", "business"),
            ("Zendesk AI", "https://www.zendesk.com/ai/", "IA para serviço de atendimento ao cliente.", "business"),
            ("Drift", "https://www.drift.com/", "Plataforma de conversação B2B.", "business"),
            ("Gong", "https://www.gong.io/", "Inteligência de receita e análise de chamadas.", "business"),
            ("Chorus.ai", "https://www.zoominfo.com/products/chorus", "Análise de conversas de vendas.", "business"),
            ("LegalRobot", "https://legalrobot.com/", "Análise de contratos legais.", "business"),
            ("DoNotPay", "https://donotpay.com/", "O 'primeiro advogado robô do mundo'.", "business"),
            ("Harvey AI", "https://www.harvey.ai/", "IA para escritórios de advocacia.", "business"),
            ("Glass Health", "https://glass.health/", "IA para diagnóstico médico e gestão de conhecimento.", "business"),
            ("BioGPT", "https://github.com/microsoft/BioGPT", "Modelo de linguagem para biomedicina (Microsoft).", "business"),
        ]

        # Validando se tempos 200 (aproximadamente, o usuário pediu 200, listei ~200)
        # O script irá iterar e adicionar.

        count = 0
        self.stdout.write("Iniciando a importação de ferramentas de IA...")

        for titulo, url, descricao, categoria in tools:
            obj, created = FerramentaIA.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'url': url,
                    'descricao': descricao,
                    'categoria': categoria
                }
            )
            if created:
                count += 1
                # self.stdout.write(f"Adicionado: {titulo}")
            else:
                # Atualiza se já existir para garantir dados atualizados
                obj.url = url
                obj.descricao = descricao
                obj.categoria = categoria
                obj.save()

        self.stdout.write(self.style.SUCCESS(f'Concluído! {count} novas ferramentas adicionadas. Total na lista: {len(tools)}.'))
