import hashlib
import json
import logging
import re
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Rich catalog of diverse seed jobs across ALL categories, shifts, and contract types
SEED_JOBS: List[Dict[str, Any]] = [
    # --- ADMINISTRAÇÃO & FINANÇAS ---
    {
        "id": "seed-adm-1",
        "title": "Assistente Administrativo Júnior",
        "company": "Grupo Alvorada Empresarial",
        "location": "São Paulo, SP (Presencial)",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 2.400 - R$ 2.800",
        "job_type": "CLT (Efetivo)",
        "shift": "integral",
        "contract_type": "clt",
        "category": "administracao",
        "description": "Buscamos Assistente Administrativo Júnior para atuar em rotinas de escritório. Atividades: Emissão de notas fiscais, controle de contas a pagar e receber, conciliação bancária, atendimento a fornecedores e preenchimento de planilhas no Excel. Requisitos: Ensino médio completo ou superior cursando, domínio de Excel e boa comunicação. Horário comercial de segunda a sexta (08h às 17h48).",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-adm-2",
        "title": "Auxiliar de Escritório - Turno Matutino",
        "company": "Comercial Martins Ltda",
        "location": "Curitiba, PR",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 1.850 + Vale Refeição",
        "job_type": "CLT (Efetivo)",
        "shift": "manha",
        "contract_type": "clt",
        "category": "administracao",
        "description": "Vaga para Auxiliar de Escritório no turno da manhã (07:00 às 13:00). Apoio na digitalização de documentos, arquivo, envio de correspondências e atendimento telefônico. Requisitos: Conhecimento básico de informática, organização e pontualidade.",
        "date_posted": "Ontem"
    },

    # --- RECURSOS HUMANOS (RH) & DP ---
    {
        "id": "seed-rh-1",
        "title": "Assistente de Recursos Humanos (R&S)",
        "company": "Talentos Conectados RH",
        "location": "Belo Horizonte, MG (Híbrido)",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 2.600 + Benefícios",
        "job_type": "CLT (Efetivo)",
        "shift": "integral",
        "contract_type": "clt",
        "category": "rh",
        "description": "Responsável por triagem de currículos na plataforma Gupy, agendamento de entrevistas, alinhamento de perfil com gestores e aplicação de testes admissionais. Apoio ao departamento pessoal em admissões e controle de ponto. Requisitos: Superior em Psicologia, RH ou Administração em andamento ou completo.",
        "date_posted": "Há 1 dia"
    },
    {
        "id": "seed-rh-2",
        "title": "Estagiário de Recursos Humanos",
        "company": "Nexus Soluções em Pessoas",
        "location": "Rio de Janeiro, RJ (Híbrido)",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "Bolsa R$ 1.300 + VT + VR",
        "job_type": "Estágio",
        "shift": "manha",
        "contract_type": "estagio",
        "category": "rh",
        "description": "Oportunidade de estágio no turno matutino (08h às 14h, 30h semanais). Apoio nas atividades de recrutamento e seleção, comunicação interna, integração de novos colaboradores e gestão de benefícios. Cursando Recursos Humanos, Psicologia ou Pedagogia a partir do 2º período.",
        "date_posted": "Há 2 dias"
    },

    # --- JOVEM / MENOR APRENDIZ ---
    {
        "id": "seed-apr-1",
        "title": "Jovem Aprendiz Administrativo",
        "company": "Rede Drogaria Mais Vida",
        "location": "Campinas, SP",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 950 (Bolsa Aprendiz)",
        "job_type": "Menor Aprendiz",
        "shift": "tarde",
        "contract_type": "aprendiz",
        "category": "administracao",
        "description": "Vaga exclusiva para Jovem Aprendiz / Menor Aprendiz conforme a Lei da Aprendizagem. Turno vespertino (13:00 às 17:00, 4h diárias). Atividades: Organização de prontuários, preenchimento de cadastros no sistema, suporte ao time de recepção e arquivamento de notas fiscais. Requisitos: Ter entre 14 e 24 anos incompletos, estar cursando ou ter concluído o Ensino Médio.",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-apr-2",
        "title": "Menor Aprendiz em Logística e Estoque",
        "company": "LogSul Distribuição",
        "location": "Porto Alegre, RS",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 980 + Vale Transporte",
        "job_type": "Menor Aprendiz",
        "shift": "manha",
        "contract_type": "aprendiz",
        "category": "logistica",
        "description": "Programa Menor Aprendiz no setor de Logística. Turno da manhã (08:00 às 12:00). Auxílio na etiquetagem de caixas, conferência de volumes, lançamento de entradas e saídas no sistema WMS e organização do estoque. Cursando Ensino Médio.",
        "date_posted": "Há 3 dias"
    },

    # --- LOGÍSTICA & ESTOQUE ---
    {
        "id": "seed-log-1",
        "title": "Auxiliar de Logística - Turno Noturno",
        "company": "ExpressLog Transportes",
        "location": "Guarulhos, SP",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 2.100 + Adicional Noturno (30%) + Fretado",
        "job_type": "CLT (Efetivo)",
        "shift": "noite",
        "contract_type": "clt",
        "category": "logistica",
        "description": "Atuação no galpão logístico durante o turno noturno (22:00 às 06:00, escala 6x1). Carga e descarga de carretas, separação de mercadorias (picking), conferência via coletor de dados e paletização. Requisitos: Ensino Fundamental completo e disponibilidade para trabalho no período da noite.",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-log-2",
        "title": "Estoquista / Conferente de Mercadorias",
        "company": "Center Varejo Distribuidora",
        "location": "Recife, PE",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 1.950 + Vale Alimentação",
        "job_type": "CLT (Efetivo)",
        "shift": "integral",
        "contract_type": "clt",
        "category": "logistica",
        "description": "Conferência física de notas fiscais de entrada e saída, abastecimento de prateleiras, inventário rotativo e separação de pedidos. Horário integral comercial (08:00 às 17:30).",
        "date_posted": "Há 1 dia"
    },

    # --- ATENDIMENTO, VENDAS & COMERCIAL ---
    {
        "id": "seed-ven-1",
        "title": "Atendente de Loja e Balcão",
        "company": "Moda & Estilo Varejo",
        "location": "Salvador, BA (Shopping)",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 1.780 + Comissões",
        "job_type": "CLT (Efetivo)",
        "shift": "escala",
        "contract_type": "clt",
        "category": "vendas_marketing",
        "description": "Atendimento receptivo aos clientes, suporte na escolha de produtos, organização de araras, conferência no caixa PDV e reposição de peças. Escala 6x1 com folga semanal, horário das 14:00 às 22:00.",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-ven-2",
        "title": "Operador de SAC / Telemarketing Receptivo",
        "company": "ContactCenter Brasil",
        "location": "Remoto (Brasil)",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 1.620 + Ajuda de Custo Home Office",
        "job_type": "CLT (Efetivo)",
        "shift": "manha",
        "contract_type": "clt",
        "category": "vendas_marketing",
        "description": "Atendimento a clientes via chat, telefone e WhatsApp para esclarecimento de dúvidas e abertura de chamados. Turno matutino (6h diárias de segunda a sábado, 08h às 14h20). Requisitos: Computador com internet e fone de ouvido.",
        "date_posted": "Ontem"
    },

    # --- SERVIÇOS GERAIS & OPERACIONAL ---
    {
        "id": "seed-op-1",
        "title": "Porteiro / Controlador de Acesso - Escala 12x36",
        "company": "SegurMax Facilities",
        "location": "São Paulo, SP",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 2.050 + Cesta Básica + VT",
        "job_type": "CLT (Efetivo)",
        "shift": "escala",
        "contract_type": "clt",
        "category": "operacional",
        "description": "Controle de acesso de moradores, prestadores de serviços e entregadores em condomínio residencial. Atendimento interfone e monitoramento por câmeras de segurança. Escala 12x36 diurna (07h às 19h).",
        "date_posted": "Há 2 dias"
    },

    # --- TECNOLOGIA & PROGRAMAÇÃO ---
    {
        "id": "seed-tech-1",
        "title": "Desenvolvedor Backend Júnior (Python)",
        "company": "TechNova Soluções Digitais",
        "location": "Brasil (Remoto)",
        "site": "LinkedIn",
        "url": "https://linkedin.com",
        "salary": "R$ 4.000 - R$ 5.500",
        "job_type": "CLT (Efetivo)",
        "shift": "integral",
        "contract_type": "clt",
        "category": "tecnologia",
        "description": "Vaga exclusiva para Desenvolvedor Backend Júnior. Desenvolvimento e manutenção de APIs RESTful utilizando Python (FastAPI ou Flask), consultas SQL (PostgreSQL/SQLite), versionamento com Git e integração com microsserviços. Exigimos apenas conhecimentos de nível júnior/iniciante e paixão por código limpo.",
        "date_posted": "Hoje"
    },
    {
        "id": "seed-tech-2",
        "title": "Desenvolvedor Frontend Júnior (React & JS)",
        "company": "Agência WebCode",
        "location": "Remoto",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "R$ 3.800",
        "job_type": "PJ / CLT",
        "shift": "integral",
        "contract_type": "clt",
        "category": "tecnologia",
        "description": "Oportunidade para Desenvolvedor Frontend Júnior. Criação de interfaces responsivas e acessíveis com HTML5, CSS3/Tailwind e React. Consumo de endpoints REST e versionamento com Git. Trabalho 100% home office.",
        "date_posted": "Há 1 dia"
    },
    {
        "id": "seed-tech-3",
        "title": "Estagiário de Suporte Técnico / Helpdesk",
        "company": "InfoServ Informática",
        "location": "Campinas, SP (Presencial)",
        "site": "Indeed",
        "url": "https://indeed.com",
        "salary": "Bolsa R$ 1.200 + VT",
        "job_type": "Estágio",
        "shift": "tarde",
        "contract_type": "estagio",
        "category": "tecnologia",
        "description": "Estágio no turno da tarde (13h às 19h). Atendimento de chamados de suporte técnico de nível 1, formatação e configuração de computadores Windows, instalação de softwares e suporte básico de redes. Cursando TI, Redes ou Ciência da Computação.",
        "date_posted": "Há 3 dias"
    }
]

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', raw_html)
    return re.sub(r'\s+', ' ', clean).strip()

def generate_job_id(title: str, company: str, site: str) -> str:
    hash_str = f"{title}_{company}_{site}".lower()
    return hashlib.md5(hash_str.encode()).hexdigest()[:12]

def fetch_remotive_jobs(search_term: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Only queried when searching tech/remote jobs."""
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {}
        if search_term:
            params["search"] = search_term
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            for r in data.get("jobs", [])[:limit]:
                clean_desc = clean_html(r.get("description", ""))
                jobs.append({
                    "id": f"remotive-{r.get('id')}",
                    "title": r.get("title", ""),
                    "company": r.get("company_name", ""),
                    "location": r.get("candidate_required_location", "Remoto"),
                    "site": "Remotive",
                    "url": r.get("url", ""),
                    "salary": r.get("salary", "Não divulgado"),
                    "job_type": r.get("job_type", "Full-time"),
                    "shift": "integral",
                    "contract_type": "clt",
                    "category": "tecnologia",
                    "description": clean_desc,
                    "date_posted": r.get("publication_date", "")[:10]
                })
    except Exception as e:
        logger.warning(f"Remotive error: {e}")
    return jobs

def fetch_jobspy_jobs(
    search_term: str = "", 
    location: str = "Brasil", 
    sites: Optional[List[str]] = None,
    results_wanted: int = 15
) -> List[Dict[str, Any]]:
    """Scrapes any profession from LinkedIn and Indeed via python-jobspy."""
    if sites is None:
        sites = ["indeed", "linkedin"]
        
    jobs = []
    try:
        from jobspy import scrape_jobs
        
        country = "brazil" if any(w in location.lower() for w in ["brasil", "brazil", "sp", "rj", "mg", "pr", "rs"]) else "usa"
        
        df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=168,
            country_indeed=country
        )
        
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                site_name = str(row.get("site", "Web")).capitalize()
                title = str(row.get("title", "Sem título"))
                company = str(row.get("company", "Empresa confidencial"))
                desc = clean_html(str(row.get("description", "")))
                job_url = str(row.get("job_url", ""))
                loc = str(row.get("location", location))
                
                min_amt = row.get("min_amount")
                max_amt = row.get("max_amount")
                interval = row.get("interval", "")
                salary_str = "Não divulgado"
                if min_amt and max_amt:
                    salary_str = f"R$ {min_amt:,.0f} - {max_amt:,.0f}"
                elif min_amt:
                    salary_str = f"R$ {min_amt:,.0f}"

                jobs.append({
                    "id": generate_job_id(title, company, site_name),
                    "title": title,
                    "company": company,
                    "location": loc,
                    "site": site_name,
                    "url": job_url,
                    "salary": salary_str,
                    "job_type": str(row.get("job_type", "Efetivo")),
                    "shift": "integral",
                    "contract_type": "clt",
                    "category": "geral",
                    "description": desc,
                    "date_posted": str(row.get("date_posted", "Recente"))
                })
    except Exception as e:
        logger.warning(f"JobSpy scraping note: {e}")
        
    return jobs

def search_all_sources(
    query: str,
    location: str = "Brasil",
    category: str = "todos",
    shift: str = "todos",
    contract: str = "todos",
    sources: Optional[List[str]] = None,
    limit: int = 30
) -> List[Dict[str, Any]]:
    """
    Unified multi-category search engine.
    Consults JobSpy (LinkedIn/Indeed), Remotive (if tech), and comprehensive Seed DB.
    """
    if sources is None:
        sources = ["jobspy"]
        
    collected: List[Dict[str, Any]] = []
    
    # 1. JobSpy for real queries across all professions (Adm, RH, Logística, TI, Vendas, etc.)
    if "jobspy" in sources and query:
        spy_jobs = fetch_jobspy_jobs(search_term=query, location=location, results_wanted=15)
        collected.extend(spy_jobs)

    # 2. Remotive only if tech / software related
    is_tech_query = any(w in query.lower() for w in ["dev", "python", "software", "programador", "backend", "frontend", "full stack", "react", "dados"])
    if "remotive" in sources and (category in ["tecnologia", "todos"] or is_tech_query):
        remotive_jobs = fetch_remotive_jobs(query, limit=10)
        collected.extend(remotive_jobs)

    # 3. Always merge matching Seed Jobs to ensure high-quality local results
    q_norm = query.lower().strip()
    words = [w for w in re.findall(r'\b\w{3,}\b', q_norm) if w not in ["para", "com", "sem", "uma", "vaga"]]
    
    for seed in SEED_JOBS:
        # Category filter check
        if category != "todos" and seed.get("category") != category:
            continue
            
        # Shift filter check
        if shift != "todos" and seed.get("shift") != shift:
            continue

        # Contract filter check
        if contract != "todos" and seed.get("contract_type") != contract:
            continue

        seed_text = f"{seed['title']} {seed['description']} {seed['category']}".lower()
        
        # Check matching
        if not words or any(w in seed_text for w in words):
            collected.append(seed)

    # Deduplicate
    seen_ids = set()
    deduped = []
    for job in collected:
        jid = job.get("id") or generate_job_id(job.get("title", ""), job.get("company", ""), job.get("site", ""))
        if jid not in seen_ids:
            seen_ids.add(jid)
            deduped.append(job)
            
    return deduped[:limit]
