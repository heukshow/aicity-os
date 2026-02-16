# Extend translations.js to include inquiry page content

inquiry_translations = '''
        inquiry: {
            title: "비즈니스 문의",
            subtitle: "Cauchemar 크루와의 협업을 제안해주세요.",
            company_name: "회사명",
            your_name: "담당자명",
            email: "이메일 주소",
            target_service: "문의 서비스",
            message: "프로젝트 설명",
            message_placeholder: "프로젝트에 대해 알려주세요...",
            send: "문의 보내기",
            services: {
                item: "3D 아이템 협업",
                live: "라이브 스트리밍",
                video: "영상 제작",
                world: "월드 제작",
                sns: "SNS 마케팅",
                brand: "브랜드 파트너십"
            }
        }'''

# Read current translations.js
with open('projects/Cauchemar/js/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add inquiry translations to each language section
# For Korean (already have the content above)
content = content.replace(
    '            brand_features: ["브랜드 매칭 및 제안서 작성", "인플루엔서 크리에이터 섭외", "이벤트 기획 및 캠페인 운영"]',
    '            brand_features: ["브랜드 매칭 및 제안서 작성", "인플루엔서 크리에이터 섭외", "이벤트 기획 및 캠페인 운영"],\n' + inquiry_translations
)

# English
en_inquiry = '''
        inquiry: {
            title: "Business Inquiry",
            subtitle: "Propose a collaboration with Cauchemar Crew.",
            company_name: "Company Name",
            your_name: "Your Name",
            email: "Email Address",
            target_service: "Target Service",
            message: "Message",
            message_placeholder: "Tell us about your project...",
            send: "Send Inquiry",
            services: {
                item: "3D Item Collaboration",
                live: "Live Streaming",
                video: "Video Production",
                world: "World Construction",
                sns: "SNS Marketing",
                brand: "Brand Partnership"
            }
        }'''

content = content.replace(
    '            brand_features: ["Brand Matching & Proposal Writing", "Influencer Creator Recruitment", "Event Planning & Campaign Management"]',
    '            brand_features: ["Brand Matching & Proposal Writing", "Influencer Creator Recruitment", "Event Planning & Campaign Management"],\n' + en_inquiry
)

# Japanese
ja_inquiry = '''
        inquiry: {
            title: "ビジネスお問い合わせ",
            subtitle: "Cauchemarクルーとのコラボレーションをご提案ください。",
            company_name: "会社名",
            your_name: "お名前",
            email: "メールアドレス",
            target_service: "対象サービス",
            message: "メッセージ",
            message_placeholder: "プロジェクトについてお聞かせください...",
            send: "お問い合わせ送信",
            services: {
                item: "3Dアイテムコラボレーション",
                live: "ライブストリーミング",
                video: "映像制作",
                world: "ワールド構築",
                sns: "SNSマーケティング",
                brand: "ブランドパートナーシップ"
            }
        }'''

content = content.replace(
    '            brand_features: ["ブランドマッチング＆提案書作成", "インフルエンサークリエイター募集", "イベント企画＆キャンペーン運営"]',
    '            brand_features: ["ブランドマッチング＆提案書作成", "インフルエンサークリエイター募集", "イベント企画＆キャンペーン運営"],\n' + ja_inquiry
)

# Add similar for other languages (ZH, ES, FR)
zh_inquiry = '''
        inquiry: {
            title: "业务咨询",
            subtitle: "向Cauchemar团队提出合作建议。",
            company_name: "公司名称",
            your_name: "您的姓名",
            email: "电子邮件地址",
            target_service: "目标服务",
            message: "消息",
            message_placeholder: "告诉我们您的项目...",
            send: "发送咨询",
            services: {
                item: "3D物品合作",
                live: "直播",
                video: "视频制作",
                world: "世界构建",
                sns: "SNS营销",
                brand: "品牌合作"
            }
        }'''

content = content.replace(
    '            brand_features: ["品牌配对与提案撰写", "网红创作者招募", "活动策划与营销活动管理"]',
    '            brand_features: ["品牌配对与提案撰写", "网红创作者招募", "活动策划与营销活动管理"],\n' + zh_inquiry
)

es_inquiry = '''
        inquiry: {
            title: "Consulta Comercial",
            subtitle: "Proponga una colaboración con Cauchemar Crew.",
            company_name: "Nombre de la Empresa",
            your_name: "Su Nombre",
            email: "Dirección de Email",
            target_service: "Servicio Objetivo",
            message: "Mensaje",
            message_placeholder: "Cuéntenos sobre su proyecto...",
            send: "Enviar Consulta",
            services: {
                item: "Colaboración de Artículos 3D",
                live: "Transmisión en Vivo",
                video: "Producción de Video",
                world: "Construcción de Mundos",
                sns: "Marketing SNS",
                brand: "Asociación de Marca"
            }
        }'''

content = content.replace(
    '            brand_features: ["Emparejamiento de Marcas y Redacción de Propuestas", "Reclutamiento de Creadores Influencers", "Planificación de Eventos y Gestión de Campañas"]',
    '            brand_features: ["Emparejamiento de Marcas y Redacción de Propuestas", "Reclutamiento de Creadores Influencers", "Planificación de Eventos y Gestión de Campañas"],\n' + es_inquiry
)

fr_inquiry = '''
        inquiry: {
            title: "Demande Commerciale",
            subtitle: "Proposez une collaboration avec Cauchemar Crew.",
            company_name: "Nom de l'Entreprise",
            your_name: "Votre Nom",
            email: "Adresse Email",
            target_service: "Service Ciblé",
            message: "Message",
            message_placeholder: "Parlez-nous de votre projet...",
            send: "Envoyer la Demande",
            services: {
                item: "Collaboration d'Articles 3D",
                live: "Diffusion en Direct",
                video: "Production Vidéo",
                world: "Construction de Monde",
                sns: "Marketing SNS",
                brand: "Partenariat de Marque"
            }
        }'''

content = content.replace(
    '            brand_features: ["Appariement de Marques et Rédaction de Propositions", "Recrutement de Créateurs Influenceurs", "Planification d\'Événements et Gestion de Campagnes"]',
    '            brand_features: ["Appariement de Marques et Rédaction de Propositions", "Recrutement de Créateurs Influenceurs", "Planification d\'Événements et Gestion de Campagnes"],\n' + fr_inquiry
)

with open('projects/Cauchemar/js/translations.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Extended translations.js with inquiry page content")
