# Fix translations.js - All languages got replaced with Korean, need to restore proper translations

translations_by_lang = {
    'en': {
        'title': 'Business Inquiry',
        'subtitle': 'Propose a collaboration with Cauchemar Crew.',
        'section_client': 'Client Information',
        'name': 'Name *',
        'email': 'Email *',
        'company': 'Company Name',
        'phone': 'Phone',
        'section_project': 'Project Information',
        'project_title': 'Project Title *',
        'budget': 'Budget Range',
        'start_date': 'Preferred Start Date',
        'description': 'Project Description *',
        'description_placeholder': 'Tell us about your project in detail...',
        'submit': 'Submit Inquiry'
    },
    'ja': {
        'title': 'ビジネスお問い合わせ',
        'subtitle': 'Cauchemarクルーとのコラボレーションをご提案ください。',
        'section_client': 'クライアント情報',
        'name': '名前 *',
        'email': 'メールアドレス *',
        'company': '会社名',
        'phone': '電話番号',
        'section_project': 'プロジェクト情報',
        'project_title': 'プロジェクトタイトル *',
        'budget': '予算範囲',
        'start_date': '希望開始日',
        'description': 'プロジェクト詳細 *',
        'description_placeholder': 'プロジェクトについて詳しくお聞かせください...',
        'submit': 'お問い合わせ送信'
    },
    'zh': {
        'title': '业务咨询',
        'subtitle': '向Cauchemar团队提出合作建议。',
        'section_client': '客户信息',
        'name': '姓名 *',
        'email': '电子邮件 *',
        'company': '公司名称',
        'phone': '电话',
        'section_project': '项目信息',
        'project_title': '项目标题 *',
        'budget': '预算范围',
        'start_date': '首选开始日期',
        'description': '项目描述 *',
        'description_placeholder': '详细告诉我们您的项目...',
        'submit': '提交咨询'
    },
    'es': {
        'title': 'Consulta Comercial',
        'subtitle': 'Proponga una colaboración con Cauchemar Crew.',
        'section_client': 'Información del Cliente',
        'name': 'Nombre *',
        'email': 'Email *',
        'company': 'Nombre de la Empresa',
        'phone': 'Teléfono',
        'section_project': 'Información del Proyecto',
        'project_title': 'Título del Proyecto *',
        'budget': 'Rango de Presupuesto',
        'start_date': 'Fecha de Inicio Preferida',
        'description': 'Descripción del Proyecto *',
        'description_placeholder': 'Cuéntenos sobre su proyecto en detalle...',
        'submit': 'Enviar Consulta'
    },
    'fr': {
        'title': 'Demande Commerciale',
        'subtitle': 'Proposez une collaboration avec Cauchemar Crew.',
        'section_client': 'Informations Client',
        'name': 'Nom *',
        'email': 'Email *',
        'company': "Nom de l'Entreprise",
        'phone': 'Téléphone',
        'section_project': 'Informations sur le Projet',
        'project_title': 'Titre du Projet *',
        'budget': 'Fourchette Budgétaire',
        'start_date': 'Date de Début Souhaitée',
        'description': 'Description du Projet *',
        'description_placeholder': 'Parlez-nous de votre projet en détail...',
        'submit': 'Envoyer la Demande'
    }
}

with open('projects/Cauchemar/js/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace each language's inquiry section with proper translations
for lang, trans in translations_by_lang.items():
    # Find the language section
    old_pattern = f'''                inquiry: {{
            title: "비즈니스 문의",
            subtitle: "Cauchemar 크루와의 협업을 제안해주세요.",
            section_client: "클라이언트 정보",
            name: "이름 *",
            email: "이메일 *",
            company: "회사명",
            phone: "연락처",
            section_project: "프로젝트 정보",
            project_title: "프로젝트 제목 *",
            budget: "예산 범위",
            start_date: "프로젝트 시작 희망일",
            description: "프로젝트 상세 설명 *",
            description_placeholder: "프로젝트에 대해 자세히 알려주세요...",
            submit: "문의 제출"
        }}'''
    
    new_pattern = f'''        inquiry: {{
            title: "{trans['title']}",
            subtitle: "{trans['subtitle']}",
            section_client: "{trans['section_client']}",
            name: "{trans['name']}",
            email: "{trans['email']}",
            company: "{trans['company']}",
            phone: "{trans['phone']}",
            section_project: "{trans['section_project']}",
            project_title: "{trans['project_title']}",
            budget: "{trans['budget']}",
            start_date: "{trans['start_date']}",
            description: "{trans['description']}",
            description_placeholder: "{trans['description_placeholder']}",
            submit: "{trans['submit']}"
        }}'''
    
    # Replace only the first occurrence after finding the language
    content = content.replace(old_pattern, new_pattern, 1)

with open('projects/Cauchemar/js/translations.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all language translations in translations.js!")
